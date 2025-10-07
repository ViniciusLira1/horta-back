from passlib.context import CryptContext

# Troca para sha256_crypt
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Gera o hash da senha usando SHA-256.
    Sem limite de tamanho.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash.
    """
    return pwd_context.verify(plain_password, hashed_password)
