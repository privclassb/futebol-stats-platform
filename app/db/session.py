from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app import models  # noqa: F401  (garante que todos os modelos sejam registrados no Base)

settings = get_settings()

connect_args: dict = {"statement_cache_size": 0}
"""Necessário com conexões via 'pooler' (ex: Neon, PgBouncer) — sem isso, o
asyncpg tenta reusar prepared statements que o pooler não suporta."""
if settings.database_ssl:
    connect_args["ssl"] = True

engine = create_async_engine(settings.database_url, echo=False, connect_args=connect_args)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
