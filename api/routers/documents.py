"""
Customer document endpoints.

Routes:
  GET    /api/customers/{customer_id}/documents        — list documents
  POST   /api/customers/{customer_id}/documents        — upload & extract document
  PATCH  /api/documents/{doc_id}                       — toggle active state
  DELETE /api/documents/{doc_id}                       — delete document
"""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from ingestion.document_parser import extract_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ── Schemas ───────────────────────────────────────────────────────────────────

class DocumentToggle(BaseModel):
    is_active: bool


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/customers/{customer_id}/documents")
async def list_documents(customer_id: str):
    if not db.get_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    docs = db.get_customer_documents(customer_id)
    return [_serialize(d) for d in docs]


@router.post("/customers/{customer_id}/documents", status_code=201)
async def upload_document(
    customer_id: str,
    file: UploadFile = File(...),
):
    if not db.get_customer(customer_id):
        raise HTTPException(status_code=404, detail="Customer not found")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    try:
        text = extract_text(content, file.filename or "")
    except Exception as exc:
        logger.exception("Text extraction failed for %s", file.filename)
        raise HTTPException(status_code=422, detail=f"Could not extract text: {exc}") from exc

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in file")

    doc_id = db.save_customer_document(customer_id, file.filename or "upload", text)
    docs = db.get_customer_documents(customer_id)
    doc = next((d for d in docs if d["id"] == doc_id), None)
    return _serialize(doc) if doc else {"id": doc_id}


@router.patch("/documents/{doc_id}")
async def toggle_document(doc_id: str, body: DocumentToggle):
    db.toggle_customer_document(doc_id, body.is_active)
    return {"id": doc_id, "is_active": body.is_active}


@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(doc_id: str):
    db.delete_customer_document(doc_id)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize(obj: dict) -> dict:
    out = {}
    for k, v in obj.items():
        if k == "extracted_text":
            out["char_count"] = obj.get("char_count", len(v or ""))
            # Don't return extracted_text in listings (large payload)
        elif hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
