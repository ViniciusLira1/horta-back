from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.configs import DBBaseModel

class ZonaSensor(DBBaseModel):
    __tablename__ = "zonas_sensores"

    id_zona_sensor = Column(Integer, primary_key=True, index=True)
    nome_zona = Column(String, nullable=False)

    id_controlador = Column(Integer, ForeignKey("controladores.id_controlador"))
    controlador = relationship("Controlador", back_populates="zonas")

    id_sensor = Column(Integer, ForeignKey("sensores.id_sensor"))
    sensor = relationship("Sensor", back_populates="zonas")  # 👈 nome bate com Sensor.zonas
    # zona_model.py
    agendamentos = relationship("Agendamento", back_populates="zonas")
