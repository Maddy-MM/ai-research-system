#!/usr/bin/env sh
set -e

python -m src.mcp_server.server &
sleep 2
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"