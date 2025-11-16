from cryptography.fernet import Fernet
from passlib.context import CryptContext
import secrets
from core.configs import settings

# Fernet para criptografia de dados sensíveis (Wi-Fi, tokens, etc)
fernet = Fernet(settings.FERNET_KEY.encode())

# Criptografia de senha (hash)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Função para gerar token seguro
def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

# Funções de criptografia/descriptografia com Fernet
def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
