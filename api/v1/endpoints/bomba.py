import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from core.deps import get_session
from core.database import SessionLocal
from models.execucao_model import ExecucaoIrrigacao

router = APIRouter()

_estado: dict = {"ligada": False, "id_execucao_ativa": None}

# Mantém referências às tasks para evitar coleta pelo GC
_tarefas: set = set()


def _criar_task(coro):
    t = asyncio.create_task(coro)
    _tarefas.add(t)
    t.add_done_callback(_tarefas.discard)
    return t


class LigarRequest(BaseModel):
    id_zona_sensor: int
    duracao_minutos: int = 5


async def _auto_completar(id_execucao: int, duracao_minutos: int):
    await asyncio.sleep(duracao_minutos * 60)

    if _estado.get("id_execucao_ativa") != id_execucao:
        return  # já foi parada manualmente

    try:
        async with SessionLocal() as db:
            result = await db.execute(
                select(ExecucaoIrrigacao).where(ExecucaoIrrigacao.id_execucao == id_execucao)
            )
            execucao = result.scalars().first()
            if execucao and execucao.status == "em_andamento":
                execucao.status = "concluido"
                execucao.descricao = f"Concluído automaticamente após {duracao_minutos} min"
                await db.commit()
    except Exception as e:
        print(f"[Bomba] Erro ao finalizar execução {id_execucao}: {e}")
    finally:
        if _estado.get("id_execucao_ativa") == id_execucao:
            _estado["ligada"] = False
            _estado["id_execucao_ativa"] = None


@router.post("/ligar")
async def ligar(req: LigarRequest, db: AsyncSession = Depends(get_session)):
    if _estado.get("ligada"):
        raise HTTPException(status_code=409, detail="Bomba já está em uso. Aguarde ou pare a irrigação atual.")

    execucao = ExecucaoIrrigacao(
        id_zona_sensor=req.id_zona_sensor,
        id_agendamento=None,
        tipo="manual",
        iniciado_em=datetime.utcnow(),
        duracao_minutos=req.duracao_minutos,
        status="em_andamento",
        descricao="Irrigação manual iniciada pelo dashboard",
    )
    db.add(execucao)
    await db.commit()
    await db.refresh(execucao)

    _estado["ligada"] = True
    _estado["id_execucao_ativa"] = execucao.id_execucao

    _criar_task(_auto_completar(execucao.id_execucao, req.duracao_minutos))

    return {"message": "Irrigação iniciada", "id_execucao": execucao.id_execucao}


@router.post("/desligar")
async def desligar(db: AsyncSession = Depends(get_session)):
    id_ativa = _estado.get("id_execucao_ativa")

    if id_ativa:
        result = await db.execute(
            select(ExecucaoIrrigacao).where(ExecucaoIrrigacao.id_execucao == id_ativa)
        )
        execucao = result.scalars().first()
        if execucao and execucao.status == "em_andamento":
            execucao.status = "interrompido"
            execucao.descricao = "Interrompido manualmente pelo usuário"
            await db.commit()

    _estado["ligada"] = False
    _estado["id_execucao_ativa"] = None

    return {"message": "Irrigação encerrada"}


@router.get("/status")
async def status():
    return {
        "ligada": _estado["ligada"],
        "id_execucao_ativa": _estado["id_execucao_ativa"],
    }
