# models/controlador_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.configs import DBBaseModel
from utils.security import generate_token
from cryptography.fernet import Fernet
from core.configs import settings

fernet = Fernet(settings.FERNET_KEY)

class Controlador(DBBaseModel):
    __tablename__ = "controladores"

    id_controlador = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    usuario = relationship("User", back_populates="controladores")

    ssid_criptografado = Column(String, nullable=True)
    senha_wifi_criptografada = Column(String, nullable=True)
    token_vinculacao = Column(String, unique=True, nullable=False, default=generate_token)

    
    zonas = relationship("ZonaSensor", back_populates="controlador")  

   
    sensores = relationship("Sensor", back_populates="controlador")

    def set_wifi(self, ssid: str, senha: str):
        self.ssid_criptografado = fernet.encrypt(ssid.encode()).decode()
        self.senha_wifi_criptografada = fernet.encrypt(senha.encode()).decode()

    def get_wifi(self):
        if self.ssid_criptografado and self.senha_wifi_criptografada:
            ssid = fernet.decrypt(self.ssid_criptografado.encode()).decode()
            senha = fernet.decrypt(self.senha_wifi_criptografada.encode()).decode()
            return ssid, senha
        return None, None

    def reset_total(self):
        self.ssid_criptografado = None
        self.senha_wifi_criptografada = None
        self.id_usuario = None
        self.token_vinculacao = generate_token()
