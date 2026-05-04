"""
Seed de dados para o dashboard de Monitoramento.

Executa com:  python seed_data.py

O script:
  1. Cria a tabela execucoes_irrigacao se não existir (seguro: não dropa nada)
  2. Descobre o primeiro sensor e a primeira zona cadastrados
  3. Insere ~180 leituras de umidade dos últimos 30 dias com padrão realista
  4. Insere ~14 execuções de irrigação (mix manual/agendado)
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import models.__all_models  # noqa: garante que todos os models estão registrados
from core.configs import DBBaseModel
from core.database import engine, SessionLocal
from models.leitura_sensor_model import LeituraSensor
from models.execucao_model import ExecucaoIrrigacao
from sqlalchemy.future import select


async def main():
    # ── 1. Cria apenas tabelas que ainda não existem ──────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(DBBaseModel.metadata.create_all)
    print("✅ Tabelas verificadas/criadas")

    async with SessionLocal() as db:
        # ── 2. Descobre sensor e zona existentes ──────────────────────────────
        from models.sensor_model import Sensor
        from models.zonas_model import ZonaSensor
        from models.agendamento_model import Agendamento

        sensor_result = await db.execute(select(Sensor).limit(1))
        sensor = sensor_result.scalars().first()

        zona_result = await db.execute(select(ZonaSensor).limit(1))
        zona = zona_result.scalars().first()

        if not sensor:
            print("⚠️  Nenhum sensor encontrado. Cadastre um sensor antes de rodar o seed.")
            return
        if not zona:
            print("⚠️  Nenhuma zona encontrada. Cadastre uma zona antes de rodar o seed.")
            return

        ag_result = await db.execute(select(Agendamento).limit(1))
        agendamento = ag_result.scalars().first()

        print(f"🌱 Usando sensor id={sensor.id_sensor}  |  zona id={zona.id_zona_sensor}")

        # ── 3. Leituras de umidade ─────────────────────────────────────────────
        # Padrão: irrigação a cada ~3 dias eleva umidade para 65-72%;
        # depois declina ~2-3 % por ciclo de 4h, com ruído de ±2 %.

        agora = datetime.utcnow()
        inicio = agora - timedelta(days=30)

        # Dias em que ocorreu irrigação (a cada ~3 dias)
        irrigation_days: set[int] = set(range(0, 30, 3))  # dias 0, 3, 6, 9…

        leituras_novas: list[LeituraSensor] = []
        umidade = 65.0  # começa alta (logo após irrigação)

        for day_offset in range(30):
            if day_offset in irrigation_days:
                umidade = random.uniform(63.0, 72.0)  # recupera com irrigação

            for hour in [0, 4, 8, 12, 16, 20]:
                ts = inicio + timedelta(days=day_offset, hours=hour)
                if ts > agora:
                    break

                noise = random.uniform(-1.5, 1.5)
                valor = round(max(18.0, min(85.0, umidade + noise)), 1)

                leituras_novas.append(
                    LeituraSensor(
                        id_sensor=sensor.id_sensor,
                        valor=valor,
                        data_hora=ts,
                    )
                )
                umidade -= random.uniform(1.8, 3.2)  # seca gradualmente

        db.add_all(leituras_novas)
        await db.commit()
        print(f"✅ {len(leituras_novas)} leituras inseridas")

        # ── 4. Execuções de irrigação ──────────────────────────────────────────
        execucoes: list[ExecucaoIrrigacao] = []

        for i, day_offset in enumerate(sorted(irrigation_days)):
            ts = inicio + timedelta(days=day_offset, hours=random.randint(6, 18))
            if ts > agora:
                break

            # Alterna manual / agendado
            if i % 3 == 0:
                tipo = "manual"
                id_ag = None
            else:
                tipo = "agendado"
                id_ag = agendamento.id_agendamento if agendamento else None

            execucoes.append(
                ExecucaoIrrigacao(
                    id_zona_sensor=zona.id_zona_sensor,
                    id_agendamento=id_ag,
                    tipo=tipo,
                    iniciado_em=ts,
                    duracao_minutos=random.choice([5, 8, 10, 12, 15]),
                    status="concluido",
                )
            )

        db.add_all(execucoes)
        await db.commit()
        print(f"✅ {len(execucoes)} execuções de irrigação inseridas")

    print("\n🎉 Seed concluído! Reinicie o servidor FastAPI.")


if __name__ == "__main__":
    asyncio.run(main())
