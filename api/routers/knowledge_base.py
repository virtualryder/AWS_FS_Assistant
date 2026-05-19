"""
Knowledge base status and ingestion trigger endpoints.

Routes:
  GET  /api/knowledge-base/status   — chunk count + manifest metadata
  POST /api/knowledge-base/ingest   — trigger a documentation ingest run
"""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])

_ingest_running = False


@router.get("/status")
async def get_status():
    """Return the current knowledge base chunk count and ingestion manifest."""
    try:
        count = db.get_chunk_count()
        manifest = db.get_manifest()
        return {
            "chunk_count": count,
            "last_updated": manifest.get("last_updated"),
            "total_chunks": manifest.get("total_chunks", count),
            "sources": manifest.get("sources", {}),
            "ingest_running": _ingest_running,
        }
    except Exception as exc:
        logger.exception("Failed to get knowledge base status")
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/sources")
async def get_sources():
    """Return grouped list of indexed AWS documentation sources with chunk counts."""
    try:
        return {"sources": db.get_indexed_sources()}
    except Exception as exc:
        logger.exception("Failed to get knowledge base sources")
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/ingest", status_code=202)
async def trigger_ingest(background_tasks: BackgroundTasks):
    """
    Trigger an AWS documentation ingest run in the background.
    Returns immediately with 202 Accepted; poll /status for completion.
    """
    global _ingest_running
    if _ingest_running:
        raise HTTPException(status_code=409, detail="An ingest run is already in progress")

    background_tasks.add_task(_run_ingest)
    return {"status": "started", "message": "Ingest run started in background"}


def _run_ingest():
    global _ingest_running
    _ingest_running = True
    try:
        from scraper.aws_doc_urls import PRIMARY_SEED_KEYS
        from ingestion.ingest_pipeline import run_ingestion
        run_ingestion(seed_keys=PRIMARY_SEED_KEYS, max_pages_per_seed=20, save_to_disk=False)
    except Exception:
        logger.exception("Ingest run failed")
    finally:
        _ingest_running = False
