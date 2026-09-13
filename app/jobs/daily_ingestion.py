from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.session import async_session_factory
from app.providers.api_football.client import ApiFootballClient
from app.services.ingestion import sync_daily_fixtures

logger = logging.getLogger(__name__)


async def run_daily_ingestion() -> None:
    """Busca os jogos do dia de todas as ligas configuradas.

    Roda 1x/dia (ver `start_scheduler`) para caber na cota do plano grátis da
    API-Football (100 chamadas/dia): 6 ligas = 6 chamadas nesta rotina,
    sobrando cota para estatísticas consultadas sob demanda pelo dashboard.
    """
    today = datetime.now(timezone.utc).date()
    logger.info("Iniciando ingestão diária de jogos (%s)", today)
    provider = ApiFootballClient()
    async with async_session_factory() as session:
        matches = await sync_daily_fixtures(session, provider, today)
    logger.info("Ingestão concluída: %d jogos sincronizados", len(matches))


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # 05:00 UTC cobre a manhã em todos os fusos das ligas cobertas, antes dos
    # primeiros jogos do dia na Europa e no Brasil.
    scheduler.add_job(run_daily_ingestion, "cron", hour=5, minute=0, id="daily_ingestion")
    scheduler.start()
    return scheduler
