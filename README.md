# 도커 이미지 빌드 

```bash 
docker build -t octofastapi . 
```

# 도커 프로젝트 실행 

```bash 
docker compose up -d  
```

## 라이브러리 추가 시 빌드 새로 해야됨!
```bash 
docker compose up -d --build  
```

# 로컬 개발환경 세팅 방법 
1. 깃 클론
2. UV 설치 가정 -> python3.13 -m venv .venv 
3. source .venv/bin/activate 
4. uv sync 
5. docker compose up -d 
6. db는 각각 