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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from api.auth import get_current_user_id
from api.session_store import store as session_store

router = APIRouter(tags=["conversations"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ConversationTitleUpdate(BaseModel):
    title: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _owned_customer(customer_id: str, user_id: str) -> dict:
    """Return customer or raise 404 if not found / not owned by this user."""
    customer = db.get_customer(customer_id, user_id=user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def _owned_conv(conv_id: str, user_id: str) -> dict:
    """Return conversation or raise 404 if not found / belongs to another user's customer."""
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Verify the customer belongs to this user
    if not db.get_customer(conv["customer_id"], user_id=user_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/customers/{customer_id}/conversations")
async def list_conversations(customer_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_customer(customer_id, user_id)
    rows = db.get_conversations(customer_id)
    return [_serialize(r) for r in rows]


@router.post("/customers/{customer_id}/conversations", status_code=201)
async def create_conversation(customer_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_customer(customer_id, user_id)
    conv_id = db.create_conversation(customer_id)
    conv = db.get_conversation(conv_id)
    return _serialize(conv)


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str, user_id: str = Depends(get_current_user_id)):
    return _serialize(_owned_conv(conv_id, user_id))


@router.put("/conversations/{conv_id}/title")
async def update_title(conv_id: str, body: ConversationTitleUpdate, user_id: str = Depends(get_current_user_id)):
    _owned_conv(conv_id, user_id)
    title = body.title.strip()[:58] or "New Conversation"
    db.update_conversation_title(conv_id, title)
    return _serialize(db.get_conversation(conv_id))


@router.delete("/conversations/{conv_id}", status_code=204)
async def delete_conversation(conv_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_conv(conv_id, user_id)
    db.delete_conversation(conv_id)
    session_store.evict(conv_id)


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_conv(conv_id, user_id)
    rows = db.get_messages(conv_id)
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
async def clear_messages(conv_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_conv(conv_id, user_id)
    db.clear_conversation_messages(conv_id)
    session_store.evict(conv_id)


# ── Serialiser ────────────────────────────────────────────────────────────────

def _serialize(obj: dict) -> dict:
    out = {}
    for k, v in obj.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
