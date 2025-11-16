from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LeituraSensorBase(BaseModel):
    id_sensor: int
    valor: float

class LeituraSensorCreate(LeituraSensorBase):
    pass

class LeituraSensorOut(LeituraSensorBase):
    id_leitura: int
    data_hora: datetime

    class Config:
        orm_mode = True
