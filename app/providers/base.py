from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class FixturesProvider(ABC):
    """Contrato comum para qualquer fonte que forneça jogos do dia + estatísticas.

    Trocar de fonte (ex: API-Football -> outro provedor, ou adicionar um
    scraper complementar) significa apenas escrever uma nova classe que
    implementa esta interface — o resto do sistema (services/ingestion.py)
    não precisa saber de onde os dados vêm.
    """

    @abstractmethod
    async def get_fixtures_by_date(self, league_api_id: int, day: date) -> list[dict[str, Any]]:
        """Retorna os jogos de uma liga em uma data, no formato bruto da fonte."""

    @abstractmethod
    async def get_fixture_statistics(self, fixture_api_id: int) -> list[dict[str, Any]]:
        """Retorna estatísticas por time de uma partida específica."""

    @abstractmethod
    async def get_team_recent_fixtures(self, team_api_id: int, last: int = 5) -> list[dict[str, Any]]:
        """Retorna os últimos N jogos de um time (para médias recentes)."""
