#!/bin/sh
set -e

echo "DB 마이그레이션 시작..."
alembic upgrade head

echo "FastAPI 서버 실행..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 80 --reload