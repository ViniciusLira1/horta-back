from pydantic import BaseModel, EmailStr

# Schema base (comum para entrada e saída)
class UserBase(BaseModel):
    nome: str
    email: EmailStr

# Schema para criação de usuário (request)
class UserCreate(UserBase):
    senha: str  # enviado pelo usuário no cadastro

# Schema para resposta de usuário (response)
class UserOut(UserBase):
    id_usuario: int  # ID gerado pelo banco

    class Config:
        orm_mode = True  # permite converter de SQLAlchemy para Pydantic
