from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.leitura_sensor_model import LeituraSensor
from schemas.leitura_sensor_schema import LeituraSensorCreate, LeituraSensorOut
from core.deps import get_session

router = APIRouter()

# Criar uma leitura
@router.post("/", response_model=LeituraSensorOut)
async def criar_leitura(leitura: LeituraSensorCreate, db: AsyncSession = Depends(get_session)):
    nova_leitura = LeituraSensor(**leitura.dict())
    db.add(nova_leitura)
    await db.commit()
    await db.refresh(nova_leitura)
    return nova_leitura

# Listar todas as leituras
@router.get("/", response_model=list[LeituraSensorOut])
async def listar_leituras(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(LeituraSensor))
    leituras = result.scalars().all()
    return leituras

# Buscar leituras por sensor
@router.get("/sensor/{id_sensor}", response_model=list[LeituraSensorOut])
async def listar_por_sensor(id_sensor: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(LeituraSensor).where(LeituraSensor.id_sensor == id_sensor))
    leituras = result.scalars().all()
    if not leituras:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para este sensor.")
    return leituras
