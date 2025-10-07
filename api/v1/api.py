from fastapi import APIRouter
from .endpoints import users

api_router = APIRouter()

# Adiciona as rotas de usuário
api_router.include_router(users.router, prefix="/users", tags=["Usuários"])
