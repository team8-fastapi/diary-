# 베이스 이미지
FROM python:3.13-slim-bookworm

# asyncmy를 위한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (패키지 전체 설치)
RUN uv sync --locked

# 코드 및 마이그레이션 복사
COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations

# FastAPI 실행
COPY ./scripts /scripts
RUN chmod +x /scripts/run.sh

# .venv/bin을 PATH에 추가
ENV PATH="/app/.venv/bin:$PATH"

CMD ["/scripts/run.sh"]