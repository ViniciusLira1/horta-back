from pydantic import BaseModel
from typing import Optional

class ControladorBase(BaseModel):
    nome: str


# Usado para criação de controlador (pode incluir Wi-Fi opcionalmente)
class ControladorCreate(ControladorBase):
    ssid: Optional[str] = None
    senha_wifi: Optional[str] = None
    id_usuario: Optional[int] = None


# Usado para atualizar o nome do controlador
class ControladorUpdate(BaseModel):
    nome: Optional[str] = None


# Usado para retorno (GET, POST etc)
class ControladorOut(ControladorBase):
    id_controlador: int
    id_usuario: Optional[int] = None
    token_vinculacao: str

    class Config:
        orm_mode = True
