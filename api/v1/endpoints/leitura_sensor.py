from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from typing import Optional

from models.leitura_sensor_model import LeituraSensor
from schemas.leitura_sensor_schema import LeituraSensorCreate, LeituraSensorOut
from core.deps import get_session

router = APIRouter()


@router.post("/", response_model=LeituraSensorOut)
async def criar_leitura(leitura: LeituraSensorCreate, db: AsyncSession = Depends(get_session)):
    nova = LeituraSensor(**leitura.dict())
    db.add(nova)
    await db.commit()
    await db.refresh(nova)
    return nova


@router.get("/sensor/{id_sensor}/latest", response_model=LeituraSensorOut)
async def ultima_leitura(id_sensor: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(LeituraSensor)
        .where(LeituraSensor.id_sensor == id_sensor)
        .order_by(LeituraSensor.data_hora.desc())
        .limit(1)
    )
    leitura = result.scalars().first()
    if not leitura:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada.")
    return leitura


@router.get("/sensor/{id_sensor}", response_model=list[LeituraSensorOut])
async def listar_por_sensor(
    id_sensor: int,
    dias: int = Query(30, ge=1, le=365, description="Últimos N dias (ignorado se data_inicio/data_fim fornecidos)"),
    data_inicio: Optional[datetime] = Query(None, description="ISO datetime (ex: 2026-01-01T00:00:00)"),
    data_fim: Optional[datetime] = Query(None, description="ISO datetime (ex: 2026-01-31T23:59:59)"),
    db: AsyncSession = Depends(get_session),
):
    if data_inicio and data_fim:
        cutoff_start = data_inicio
        cutoff_end = data_fim
    else:
        cutoff_end = datetime.utcnow()
        cutoff_start = cutoff_end - timedelta(days=dias)

    result = await db.execute(
        select(LeituraSensor)
        .where(LeituraSensor.id_sensor == id_sensor)
        .where(LeituraSensor.data_hora >= cutoff_start)
        .where(LeituraSensor.data_hora <= cutoff_end)
        .order_by(LeituraSensor.data_hora.asc())
    )
    leituras = result.scalars().all()
    if not leituras:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para este sensor.")
    return leituras


@router.get("/", response_model=list[LeituraSensorOut])
async def listar_leituras(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(LeituraSensor).order_by(LeituraSensor.data_hora.desc()).limit(limit)
    )
    return result.scalars().all()
