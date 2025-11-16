# models/sensor_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.configs import DBBaseModel

class Sensor(DBBaseModel):
    __tablename__ = "sensores"

    id_sensor = Column(Integer, primary_key=True, index=True)
    tipo_sensor = Column(String, nullable=False)
    unidade_medida = Column(String, nullable=False)

    id_controlador = Column(Integer, ForeignKey("controladores.id_controlador"))
    controlador = relationship("Controlador", back_populates="sensores")

    zonas = relationship("ZonaSensor", back_populates="sensor")
    leituras = relationship("LeituraSensor", back_populates="sensor")
