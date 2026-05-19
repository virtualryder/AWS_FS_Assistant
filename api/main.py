"""
AWS Financial Services Assistant — FastAPI Backend

Exposes all app functionality as a JSON + SSE REST API so the Next.js frontend
can replace the Streamlit UI without touching any Python agent code.

Run with:
    uvicorn api.main:app --reload --port 8000

Or for production:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1

Note: workers must be 1 — the SessionStore is in-process memory.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on the import path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.session_store import store as session_store
from api.routers import customers, conversations, chat, documents, discovery, knowledge_base, general_chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Background TTL eviction ───────────────────────────────────────────────────

async def _eviction_loop():
    """Periodically evict idle agent sessions from memory."""
    while True:
        await asyncio.sleep(600)  # run every 10 minutes
        try:
            n = session_store.evict_stale()
            if n:
                logger.info("Session eviction: removed %d stale sessions", n)
        except Exception:
            logger.exception("Error during session eviction")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_eviction_loop())
    logger.info("AWS Financial Services Assistant API started")
    yield
    task.cancel()
    logger.info("AWS Financial Services Assistant API stopped")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AWS Financial Services Assistant API",
    description=(
        "REST + SSE backend for the AWS Financial Services Assistant. "
        "Powered by dual AI agents (AWS Architect + GenAI/ML) with full "
        "financial services regulatory compliance validation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js dev server and production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://awsfsfrontend-production.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(customers.router,       prefix="/api")
app.include_router(conversations.router,   prefix="/api")
app.include_router(chat.router,            prefix="/api")
app.include_router(documents.router,       prefix="/api")
app.include_router(discovery.router,       prefix="/api")
app.include_router(knowledge_base.router,  prefix="/api")
app.include_router(general_chat.router,    prefix="/api")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "sessions": len(session_store)}
