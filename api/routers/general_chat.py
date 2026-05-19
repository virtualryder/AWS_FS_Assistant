"""
General-purpose Claude chat endpoint with optional Tavily web search.

Route:
  POST /api/general-chat

A direct chat with Claude that can autonomously search the web when needed.
Claude decides when to call the search_web tool — the tool-use loop runs
until Claude produces a final text response.

SSE events:
  {"type": "status",    "text": "..."}   — search activity / status updates
  {"type": "token",     "text": "..."}   — streamed response tokens
  {"type": "done",      "text": "..."}   — full response; signals end of stream
  {"type": "heartbeat", "text": ""}      — keep-alive (browser ignores)
  {"type": "error",     "text": "..."}   — error; signals end of stream
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import ANTHROPIC_API_KEY, MODEL_NAME, TAVILY_API_KEY

logger = logging.getLogger(__name__)
router = APIRouter(tags=["general-chat"])

_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """\
You are Claude, a highly capable AI assistant made by Anthropic. You can answer any \
question — technology, business, finance, law, science, coding, strategy, creative work, \
and beyond. You have access to a web search tool; use it whenever:
  • The question requires current information (news, prices, events after your training)
  • The user asks about a specific company, product, or person where fresh data helps
  • You're uncertain and a quick search would improve your answer
  • The user explicitly asks you to search

When you search, always tell the user what you're searching for before you do it. \
After receiving search results, synthesise them into a clear, direct answer — do not \
just dump the raw results. Cite sources inline as markdown links where relevant.

For questions fully within your training knowledge, answer directly without searching. \
Format with markdown (headers, bullets, code blocks) when it improves readability. \
Be direct, thorough, and opinionated where appropriate.\
"""

# Tool schema for web search
SEARCH_WEB_TOOL = {
    "name": "search_web",
    "description": (
        "Search the public internet for current information. "
        "Use for: recent news, current events, company research, product details, "
        "pricing, documentation, anything that may have changed since training cutoff, "
        "or any topic where live data improves the answer."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A targeted search query. Be specific.",
            },
            "max_results": {
                "type": "integer",
                "description": "Number of results to return (default 5, max 10).",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}


def _run_web_search(query: str, max_results: int = 5) -> str:
    """Execute a Tavily web search and return formatted results."""
    if not TAVILY_API_KEY:
        return (
            "Web search is not available — TAVILY_API_KEY is not configured. "
            "The Railway API service needs TAVILY_API_KEY set in its environment variables."
        )

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query,
            search_depth="advanced",
            max_results=min(max_results, 10),
        )
    except Exception as exc:
        logger.error("Tavily search failed: %s", exc)
        return f"Web search failed: {exc}"

    results = response.get("results", [])
    if not results:
        return f"No web results found for: {query}"

    lines = [f"Web search results for: \"{query}\"\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r.get('title', 'No title')}")
        lines.append(f"    URL: {r.get('url', '')}")
        content = r.get("content", "")
        if len(content) > 1500:
            content = content[:1500] + " [...]"
        lines.append(f"    {content}")
        lines.append("")
    return "\n".join(lines)


class GeneralChatRequest(BaseModel):
    messages: list[dict]  # [{"role": "user"|"assistant", "content": "..."}]


@router.post("/general-chat")
async def general_chat(body: GeneralChatRequest):
    if not body.messages:
        raise HTTPException(status_code=422, detail="messages must not be empty")

    queue: asyncio.Queue = asyncio.Queue()

    async def event_generator():
        total_wait = 0
        max_wait = 120  # 2-minute cap for general chat

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=4.0)
            except asyncio.TimeoutError:
                total_wait += 4
                if total_wait >= max_wait:
                    yield {"data": json.dumps({"type": "error", "text": "Request timed out"})}
                    return
                yield {"data": json.dumps({"type": "heartbeat", "text": ""})}
                continue

            if item is None:
                # Sentinel — agent task is done
                return

            yield {"data": json.dumps(item)}

            if item["type"] in ("done", "error"):
                return

    # Run the tool-use loop in a background task so we can stream heartbeats
    asyncio.create_task(_run_agent(body.messages, queue))

    return EventSourceResponse(event_generator(), ping=15)


async def _run_agent(messages: list[dict], queue: asyncio.Queue) -> None:
    """
    Async tool-use loop:
      1. Call Claude with tool definitions
      2. If Claude uses search_web, run it and feed results back
      3. When Claude produces a final text response, stream it token by token
    """
    full_response = ""
    current_messages = list(messages)
    MAX_TOOL_ROUNDS = 5  # safety cap

    try:
        for _round in range(MAX_TOOL_ROUNDS):
            # Does this round produce a final answer or a tool call?
            # Use non-streaming first to check for tool use
            response = await _client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=[SEARCH_WEB_TOOL],
                messages=current_messages,
            )

            # ── Tool use round ────────────────────────────────────────────────
            if response.stop_reason == "tool_use":
                # Add Claude's tool-call turn to history
                current_messages.append({
                    "role": "assistant",
                    "content": response.content,
                })

                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue

                    tool_name = block.name
                    tool_input = block.input

                    if tool_name == "search_web":
                        query = tool_input.get("query", "")
                        max_results = int(tool_input.get("max_results", 5))
                        await queue.put({
                            "type": "status",
                            "text": f"🔍 Searching: {query}",
                        })
                        # Run blocking Tavily call in thread pool
                        result = await asyncio.get_event_loop().run_in_executor(
                            None, _run_web_search, query, max_results
                        )
                        await queue.put({
                            "type": "status",
                            "text": f"✓ Got {result.count('[') } results — synthesising…",
                        })
                    else:
                        result = f"Unknown tool: {tool_name}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

                current_messages.append({
                    "role": "user",
                    "content": tool_results,
                })
                continue  # go back for Claude's next response

            # ── Final text response — stream it ───────────────────────────────
            await queue.put({"type": "status", "text": "📝 Streaming response…"})

            async with _client.messages.stream(
                model=MODEL_NAME,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=[SEARCH_WEB_TOOL],
                tool_choice={"type": "none"},  # no more tool calls in final pass
                messages=current_messages,
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    await queue.put({"type": "token", "text": text})

            await queue.put({"type": "done", "text": full_response})
            return

        # Exhausted tool rounds — ask Claude for a plain final answer
        current_messages.append({
            "role": "user",
            "content": "Please provide your final answer now.",
        })
        async with _client.messages.stream(
            model=MODEL_NAME,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=current_messages,
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                await queue.put({"type": "token", "text": text})

        await queue.put({"type": "done", "text": full_response})

    except Exception as exc:
        logger.exception("General chat agent error")
        await queue.put({"type": "error", "text": str(exc)})
    finally:
        await queue.put(None)  # signal event_generator to exit
