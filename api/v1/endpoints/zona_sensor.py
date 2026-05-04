from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.zonas_model import ZonaSensor
from models.agendamento_model import Agendamento
from models.execucao_model import ExecucaoIrrigacao
from schemas.zonas_schema import ZonaSensorCreate, ZonaSensorOut
from core.deps import get_session



router = APIRouter()


# Criar nova zona
@router.post("/", response_model=ZonaSensorOut, status_code=status.HTTP_201_CREATED)
async def criar_zona(zona: ZonaSensorCreate, db: AsyncSession = Depends(get_session)):
    nova_zona = ZonaSensor(
        nome_zona=zona.nome_zona,
        id_controlador=zona.id_controlador,
        id_sensor=zona.id_sensor
    )
    db.add(nova_zona)
    await db.commit()
    await db.refresh(nova_zona)
    return nova_zona


# Listar todas as zonas
@router.get("/", response_model=list[ZonaSensorOut])
async def listar_zonas(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ZonaSensor))
    zonas = result.scalars().all()
    return zonas


# Buscar zona por ID
@router.get("/{zona_id}", response_model=ZonaSensorOut)
async def buscar_zona(zona_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ZonaSensor).filter(ZonaSensor.id_zona_sensor == zona_id))
    zona = result.scalars().first()
    if not zona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona não encontrada")
    return zona


# Atualizar zona
@router.put("/{zona_id}", response_model=ZonaSensorOut)
async def atualizar_zona(zona_id: int, zona_data: ZonaSensorCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ZonaSensor).filter(ZonaSensor.id_zona_sensor == zona_id))
    zona = result.scalars().first()
    if not zona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona não encontrada")

    zona.nome_zona = zona_data.nome_zona
    zona.id_controlador = zona_data.id_controlador
    zona.id_sensor = zona_data.id_sensor

    await db.commit()
    await db.refresh(zona)
    return zona


# Deletar zona
@router.delete("/{zona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_zona(zona_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(ZonaSensor).filter(ZonaSensor.id_zona_sensor == zona_id))
    zona = result.scalars().first()
    if not zona:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zona não encontrada")

    ag_result = await db.execute(
        select(Agendamento).where(Agendamento.id_zona_sensor == zona_id)
    )
    agendamentos = ag_result.scalars().all()
    if agendamentos:
        nomes = ", ".join(f'"{a.nome}"' for a in agendamentos)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Não é possível excluir: a zona possui {len(agendamentos)} agendamento(s) vinculado(s) ({nomes}). Exclua os agendamentos primeiro.",
        )

    # Remove o histórico de execuções vinculado à zona antes de deletar
    exec_result = await db.execute(
        select(ExecucaoIrrigacao).where(ExecucaoIrrigacao.id_zona_sensor == zona_id)
    )
    for execucao in exec_result.scalars().all():
        await db.delete(execucao)
    await db.flush()

    await db.delete(zona)
    await db.commit()
    return None
