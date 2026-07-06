from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://calling_agent:calling_agent_secret@localhost:5432/calling_agent"
    DATABASE_URL_SYNC: str = "postgresql://calling_agent:calling_agent_secret@localhost:5432/calling_agent"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "super-secret-change-me-in-production-9f8e7d6c5b4a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    EXOTEL_ACCOUNT_SID: str = ""
    EXOTEL_API_KEY: str = ""
    EXOTEL_API_TOKEN: str = ""
    EXOTEL_CALLER_ID: str = "+919999999999"
    EXOTEL_BASE_URL: str = "https://api.exotel.com/v1"

    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    TTS_LANGUAGE_CODE: str = "hi-IN"
    TTS_VOICE_NAME: str = "hi-IN-Wavenet-A"

    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
