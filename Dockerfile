# 베이스 이미지로 가볍고 최신 Python 3.12 슬림 버전 사용
FROM python:3.12-slim

# Python이 pyc 바이트코드 파일을 생성하지 않고, 버퍼링 없이 로그를 출력하도록 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# uv(astral-sh/uv) 실행 파일을 다른 이미지에서 복사해옴 (pip 대체용)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 작업 디렉토리 설정: 이 위치에서 모든 명령어가 실행됨
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# 의존성 파일 복사 (pyproject.toml, uv.lock)
COPY ./pyproject.toml ./uv.lock ./

# 의존성 설치 2: 캐시 없이, uv.lock과 완전히 일치하는지 엄격하게 설치 (빌드 안정성 확보)
RUN uv sync --frozen --no-cache

# 앱 소스코드 복사
COPY ./app ./app
COPY .env .env

COPY ./alembic ./alembic
COPY alembic.ini .


# 외부와 통신하는 포트 노출 (FastAPI 기본 포트 8000)
EXPOSE 8000

# 실행 스크립트 복사 및 실행 권한 부여
COPY ./scripts/run.sh /scripts/run.sh
RUN chmod +x /scripts/run.sh

# 컨테이너 시작 시 실행할 기본 명령어 (run.sh 내부에 uvicorn 실행 커맨드 포함)
CMD ["/scripts/run.sh"]
#ENTRYPOINT [ "/bin/bash", "-c", "sleep 500" ]
