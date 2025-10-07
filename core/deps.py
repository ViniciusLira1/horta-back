from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import SessionLocal

# Dependência para obter a sessão em cada request
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
