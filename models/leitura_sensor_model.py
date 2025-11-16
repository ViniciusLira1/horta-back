from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.configs import DBBaseModel

class LeituraSensor(DBBaseModel):
    __tablename__ = "leituras_sensores"

    id_leitura = Column(Integer, primary_key=True, index=True)
    id_sensor = Column(Integer, ForeignKey("sensores.id_sensor"), nullable=False)
    valor = Column(Float, nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    sensor = relationship("Sensor", back_populates="leituras")
