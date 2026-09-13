from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
    def _normalize_for_asyncpg(cls, value: str) -> str:
        """Provedores de hospedagem (Render, Neon, Heroku, etc.) costumam
        entregar a URL do Postgres como 'postgres://' ou 'postgresql://', às
        vezes com '?sslmode=require' — isso é sintaxe do libpq/psycopg2, e o
        driver asyncpg não entende esse parâmetro (usamos DATABASE_SSL pra
        isso). Aqui a gente troca o driver e remove esse parâmetro se vier.
        """
        if value.startswith("postgres://"):
            value = value.replace("postgres://", "postgresql+asyncpg://", 1)
        elif value.startswith("postgresql://") and not value.startswith("postgresql+asyncpg://"):
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1)

        libpq_only_params = {"sslmode", "channel_binding"}
        parts = urlsplit(value)
        query = [(k, v) for k, v in parse_qsl(parts.query) if k not in libpq_only_params]
        return urlunsplit(parts._replace(query=urlencode(query)))


@lru_cache
def get_settings() -> Settings:
    return Settings()
