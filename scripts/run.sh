#!/bin/sh
set -e

# DB 연결 대기 (최대 30초 시도)
counter=0
until uv run alembic current 2>/dev/null ; do
    counter=$((counter+1))
    if [ $counter -gt 30 ]; then
        echo "Error: Database connection failed after 30 attempts."
        exit 1
    fi
    echo "Waiting for database... ($counter/30)"
    sleep 1
done

uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload