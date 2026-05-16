"""
Discovery Brief SSE endpoint.

Route:
  POST /api/customers/{customer_id}/discovery

Generates a financial services discovery brief for a customer via the
DiscoveryAgent. Streams status updates and the final brief text via SSE.
Optionally saves the brief as a conversation in the customer's workspace.

SSE event types (same shape as chat.py):
  {"type": "status", "text": "..."}  — live progress messages
  {"type": "token",  "text": "..."}  — streamed text tokens
  {"type": "done",   "text": "..."}  — full brief markdown
  {"type": "error",  "text": "..."}  — error details
"""

import asyncio
import json
import logging
import sys
from datetime import date
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from api.streaming import build_discovery_runner, get_executor

logger = logging.getLogger(__name__)

router = APIRouter(tags=["discovery"])


# ── Schema ────────────────────────────────────────────────────────────────────

class DiscoveryRequest(BaseModel):
    website: str = ""
    notes: str = ""
    save_as_conversation: bool = True


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/customers/{customer_id}/discovery")
async def generate_discovery_brief(customer_id: str, body: DiscoveryRequest):
    customer = db.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    from agent.discovery_agent import DiscoveryAgent
    discovery_agent = DiscoveryAgent()

    arch_context = (customer.get("arch_context") or "").strip()
    industry = (customer.get("industry") or "").strip()

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    runner = build_discovery_runner(
        agent=discovery_agent,
        customer_name=customer["name"],
        industry=industry,
        website=body.website,
        notes=body.notes,
        arch_context=arch_context,
        queue=queue,
        loop=loop,
    )

    async def event_generator():
        get_executor().submit(runner)
        brief_text = ""

        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=300.0)
            except asyncio.TimeoutError:
                yield {
                    "data": json.dumps({"type": "error", "text": "Discovery brief timed out"})
                }
                return

            yield {"data": json.dumps(item)}

            if item["type"] == "done":
                brief_text = item["text"]
                break
            if item["type"] == "error":
                logger.error("Discovery error for %s: %s", customer_id, item["text"])
                return

        # Optionally persist the brief as a conversation
        if body.save_as_conversation and brief_text:
            try:
                _save_brief_as_conversation(
                    customer_id=customer_id,
                    customer_name=customer["name"],
                    website=body.website,
                    notes=body.notes,
                    brief_text=brief_text,
                )
            except Exception:
                logger.exception("Failed to save discovery brief as conversation")

    return EventSourceResponse(event_generator())


# ── Helpers ───────────────────────────────────────────────────────────────────

def _save_brief_as_conversation(
    customer_id: str,
    customer_name: str,
    website: str,
    notes: str,
    brief_text: str,
) -> str:
    title = f"Discovery Brief — {date.today().strftime('%b %d, %Y')}"
    conv_id = db.create_conversation(customer_id)
    db.update_conversation_title(conv_id, title[:58])

    parts = [f"Generate a Financial Services discovery brief for {customer_name}."]
    if website:
        parts.append(f"Website: {website}")
    if notes:
        parts.append(f"Notes: {notes}")
    user_msg = "\n".join(parts)

    next_idx = db.get_next_turn_index(conv_id)
    db.save_messages_batch([
        {
            "conversation_id": conv_id,
            "turn_index":      next_idx,
            "role":            "user",
            "message_type":    "text",
            "content_text":    user_msg,
            "content_json":    None,
            "display_content": user_msg,
            "is_display_turn": True,
        },
        {
            "conversation_id": conv_id,
            "turn_index":      next_idx + 1,
            "role":            "assistant",
            "message_type":    "text",
            "content_text":    brief_text,
            "content_json":    None,
            "display_content": brief_text,
            "is_display_turn": True,
        },
    ])
    db.bump_conversation(conv_id)
    return conv_id
