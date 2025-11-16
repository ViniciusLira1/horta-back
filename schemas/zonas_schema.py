from pydantic import BaseModel
from typing import Optional

class ZonaSensorBase(BaseModel):
    nome_zona: str
    id_controlador: int
    id_sensor: int

class ZonaSensorCreate(ZonaSensorBase):
    pass

class ZonaSensorOut(ZonaSensorBase):
    id_zona_sensor: int

    class Config:
        orm_mode = True
