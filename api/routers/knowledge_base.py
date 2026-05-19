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
    "phase": None,           # "fetching" | "chunking" | "upserting" | "completed" | "skipped"
    "current_service": None, # display name of current service
    "services_done": 0,
    "services_total": 0,
    "started_at": None,
    # current-service detail
    "current_pages": 0,
    "current_chunks": 0,
    "current_batch": 0,
    "current_total_batches": 0,
    # run-level totals
    "pages_this_run": 0,
    "chunks_this_run": 0,
    "services_completed": [],  # list of completed service names
}


def _progress_callback(message: str, current: int, total: int) -> None:
    """Parse structured progress messages from ingest_pipeline and update state."""
    global _ingest_progress
    p = _ingest_progress
    p["services_done"] = current
    p["services_total"] = total

    parts = message.split(":", 1)
    cmd = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    if cmd == "fetch":
        p["phase"] = "fetching"
        p["current_service"] = rest
        p["current_pages"] = 0
        p["current_chunks"] = 0
        p["current_batch"] = 0
        p["current_total_batches"] = 0

    elif cmd == "chunk":
        sub = rest.split(":", 1)
        p["phase"] = "chunking"
        p["current_service"] = sub[0]
        p["current_pages"] = int(sub[1]) if len(sub) > 1 else 0

    elif cmd == "upsert":
        sub = rest.split(":")
        # upsert:{name}:{batch_idx}:{total_batches}:{total_chunks}
        p["phase"] = "upserting"
        p["current_service"] = sub[0] if len(sub) > 0 else rest
        p["current_batch"] = int(sub[1]) if len(sub) > 1 else 0
        p["current_total_batches"] = int(sub[2]) if len(sub) > 2 else 0
        p["current_chunks"] = int(sub[3]) if len(sub) > 3 else 0

    elif cmd == "done":
        sub = rest.split(":")
        name = sub[0] if len(sub) > 0 else rest
        pages = int(sub[1]) if len(sub) > 1 else 0
        chunks = int(sub[2]) if len(sub) > 2 else 0
        p["phase"] = "completed"
        p["current_service"] = name
        p["pages_this_run"] += pages
        p["chunks_this_run"] += chunks
        if name not in p["services_completed"]:
            p["services_completed"].append(name)

    elif cmd == "skip":
        p["phase"] = "skipped"
        p["current_service"] = rest

    else:
        # Legacy / fallback
        p["phase"] = "fetching"
        p["current_service"] = message


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
            started_at = _ingest_progress.get("started_at")
            elapsed_seconds: int | None = None
            if started_at:
                try:
                    elapsed_seconds = int(
                        (datetime.now() - datetime.fromisoformat(started_at)).total_seconds()
                    )
                except Exception:
                    pass

            progress = {
                "phase": _ingest_progress.get("phase"),
                "current_service": _ingest_progress.get("current_service"),
                "services_done": _ingest_progress.get("services_done", 0),
                "services_total": _ingest_progress.get("services_total", 0),
                "current_pages": _ingest_progress.get("current_pages", 0),
                "current_chunks": _ingest_progress.get("current_chunks", 0),
                "current_batch": _ingest_progress.get("current_batch", 0),
                "current_total_batches": _ingest_progress.get("current_total_batches", 0),
                "pages_this_run": _ingest_progress.get("pages_this_run", 0),
                "chunks_this_run": _ingest_progress.get("chunks_this_run", 0),
                "services_completed": _ingest_progress.get("services_completed", []),
                "started_at": started_at,
                "elapsed_seconds": elapsed_seconds,
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
        "phase": "starting",
        "current_service": "Starting…",
        "services_done": 0,
        "services_total": 0,
        "started_at": datetime.now().isoformat(),
        "current_pages": 0,
        "current_chunks": 0,
        "current_batch": 0,
        "current_total_batches": 0,
        "pages_this_run": 0,
        "chunks_this_run": 0,
        "services_completed": [],
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
