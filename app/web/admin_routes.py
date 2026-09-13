from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from sqlalchemy import func, select

from app.config import get_settings
from app.db.session import async_session_factory
from app.models.match import Match
from app.providers.api_football.client import ApiFootballClient
from app.services.ingestion import sync_daily_fixtures

router = APIRouter(prefix="/admin")


def _check_token(token: str) -> None:
    settings = get_settings()
    if not settings.admin_token or token != settings.admin_token:
        raise HTTPException(status_code=404)


@router.get("/sync-today", response_class=PlainTextResponse)
async def sync_today(token: str = "") -> str:
    """Roda a coleta de jogos do dia na hora, sem precisar esperar o job
    agendado. Existe porque planos grátis de hospedagem não dão acesso a
    terminal para rodar isso manualmente."""
    _check_token(token)
    today = datetime.now(timezone.utc).date()
    provider = ApiFootballClient()
    async with async_session_factory() as session:
        matches = await sync_daily_fixtures(session, provider, today)
    return f"Ingestão concluída: {len(matches)} jogos sincronizados para {today.isoformat()}."


@router.get("/seed", response_class=PlainTextResponse)
async def seed_dev_data(token: str = "") -> str:
    """Popula o banco com dados de exemplo (ver scripts/seed_dev_data.py).
    Só roda se ainda não houver nenhuma partida no banco, pra evitar duplicar
    dados se o link for aberto mais de uma vez (times/ligas já existentes,
    de uma ingestão real anterior, são reaproveitados normalmente)."""
    _check_token(token)
    async with async_session_factory() as session:
        already_seeded = (await session.execute(select(func.count()).select_from(Match))).scalar_one() > 0
    if already_seeded:
        return "Já existem partidas no banco — nada foi alterado."

    from scripts.seed_dev_data import seed

    await seed()
    return "Dados de exemplo criados com sucesso."
