from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base
import os

# Base global para todos os Models
DBBaseModel = declarative_base()

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = "sqlite+aiosqlite:///./meubanco.db"  # banco local SQLite
    FERNET_KEY: str = "b2xqR7vK5iH1s9Z8vP6hQ0lW2aT4nY3fU7xD9eM0K2o="  # Chave para Fernet

    class Config:
        case_sensitive = True

settings = Settings()
