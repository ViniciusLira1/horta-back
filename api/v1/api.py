from fastapi import APIRouter
from .endpoints import users, controlador, sensor, zona_sensor, leitura_sensor, agendamento, bomba, execucoes

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Usuários"])
api_router.include_router(controlador.router, prefix="/controladores", tags=["Controladores"])
api_router.include_router(sensor.router, prefix="/sensores", tags=["Sensores"])
api_router.include_router(zona_sensor.router, prefix="/zonas", tags=["Zonas de Sensores"])
api_router.include_router(leitura_sensor.router, prefix="/leitura", tags=["Leitura do Sensor"])
api_router.include_router(agendamento.router, prefix="/agendamento", tags=["Agendamento"])
api_router.include_router(bomba.router, prefix="/bomba", tags=["Bomba"])
api_router.include_router(execucoes.router, prefix="/execucoes", tags=["Execuções de Irrigação"])