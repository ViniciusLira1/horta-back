from fastapi import FastAPI
from api.v1.api import api_router
from core.configs import settings

app = FastAPI(title="API Irrigação IoT", version="1.0")

# Adiciona router da API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/ping")
async def ping():
    return {"msg": "pong!"}
