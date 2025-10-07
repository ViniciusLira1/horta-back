import asyncio
from core.configs import DBBaseModel
from core.database import engine

async def create_tables() -> None:
    # Força o carregamento de todos os models
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
