"""
Project CRUD endpoints + project-scoped conversations and documents.

Routes:
  GET    /api/customers/{customer_id}/projects              — list projects
  POST   /api/customers/{customer_id}/projects              — create project
  GET    /api/projects/{project_id}                         — get project
  PUT    /api/projects/{project_id}                         — update project
  DELETE /api/projects/{project_id}                         — delete project
  GET    /api/projects/{project_id}/conversations           — list conversations
  POST   /api/projects/{project_id}/conversations           — create conversation
  GET    /api/projects/{project_id}/documents               — list documents
  POST   /api/projects/{project_id}/documents               — upload document
"""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db
from api.auth import get_current_user_id
from ingestion.document_parser import extract_text

logger = logging.getLogger(__name__)

router = APIRouter(tags=["projects"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str
    description: str = ""


# ── Customer → Projects ───────────────────────────────────────────────────────

def _owned_project(project_id: str, user_id: str) -> dict:
    """Return project or 404 if not found / belongs to another user's customer."""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.get_customer(project["customer_id"], user_id=user_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/customers/{customer_id}/projects")
async def list_projects(customer_id: str, user_id: str = Depends(get_current_user_id)):
    if not db.get_customer(customer_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    rows = db.get_projects(customer_id)
    return [_serialize(r) for r in rows]


@router.post("/customers/{customer_id}/projects", status_code=201)
async def create_project(customer_id: str, body: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    if not db.get_customer(customer_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="Customer not found")
    if not body.name.strip():
        raise HTTPException(status_code=422, detail="Project name is required")
    project_id = db.create_project(customer_id, body.name, body.description)
    project = db.get_project(project_id)
    return _serialize(project)


# ── Project CRUD ──────────────────────────────────────────────────────────────

@router.get("/projects/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user_id)):
    return _serialize(_owned_project(project_id, user_id))


@router.put("/projects/{project_id}")
async def update_project(project_id: str, body: ProjectUpdate, user_id: str = Depends(get_current_user_id)):
    _owned_project(project_id, user_id)
    if not body.name.strip():
        raise HTTPException(status_code=422, detail="Project name is required")
    db.update_project(project_id, body.name, body.description)
    return _serialize(db.get_project(project_id))


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_project(project_id, user_id)
    db.delete_project(project_id)


# ── Project → Conversations ───────────────────────────────────────────────────

@router.get("/projects/{project_id}/conversations")
async def list_project_conversations(project_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_project(project_id, user_id)
    rows = db.get_project_conversations(project_id)
    return [_serialize(r) for r in rows]


@router.post("/projects/{project_id}/conversations", status_code=201)
async def create_project_conversation(project_id: str, user_id: str = Depends(get_current_user_id)):
    project = _owned_project(project_id, user_id)
    conv_id = db.create_project_conversation(project_id, project["customer_id"])
    conv = db.get_conversation(conv_id)
    return _serialize(conv)


# ── Project → Documents ───────────────────────────────────────────────────────

@router.get("/projects/{project_id}/documents")
async def list_project_documents(project_id: str, user_id: str = Depends(get_current_user_id)):
    _owned_project(project_id, user_id)
    docs = db.get_project_documents(project_id)
    return [_serialize_doc(d) for d in docs]


@router.post("/projects/{project_id}/documents", status_code=201)
async def upload_project_document(
    project_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    project = _owned_project(project_id, user_id)

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

    doc_id = db.save_project_document(
        project_id, project["customer_id"], file.filename or "upload", text
    )
    docs = db.get_project_documents(project_id)
    doc = next((d for d in docs if d["id"] == doc_id), None)
    return _serialize_doc(doc) if doc else {"id": doc_id}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize(obj: dict) -> dict:
    out = {}
    for k, v in obj.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def _serialize_doc(obj: dict) -> dict:
    out = {}
    for k, v in obj.items():
        if k == "extracted_text":
            out["char_count"] = obj.get("char_count", len(v or ""))
        elif hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
