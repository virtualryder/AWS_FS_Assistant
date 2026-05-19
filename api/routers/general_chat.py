"""
General-purpose Claude chat endpoint.

Route:
  POST /api/general-chat

A simple direct chat with Claude — no dual agents, no tools, no customer
context. Used for ad-hoc questions from the sidebar "Chat with Claude" panel.

SSE events:
  {"type": "token",  "text": "..."}   — streamed response tokens
  {"type": "done",   "text": "..."}   — full response; signals end of stream
  {"type": "error",  "text": "..."}   — error; signals end of stream
"""

import json
import logging
import sys
from pathlib import Path

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import ANTHROPIC_API_KEY, MODEL_NAME

logger = logging.getLogger(__name__)
router = APIRouter(tags=["general-chat"])

# Use the async client so streaming doesn't block the event loop
_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """\
You are Claude, an AI assistant made by Anthropic. Answer the user's questions \
clearly, concisely, and helpfully. You have broad general knowledge — technology, \
business, finance, coding, strategy, and beyond. Format responses with markdown \
when it improves readability (headers, bullets, code blocks). Be direct and thorough.\
"""


class GeneralChatRequest(BaseModel):
    messages: list[dict]  # [{"role": "user"|"assistant", "content": "..."}]


@router.post("/general-chat")
async def general_chat(body: GeneralChatRequest):
    if not body.messages:
        raise HTTPException(status_code=422, detail="messages must not be empty")

    async def event_generator():
        full_response = ""
        try:
            async with _client.messages.stream(
                model=MODEL_NAME,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=body.messages,
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield {"data": json.dumps({"type": "token", "text": text})}

            yield {"data": json.dumps({"type": "done", "text": full_response})}

        except Exception as exc:
            logger.exception("General chat error")
            yield {"data": json.dumps({"type": "error", "text": str(exc)})}

    return EventSourceResponse(event_generator(), ping=20)
