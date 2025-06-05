# 베이스 이미지
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# uv 및 필수 도구 설치
RUN apt-get update && apt-get install -y curl build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 작업 디렉토리 설정
WORKDIR /app

# pyproject.toml & uv.lock 복사 및 설치
COPY ./pyproject.toml ./uv.lock ./
RUN ~/.cargo/bin/uv venv install

# 애플리케이션 코드 복사
COPY ./app ./app


# 포트 설정 (FastAPI일 경우도 동일)
EXPOSE 8000

COPY ./scripts /scripts
RUN chmod +x /scripts/run.sh
CMD ["/scripts/run.sh"]