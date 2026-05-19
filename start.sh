#!/bin/sh
# Entrypoint for Railway deployment.
# Runs startup_ingest.py in the background, then execs uvicorn as PID 1.
# Using exec replaces this shell with uvicorn so Railway signals are handled correctly.

set -e

echo "Starting AWS Financial Services Assistant API..."
echo "PORT: ${PORT:-8000}"

# Run knowledge base ingestion in the background.
# If it fails (e.g. DB not yet reachable), it logs and exits — uvicorn is unaffected.
python startup_ingest.py &

# Exec uvicorn so it becomes PID 1 — required for Railway's health checks and signal handling.
# workers=1 is mandatory: SessionStore is in-process memory.
exec uvicorn api.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --timeout-keep-alive 120
