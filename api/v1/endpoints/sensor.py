from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from models.sensor_model import Sensor
from schemas.sensor_schema import SensorCreate, SensorOut
from core.deps import get_session

router = APIRouter()

# ---------------------- CRIAR SENSOR ----------------------
@router.post("/", response_model=SensorOut, status_code=status.HTTP_201_CREATED)
async def create_sensor(sensor: SensorCreate, db: AsyncSession = Depends(get_session)):
    new_sensor = Sensor(**sensor.dict())
    db.add(new_sensor)
    await db.commit()
    await db.refresh(new_sensor)
    return new_sensor

# ---------------------- LISTAR TODOS ----------------------
@router.get("/", response_model=List[SensorOut])
async def list_sensors(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Sensor))
    return result.scalars().all()

# ---------------------- BUSCAR POR ID ----------------------
@router.get("/{id_sensor}", response_model=SensorOut)
async def get_sensor(id_sensor: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Sensor).filter(Sensor.id_sensor == id_sensor))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado")
    return sensor

# ---------------------- ATUALIZAR SENSOR ----------------------
@router.put("/{id_sensor}", response_model=SensorOut)
async def update_sensor(id_sensor: int, sensor_update: SensorCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Sensor).filter(Sensor.id_sensor == id_sensor))
    sensor = result.scalar_one_or_none()

    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado")

    for key, value in sensor_update.dict().items():
        setattr(sensor, key, value)

    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return sensor

# ---------------------- DELETAR SENSOR ----------------------
@router.delete("/{id_sensor}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sensor(id_sensor: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Sensor).filter(Sensor.id_sensor == id_sensor))
    sensor = result.scalar_one_or_none()

    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sensor não encontrado")

    await db.delete(sensor)
    await db.commit()
    return None
