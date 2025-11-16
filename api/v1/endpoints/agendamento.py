from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime, time
from core.deps import get_session
from models.agendamento_model import Agendamento
from schemas.agendamento_schema import AgendamentoCreate, AgendamentoOut

router = APIRouter()

# Criar agendamento
@router.post("/", response_model=AgendamentoOut)
async def create_agendamento(agendamento: AgendamentoCreate, db: AsyncSession = Depends(get_session)):
    new_agendamento = Agendamento(**agendamento.dict())
    db.add(new_agendamento)
    await db.commit()
    await db.refresh(new_agendamento)
    return new_agendamento


# Listar todos os agendamentos
@router.get("/", response_model=List[AgendamentoOut])
async def list_agendamentos(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Agendamento))
    return result.scalars().all()


# Buscar agendamento por ID
@router.get("/{id_agendamento}", response_model=AgendamentoOut)
async def get_agendamento(id_agendamento: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Agendamento).filter(Agendamento.id_agendamento == id_agendamento))
    agendamento = result.scalars().first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    return agendamento


# Atualizar agendamento
@router.put("/{id_agendamento}", response_model=AgendamentoOut)
async def update_agendamento(id_agendamento: int, agendamento: AgendamentoCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Agendamento).filter(Agendamento.id_agendamento == id_agendamento))
    db_agendamento = result.scalars().first()

    if not db_agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    for key, value in agendamento.dict().items():
        setattr(db_agendamento, key, value)

    await db.commit()
    await db.refresh(db_agendamento)
    return db_agendamento


# Deletar agendamento
@router.delete("/{id_agendamento}")
async def delete_agendamento(id_agendamento: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Agendamento).filter(Agendamento.id_agendamento == id_agendamento))
    agendamento = result.scalars().first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    await db.delete(agendamento)
    await db.commit()
    return {"message": "Agendamento removido com sucesso"}


# Executar manualmente a irrigação
@router.post("/{id_agendamento}/executar")
async def executar_agendamento(id_agendamento: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Agendamento).filter(Agendamento.id_agendamento == id_agendamento))
    agendamento = result.scalars().first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    # Aqui futuramente vamos integrar com o microcontrolador (ESP32)
    agendamento.ultima_execucao = datetime.utcnow()
    await db.commit()
    return {"message": f"Irrigação manual executada para '{agendamento.nome}'"}
