from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.configs import DBBaseModel


class ExecucaoIrrigacao(DBBaseModel):
    __tablename__ = "execucoes_irrigacao"

    id_execucao = Column(Integer, primary_key=True, index=True)
    id_zona_sensor = Column(Integer, ForeignKey("zonas_sensores.id_zona_sensor"), nullable=False)
    # NULL = execução manual; preenchido = disparada por agendamento
    id_agendamento = Column(Integer, ForeignKey("agendamentos.id_agendamento"), nullable=True)

    tipo = Column(String, nullable=False)          # "manual" | "agendado"
    iniciado_em = Column(DateTime, default=datetime.utcnow)
    duracao_minutos = Column(Integer, nullable=False)
    status = Column(String, default="concluido")   # "concluido" | "interrompido" | "em_andamento" | "erro"
    descricao = Column(String, nullable=True)       # log/mensagem de status

    zona = relationship("ZonaSensor", back_populates="execucoes")
    agendamento = relationship("Agendamento", back_populates="execucoes")
