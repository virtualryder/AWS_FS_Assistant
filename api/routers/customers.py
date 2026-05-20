"""
Customer CRUD endpoints.

Routes:
  GET    /api/customers                  — list all customers
  POST   /api/customers                  — create a customer
  GET    /api/customers/{customer_id}    — get a single customer
  PUT    /api/customers/{customer_id}    — update a customer
  DELETE /api/customers/{customer_id}   — delete a customer (cascade-deletes conversations)
"""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from api.auth import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["customers"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    name: str
    industry: str = ""
    arch_context: str = ""
    stage: str = "Prospect"


class CustomerUpdate(BaseModel):
    name: str
    industry: str = ""
    arch_context: str = ""
    stage: str = "Prospect"


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/customers")
async def list_customers(user_id: str = Depends(get_current_user_id)):
    """List all customers for the authenticated user."""
    rows = db.get_customers(user_id=user_id)
    return [_serialize(r) for r in rows]


@router.post("/customers", status_code=201)
async def create_customer(body: CustomerCreate, user_id: str = Depends(get_current_user_id)):
    try:
        customer_id = db.create_customer(
            name=body.name,
            industry=body.industry,
            arch_context=body.arch_context,
            stage=body.stage,
            user_id=user_id,
        )
        customer = db.get_customer(customer_id)
        return _serialize(customer)
    except Exception as exc:
        logger.exception("Failed to create customer")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str, user_id: str = Depends(get_current_user_id)):
    customer = db.get_customer(customer_id, user_id=user_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _serialize(customer)


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, body: CustomerUpdate, user_id: str = Depends(get_current_user_id)):
    if not db.get_customer(customer_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    db.update_customer(
        customer_id=customer_id,
        name=body.name,
        industry=body.industry,
        arch_context=body.arch_context,
        stage=body.stage,
    )
    return _serialize(db.get_customer(customer_id))


@router.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: str, user_id: str = Depends(get_current_user_id)):
    if not db.get_customer(customer_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete_customer(customer_id)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize(obj: dict) -> dict:
    """Convert datetime values to ISO strings."""
    out = {}
    for k, v in obj.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
