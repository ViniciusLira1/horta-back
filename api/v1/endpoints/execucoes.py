from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, timedelta


from core.deps import get_session
from models.execucao_model import ExecucaoIrrigacao
from schemas.execucao_schema import ExecucaoCreate, ExecucaoOut

router = APIRouter()


@router.post("/", response_model=ExecucaoOut)
async def criar_execucao(
    execucao: ExecucaoCreate,
    db: AsyncSession = Depends(get_session),
):
    nova = ExecucaoIrrigacao(**execucao.dict())
    db.add(nova)
    await db.commit()
    await db.refresh(nova)

    # Retorna com nomes enriquecidos
    return await _enriquecer(nova.id_execucao, db)


@router.get("/", response_model=List[ExecucaoOut])
async def listar_execucoes(
    id_zona_sensor: Optional[int] = None,
    tipo: Optional[str] = None,
    dias: int = Query(30, ge=1, le=365),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_session),
):
    if data_inicio and data_fim:
        cutoff = data_inicio
        cutoff_end = data_fim
    else:
        cutoff = datetime.utcnow() - timedelta(days=dias)
        cutoff_end = datetime.utcnow()

    stmt = (
        select(ExecucaoIrrigacao)
        .options(
            joinedload(ExecucaoIrrigacao.zona),
            joinedload(ExecucaoIrrigacao.agendamento),
        )
        .where(ExecucaoIrrigacao.iniciado_em >= cutoff)
        .where(ExecucaoIrrigacao.iniciado_em <= cutoff_end)
        .order_by(ExecucaoIrrigacao.iniciado_em.desc())
    )

    if id_zona_sensor is not None:
        stmt = stmt.where(ExecucaoIrrigacao.id_zona_sensor == id_zona_sensor)
    if tipo is not None:
        stmt = stmt.where(ExecucaoIrrigacao.tipo == tipo)

    result = await db.execute(stmt)
    rows = result.scalars().unique().all()

    return [
        ExecucaoOut(
            id_execucao=e.id_execucao,
            id_zona_sensor=e.id_zona_sensor,
            id_agendamento=e.id_agendamento,
            tipo=e.tipo,
            iniciado_em=e.iniciado_em,
            duracao_minutos=e.duracao_minutos,
            status=e.status,
            nome_zona=e.zona.nome_zona if e.zona else None,
            nome_agendamento=e.agendamento.nome if e.agendamento else None,
            descricao=e.descricao,
        )
        for e in rows
    ]


async def _enriquecer(id_execucao: int, db: AsyncSession) -> ExecucaoOut:
    stmt = (
        select(ExecucaoIrrigacao)
        .options(
            joinedload(ExecucaoIrrigacao.zona),
            joinedload(ExecucaoIrrigacao.agendamento),
        )
        .where(ExecucaoIrrigacao.id_execucao == id_execucao)
    )
    result = await db.execute(stmt)
    e = result.scalars().first()
    return ExecucaoOut(
        id_execucao=e.id_execucao,
        id_zona_sensor=e.id_zona_sensor,
        id_agendamento=e.id_agendamento,
        tipo=e.tipo,
        iniciado_em=e.iniciado_em,
        duracao_minutos=e.duracao_minutos,
        status=e.status,
        nome_zona=e.zona.nome_zona if e.zona else None,
        nome_agendamento=e.agendamento.nome if e.agendamento else None,
        descricao=e.descricao,
    )
