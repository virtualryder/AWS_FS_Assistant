"""
Conversation CRUD endpoints.

Routes:
  GET    /api/customers/{customer_id}/conversations          — list conversations
  POST   /api/customers/{customer_id}/conversations          — create conversation
  GET    /api/conversations/{conv_id}                        — get conversation
  PUT    /api/conversations/{conv_id}/title                  — rename conversation
  DELETE /api/conversations/{conv_id}                        — delete conversation
  GET    /api/conversations/{conv_id}/messages               — get messages (display turns)
  DELETE /api/conversations/{conv_id}/messages               — clear messages
"""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from api.session_store import store as session_store

router = APIRouter(tags=["conversations"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ConversationTitleUpdate(BaseModel):
    title: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/customers/{customer_id}/conversations")
async def list_conversations(customer_id: str):
    if not db.get_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    rows = db.get_conversations(customer_id)
    return [_serialize(r) for r in rows]


@router.post("/customers/{customer_id}/conversations", status_code=201)
async def create_conversation(customer_id: str):
    if not db.get_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    conv_id = db.create_conversation(customer_id)
    conv = db.get_conversation(conv_id)
    return _serialize(conv)


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _serialize(conv)


@router.put("/conversations/{conv_id}/title")
async def update_title(conv_id: str, body: ConversationTitleUpdate):
    if not db.get_conversation(conv_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    title = body.title.strip()[:58] or "New Conversation"
    db.update_conversation_title(conv_id, title)
    return _serialize(db.get_conversation(conv_id))


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(conv_id: str):
    if not db.get_conversation(conv_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete_conversation(conv_id)
    session_store.evict(conv_id)


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str):
    if not db.get_conversation(conv_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    rows = db.get_messages(conv_id)
    # Return only display turns for the frontend
    return [
        {
            "role": m["role"],
            "content": m["display_content"],
            "turn_index": m["turn_index"],
        }
        for m in rows
        if m["is_display_turn"]
    ]


@router.delete("/conversations/{conv_id}/messages", status_code=204)
async def clear_messages(conv_id: str):
    if not db.get_conversation(conv_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.clear_conversation_messages(conv_id)
    # Evict in-memory session so the agent starts fresh
    session_store.evict(conv_id)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize(obj: dict) -> dict:
    out = {}
    for k, v in obj.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
