from pydantic import BaseModel
from typing import Optional

class SensorBase(BaseModel):
    tipo_sensor: str
    unidade_medida: str
    id_controlador: int

class SensorCreate(SensorBase):
    pass

class SensorOut(SensorBase):
    id_sensor: int

    class Config:
        orm_mode = True
