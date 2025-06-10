from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str = (
        "YOUR_SUPER_SECRET_KEY_HERE"  # 실제 환경에서는 매우 길고 복잡하게, 환경 변수에서 로드
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 액세스 토큰 만료 시간 (분)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
