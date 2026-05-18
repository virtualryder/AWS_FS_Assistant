"""
Chat SSE endpoint.

Route:
  POST /api/conversations/{conv_id}/chat

Accepts a JSON body with the user's message and optional customer context.
Returns a Server-Sent Events stream of:

  {"type": "status", "text": "..."}      — agent status updates (Phase 1, Phase 2, etc.)
  {"type": "token",  "text": "..."}      — streamed response tokens (synthesis phase)
  {"type": "done",   "text": "..."}      — full response text; also signals end of stream
  {"type": "error",  "text": "..."}      — error message; also signals end of stream

After the stream ends the response is persisted to the database and the
conversation title is auto-generated from the first user message.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from api.session_store import store as session_store
from api.streaming import build_agent_runner, get_executor, make_callbacks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


# ── Schema ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_message: str
    customer_context: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_title(prompt: str) -> str:
    clean = prompt.strip().replace("\n", " ")
    if len(clean) <= 58:
        return clean
    cut = clean[:58].rfind(" ")
    return clean[:cut if cut > 20 else 58] + "…"


def _save_exchange(conv_id: str, user_prompt: str, assistant_response: str) -> None:
    next_idx = db.get_next_turn_index(conv_id)
    db.save_messages_batch([
        {
            "conversation_id": conv_id,
            "turn_index":      next_idx,
            "role":            "user",
            "message_type":    "text",
            "content_text":    user_prompt,
            "content_json":    None,
            "display_content": user_prompt,
            "is_display_turn": True,
        },
        {
            "conversation_id": conv_id,
            "turn_index":      next_idx + 1,
            "role":            "assistant",
            "message_type":    "text",
            "content_text":    assistant_response,
            "content_json":    None,
            "display_content": assistant_response,
            "is_display_turn": True,
        },
    ])
    db.bump_conversation(conv_id)


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/conversations/{conv_id}/chat")
async def chat(conv_id: str, body: ChatRequest):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_message = body.user_message.strip()
    if not user_message:
        raise HTTPException(status_code=422, detail="user_message must not be empty")

    # Load or create agent session, hydrating history from DB if needed
    db_msgs = db.get_messages(conv_id)
    agent = session_store.get_or_create(conv_id, db_messages=db_msgs)

    # On the first message of a new conversation, enrich customer_context with
    # summaries of the customer's prior conversations so the agent has memory
    # across sessions.
    is_first_message = (len(db_msgs) == 0)
    customer_context = body.customer_context
    if is_first_message and conv.get("customer_id"):
        prior = db.get_prior_conversation_summaries(
            customer_id=conv["customer_id"],
            exclude_conv_id=conv_id,
            limit=5,
        )
        if prior:
            lines = ["## Prior Conversations with This Customer\n"]
            for s in prior:
                lines.append(f"**{s['title']}**")
                if s["first_user"]:
                    lines.append(f"- Asked: {s['first_user']}")
                if s["last_asst"]:
                    lines.append(f"- Summary: {s['last_asst'][:400]}")
                lines.append("")
            prior_block = "\n".join(lines)
            customer_context = (
                prior_block + "\n\n" + customer_context
                if customer_context.strip()
                else prior_block
            )

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    runner = build_agent_runner(
        agent=agent,
        user_message=user_message,
        customer_context=customer_context,
        queue=queue,
        loop=loop,
    )

    async def event_generator():
        get_executor().submit(runner)

        full_response = ""

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=300.0)
            except asyncio.TimeoutError:
                yield {
                    "data": json.dumps({"type": "error", "text": "Request timed out after 5 minutes"})
                }
                return

            yield {"data": json.dumps(item)}

            if item["type"] == "done":
                full_response = item["text"]
                break
            if item["type"] == "error":
                logger.error("Chat error for conv %s: %s", conv_id, item["text"])
                return

        # Persist after streaming is complete
        try:
            _save_exchange(conv_id, user_message, full_response)
        except Exception:
            logger.exception("Failed to persist exchange for conv %s", conv_id)

        # Auto-title on first message
        if is_first_message and conv.get("title") == "New Conversation":
            try:
                db.update_conversation_title(conv_id, _make_title(user_message))
            except Exception:
                logger.exception("Failed to auto-title conv %s", conv_id)

    return EventSourceResponse(event_generator())
