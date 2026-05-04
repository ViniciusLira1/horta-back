from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.controlador_model import Controlador
from models.zonas_model import ZonaSensor
from models.sensor_model import Sensor
from core.deps import get_session
from schemas.controlador_schema import ControladorCreate, ControladorUpdate, ControladorOut
from api.v1.endpoints.sensor import _deletar_sensor_cascade

router = APIRouter()

# Criar novo controlador
@router.post("/", response_model=ControladorOut, status_code=status.HTTP_201_CREATED)
async def criar_controlador(controlador: ControladorCreate, db: AsyncSession = Depends(get_session)):
    novo_controlador = Controlador(nome=controlador.nome, id_usuario=controlador.id_usuario)
    db.add(novo_controlador)
    await db.commit()
    await db.refresh(novo_controlador)
    return novo_controlador


# Listar todos os controladores
@router.get("/", response_model=list[ControladorOut])
async def listar_controladores(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Controlador))
    controladores = result.scalars().all()
    return controladores


# Obter controlador por ID
@router.get("/{controlador_id}", response_model=ControladorOut)
async def obter_controlador(controlador_id: int, db: AsyncSession = Depends(get_session)):
    controlador = await db.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador não encontrado")
    return controlador


# Atualizar nome do controlador
@router.put("/{controlador_id}", response_model=ControladorOut)
async def atualizar_controlador(controlador_id: int, dados: ControladorUpdate, db: AsyncSession = Depends(get_session)):
    controlador = await db.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador não encontrado")

    controlador.nome = dados.nome or controlador.nome
    await db.commit()
    await db.refresh(controlador)
    return controlador


# Configurar Wi-Fi
@router.post("/{controlador_id}/wifi")
async def configurar_wifi(controlador_id: int, ssid: str, senha: str, db: AsyncSession = Depends(get_session)):
    controlador = await db.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador não encontrado")

    controlador.set_wifi(ssid, senha)
    await db.commit()
    return {"msg": "Wi-Fi configurado com sucesso"}


# Deletar controlador
@router.delete("/{controlador_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_controlador(controlador_id: int, db: AsyncSession = Depends(get_session)):
    controlador = await db.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador não encontrado")

    zonas_result = await db.execute(
        select(ZonaSensor).where(ZonaSensor.id_controlador == controlador_id)
    )
    zonas = zonas_result.scalars().all()
    if zonas:
        nomes = ", ".join(f'"{z.nome_zona}"' for z in zonas)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Não é possível excluir: o controlador possui {len(zonas)} zona(s) vinculada(s) ({nomes}). Exclua as zonas primeiro.",
        )

    sensores_result = await db.execute(
        select(Sensor).where(Sensor.id_controlador == controlador_id)
    )
    for sensor in sensores_result.scalars().all():
        await _deletar_sensor_cascade(sensor, db)
    await db.flush()

    await db.delete(controlador)
    await db.commit()
    return None


# Reset total (Wi-Fi, vinculação e token)
@router.post("/{controlador_id}/reset")
async def resetar_controlador(controlador_id: int, db: AsyncSession = Depends(get_session)):
    controlador = await db.get(Controlador, controlador_id)
    if not controlador:
        raise HTTPException(status_code=404, detail="Controlador não encontrado")

    controlador.reset_total()
    await db.commit()
    return {"msg": "Controlador resetado com sucesso", "novo_token": controlador.token_vinculacao}
