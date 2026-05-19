"""
Knowledge base status and ingestion trigger endpoints.

Routes:
  GET  /api/knowledge-base/status   — chunk count + per-seed manifest data
  POST /api/knowledge-base/ingest   — trigger a documentation ingest run
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import vectorstore.pg_client as db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])

_ingest_running = False
_ingest_progress: dict[str, Any] = {
    "current_service": None,
    "services_done": 0,
    "services_total": 0,
    "started_at": None,
}


def _progress_callback(message: str, current: int, total: int) -> None:
    global _ingest_progress
    _ingest_progress["current_service"] = message
    _ingest_progress["services_done"] = current
    _ingest_progress["services_total"] = total


def _build_all_seeds(manifest_sources: dict) -> list[dict]:
    """
    Return a list of all PRIMARY_SEED_KEYS with their manifest data merged in.
    Seeds not yet indexed appear with indexed=False and zero counts.
    """
    try:
        from scraper.aws_doc_urls import PRIMARY_SEED_KEYS, SEED_URLS
    except Exception:
        return []

    currently_indexing = _ingest_progress.get("current_service") or ""

    seeds = []
    for key in PRIMARY_SEED_KEYS:
        info = SEED_URLS.get(key, {})
        manifest_entry = manifest_sources.get(key, {})
        chunks = manifest_entry.get("chunks_indexed", 0)
        indexed = chunks > 0

        # Check if this service is the one currently being scraped
        name = info.get("name", key)
        is_active = (
            _ingest_running
            and currently_indexing
            and (
                currently_indexing.startswith("Fetching:")
                and name in currently_indexing
            )
        )

        seeds.append({
            "key": key,
            "name": name,
            "tier": info.get("tier", 1),
            "url": info.get("url", ""),
            "indexed": indexed,
            "active": is_active,
            "chunks": chunks,
            "pages": manifest_entry.get("pages_scraped", 0),
            "last_indexed": manifest_entry.get("crawl_timestamp"),
        })
    return seeds


@router.get("/status")
async def get_status():
    """Return chunk count, per-seed manifest, and live ingest progress."""
    try:
        count = db.get_chunk_count()
        manifest = db.get_manifest()
        manifest_sources = manifest.get("sources", {})

        all_seeds = _build_all_seeds(manifest_sources)
        indexed_count = sum(1 for s in all_seeds if s["indexed"])

        progress = None
        if _ingest_running:
            progress = {
                "current_service": _ingest_progress.get("current_service"),
                "services_done": _ingest_progress.get("services_done", 0),
                "services_total": _ingest_progress.get("services_total", 0),
                "started_at": _ingest_progress.get("started_at"),
            }

        return {
            "chunk_count": count,
            "last_updated": manifest.get("last_updated"),
            "total_chunks": manifest.get("total_chunks", count),
            "ingest_running": _ingest_running,
            "ingest_progress": progress,
            "all_seeds": all_seeds,
            "indexed_services": indexed_count,
            "total_services": len(all_seeds),
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
    global _ingest_running, _ingest_progress
    _ingest_running = True
    _ingest_progress = {
        "current_service": "Starting…",
        "services_done": 0,
        "services_total": 0,
        "started_at": datetime.now().isoformat(),
    }
    try:
        from scraper.aws_doc_urls import PRIMARY_SEED_KEYS
        from ingestion.ingest_pipeline import run_ingestion
        run_ingestion(
            seed_keys=PRIMARY_SEED_KEYS,
            max_pages_per_seed=20,
            save_to_disk=False,
            progress_callback=_progress_callback,
        )
    except Exception:
        logger.exception("Ingest run failed")
    finally:
        _ingest_running = False
        _ingest_progress["current_service"] = None
