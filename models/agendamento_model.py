from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.configs import DBBaseModel

class Agendamento(DBBaseModel):
    __tablename__ = "agendamentos"

    id_agendamento = Column(Integer, primary_key=True, index=True)
    id_zona_sensor = Column(Integer, ForeignKey("zonas_sensores.id_zona_sensor"), nullable=False)
    nome = Column(String, nullable=False)

    hora_inicio = Column(Time, nullable=False)
    duracao_minutos = Column(Integer, nullable=False)

    # --- Configurações de repetição ---
    repetir_todos_dias = Column(Boolean, default=False)
    dias_semana = Column(String, nullable=True)  # Ex: "segunda,quarta,sexta"
    intervalo_dias = Column(Integer, nullable=True)  # Ex: 2 → a cada 2 dias

    # --- Controle de execução manual ---
    ativo = Column(Boolean, default=True)
    ultima_execucao = Column(DateTime, nullable=True)

    # Relacionamento
    zonas = relationship("ZonaSensor", back_populates="agendamentos")
