import asyncio
from datetime import datetime, timezone, timedelta, time as time_type
from sqlalchemy.future import select

from core.database import SessionLocal
from models.agendamento_model import Agendamento
from models.execucao_model import ExecucaoIrrigacao

# Brasília = UTC-3 fixo (sem horário de verão desde 2019)
BRASILIA = timezone(timedelta(hours=-3))
UTC = timezone.utc

# weekday() 0=Mon…5=Sat, 6=Sun  →  chaves usadas no frontend
_DIA_MAP = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


def _to_time(value) -> time_type:
    """Converte para time independente do que o SQLite devolver (time ou string)."""
    if isinstance(value, time_type):
        return value
    if isinstance(value, str):
        parts = value.split(":")
        h = int(parts[0])
        m = int(parts[1])
        s = int(float(parts[2])) if len(parts) > 2 else 0
        return time_type(h, m, s)
    raise TypeError(f"Não foi possível converter {type(value)} para time")


async def _executar_agendamento(ag_id: int, id_zona_sensor: int, duracao_minutos: int, nome: str) -> None:
    from api.v1.endpoints.bomba import _estado, _auto_completar, _criar_task

    if _estado.get("ligada"):
        return  # bomba ocupada — tenta no próximo minuto se ainda estiver no horário

    async with SessionLocal() as db:
        result = await db.execute(
            select(Agendamento).where(Agendamento.id_agendamento == ag_id)
        )
        ag = result.scalars().first()
        if not ag:
            return

        ag.ultima_execucao = datetime.utcnow()

        execucao = ExecucaoIrrigacao(
            id_zona_sensor=id_zona_sensor,
            id_agendamento=ag_id,
            tipo="agendado",
            iniciado_em=datetime.utcnow(),
            duracao_minutos=duracao_minutos,
            status="em_andamento",
            descricao=f"Agendamento '{nome}' disparado automaticamente pelo scheduler",
        )
        db.add(execucao)
        await db.commit()
        await db.refresh(execucao)
        execucao_id = execucao.id_execucao

    _estado["ligada"] = True
    _estado["id_execucao_ativa"] = execucao_id
    _criar_task(_auto_completar(execucao_id, duracao_minutos))


async def _verificar_agendamentos() -> None:
    agora = datetime.now(BRASILIA)
    hora_atual = agora.time().replace(second=0, microsecond=0)
    dia_atual = _DIA_MAP[agora.weekday()]

    print(f"[Scheduler] Verificando às {hora_atual} ({dia_atual})")

    async with SessionLocal() as db:
        result = await db.execute(select(Agendamento).where(Agendamento.ativo == True))
        agendamentos = result.scalars().all()

    print(f"[Scheduler] {len(agendamentos)} agendamento(s) ativo(s) encontrado(s)")

    for ag in agendamentos:
        try:
            hora_ag = _to_time(ag.hora_inicio).replace(second=0, microsecond=0)
        except Exception as e:
            print(f"[Scheduler] Erro ao ler hora_inicio do agendamento {ag.id_agendamento}: {e}")
            continue

        # ── 1. Verifica horário ───────────────────────────────────────
        if hora_ag != hora_atual:
            continue

        print(f"[Scheduler]  → '{ag.nome}' hora={hora_ag} repetir_todos_dias={ag.repetir_todos_dias} dias={ag.dias_semana}")

        # ── 2. Já executou hoje em Brasília? ─────────────────────────
        if ag.ultima_execucao:
            ultima_br = ag.ultima_execucao.replace(tzinfo=UTC).astimezone(BRASILIA)
            if ultima_br.date() == agora.date():
                print(f"[Scheduler]  → '{ag.nome}' já executou hoje, pulando")
                continue

        # ── 3. Verifica regra de repetição ───────────────────────────
        if not ag.repetir_todos_dias:
            if ag.intervalo_dias and ag.ultima_execucao:
                ultima_utc = ag.ultima_execucao.replace(tzinfo=UTC)
                if (agora - ultima_utc).days < ag.intervalo_dias:
                    continue
            elif ag.dias_semana:
                dias = {d.strip() for d in ag.dias_semana.split(",")}
                if dia_atual not in dias:
                    continue
            else:
                continue

        print(f"[Scheduler]  → Disparando '{ag.nome}'")
        asyncio.create_task(
            _executar_agendamento(ag.id_agendamento, ag.id_zona_sensor, ag.duracao_minutos, ag.nome)
        )


async def iniciar_scheduler() -> None:
    """Verifica agendamentos a cada 60 segundos."""
    print("[Scheduler] Iniciado")
    while True:
        try:
            await _verificar_agendamentos()
        except Exception as e:
            print(f"[Scheduler] Erro na verificação: {e}")
        await asyncio.sleep(60)
