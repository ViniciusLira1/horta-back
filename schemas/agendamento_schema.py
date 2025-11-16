from pydantic import BaseModel
from typing import Optional
from datetime import time, datetime

class AgendamentoBase(BaseModel):
    nome: str
    hora_inicio: time
    duracao_minutos: int
    repetir_todos_dias: Optional[bool] = False
    dias_semana: Optional[str] = None
    intervalo_dias: Optional[int] = None
    ativo: Optional[bool] = True

class AgendamentoCreate(AgendamentoBase):
    id_zona_sensor: int

class AgendamentoOut(AgendamentoBase):
    id_agendamento: int
    id_zona_sensor: int
    ultima_execucao: Optional[datetime] = None

    class Config:
        orm_mode = True
