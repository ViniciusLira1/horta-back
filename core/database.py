from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.configs import settings

# Engine assíncrono
engine = create_async_engine(
    settings.DB_URL,
    echo=True,  # mostra queries no console
    future=True
)

# Session factory (assíncrona)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)
