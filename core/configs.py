from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
import os

# Base global para todos os Models
DBBaseModel = declarative_base()


def _build_db_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./meubanco.db")
    # Railway fornece postgresql://, SQLAlchemy async precisa de postgresql+asyncpg://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = _build_db_url()
    FERNET_KEY: str = os.getenv("FERNET_KEY", "b2xqR7vK5iH1s9Z8vP6hQ0lW2aT4nY3fU7xD9eM0K2o=")

    class Config:
        case_sensitive = True

settings = Settings()
