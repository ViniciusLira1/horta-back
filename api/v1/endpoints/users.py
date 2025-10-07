from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.deps import get_session
from models.users_model import User
from schemas.user_schema import UserCreate, UserOut
from utils.security import hash_password, verify_password  # SHA-256 sem limite de bytes
from pydantic import BaseModel

router = APIRouter()

# -------------------------
# CRIAR USUÁRIO
# -------------------------
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    # Verifica se já existe usuário com o mesmo email
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    db_user = User(
        nome=user.nome,
        email=user.email,
        senha_hash=hash_password(user.senha)  # SHA-256
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# -------------------------
# LISTAR TODOS OS USUÁRIOS
# -------------------------
@router.get("/", response_model=list[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# -------------------------
# PEGAR 1 USUÁRIO POR ID
# -------------------------
@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.id_usuario == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

# -------------------------
# DELETE USUÁRIO
# -------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.id_usuario == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    await db.delete(db_user)
    await db.commit()
    return None  # 204 No Content

# -------------------------
# LOGIN
# -------------------------
class UserLogin(BaseModel):
    email: str
    senha: str

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.senha, db_user.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    # Retorna OK, sem JWT por enquanto
    return {"msg": "Login realizado com sucesso", "user_id": db_user.id_usuario}
