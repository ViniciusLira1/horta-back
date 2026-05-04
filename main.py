import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import models.__all_models  # noqa: garante que todos os models estão registrados
from api.v1.api import api_router
from core.configs import settings, DBBaseModel
from core.database import engine, SessionLocal
from core.scheduler import iniciar_scheduler
from sqlalchemy import text
from sqlalchemy.future import select
from models.execucao_model import ExecucaoIrrigacao


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Cria tabelas que ainda não existem
    async with engine.begin() as conn:
        await conn.run_sync(DBBaseModel.metadata.create_all)
        # Migração: adiciona coluna descricao se ainda não existir
        try:
            await conn.execute(text("ALTER TABLE execucoes_irrigacao ADD COLUMN descricao TEXT"))
        except Exception:
            pass  # coluna já existe

    # 2. Marca execuções travadas como erro (servidor foi reiniciado durante irrigação)
    async with SessionLocal() as db:
        result = await db.execute(
            select(ExecucaoIrrigacao).where(ExecucaoIrrigacao.status == "em_andamento")
        )
        travadas = result.scalars().all()
        for ex in travadas:
            ex.status = "erro"
            ex.descricao = "Servidor reiniciado durante a execução"
        if travadas:
            await db.commit()
            print(f"[Startup] {len(travadas)} execução(ões) travada(s) marcada(s) como erro")

    # 3. Garante que _estado começa limpo
    from api.v1.endpoints.bomba import _estado
    _estado["ligada"] = False
    _estado["id_execucao_ativa"] = None

    # 4. Inicia o scheduler de agendamentos
    task = asyncio.create_task(iniciar_scheduler())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="API Irrigação IoT", version="1.0", lifespan=lifespan)

# 🔥 CORS (LIBERA TUDO - DEV)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/ping")
async def ping():
    return {"msg": "pong!"}



if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
    )