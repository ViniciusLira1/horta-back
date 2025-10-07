from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base

# Base global para todos os Models
DBBaseModel = declarative_base()

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = "sqlite+aiosqlite:///./meubanco.db"  # banco local SQLite

    class Config:
        case_sensitive = True

settings = Settings()
