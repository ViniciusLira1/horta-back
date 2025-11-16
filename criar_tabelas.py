import asyncio
import sys
import os
import models.__all_models  
# Adiciona o diretório raiz do projeto no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.configs import DBBaseModel
from core.database import engine

async def create_tables() -> None:
   
    import models.__all_models  

    print('Criando as tabelas do banco de dados')

    async with engine.begin() as conn:
        # Remove tabelas existentes (opcional, útil em dev)
        await conn.run_sync(DBBaseModel.metadata.drop_all)
        # Cria todas as tabelas
        await conn.run_sync(DBBaseModel.metadata.create_all)
    
    print('Tabelas criadas com sucesso!')

if __name__ == "__main__":
    asyncio.run(create_tables())
