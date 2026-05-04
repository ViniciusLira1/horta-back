from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExecucaoCreate(BaseModel):
    id_zona_sensor: int
    id_agendamento: Optional[int] = None
    tipo: str               # "manual" | "agendado"
    duracao_minutos: int
    status: Optional[str] = "concluido"


class ExecucaoOut(BaseModel):
    id_execucao: int
    id_zona_sensor: int
    id_agendamento: Optional[int]
    tipo: str
    iniciado_em: datetime
    duracao_minutos: int
    status: str
    descricao: Optional[str] = None
    nome_zona: Optional[str] = None
    nome_agendamento: Optional[str] = None

    class Config:
        from_attributes = True
