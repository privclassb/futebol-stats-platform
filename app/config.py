from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_football_key: str = ""
    api_football_base_url: str = "https://v3.football.api-sports.io"

    odds_api_key: str = ""

    database_url: str = "postgresql+asyncpg://futebol:futebol@db:5432/futebol_stats"
    database_ssl: bool = False
    """Ative (DATABASE_SSL=true) ao rodar em hospedagens que exigem SSL na
    conexão com o Postgres (ex: banco externo no Render)."""

    @field_validator("database_url")
    @classmethod
    def _use_asyncpg_driver(cls, value: str) -> str:
        """Provedores de hospedagem (Render, Heroku, etc.) costumam entregar a
        URL do Postgres como 'postgres://' ou 'postgresql://' — o SQLAlchemy
        async precisa do driver explícito 'postgresql+asyncpg://'."""
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
