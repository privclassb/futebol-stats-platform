from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.config import get_settings
from app.providers.base import FixturesProvider


class ApiFootballError(RuntimeError):
    """Erro de comunicação ou de cota com a API-Football."""


class ApiFootballClient(FixturesProvider):
    """Cliente para a API-Football (https://www.api-football.com/documentation-v3).

    O plano grátis tem uma cota diária baixa (100 chamadas/dia) — o serviço de
    ingestão (app/services/ingestion.py) é quem controla QUANDO chamar isso,
    este client só sabe COMO falar com a API.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.api_football_key
        self._base_url = base_url or settings.api_football_base_url

    def _headers(self) -> dict[str, str]:
        return {"x-apisports-key": self._api_key}

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise ApiFootballError(
                "API_FOOTBALL_KEY não configurada. Crie uma conta grátis em "
                "https://www.api-football.com/ e preencha o .env."
            )
        async with httpx.AsyncClient(base_url=self._base_url, timeout=15.0) as client:
            response = await client.get(path, params=params, headers=self._headers())
        if response.status_code == 429:
            raise ApiFootballError("Cota diária da API-Football excedida.")
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise ApiFootballError(str(payload["errors"]))
        return payload

    async def get_fixtures_by_date(self, league_api_id: int, day: date) -> list[dict[str, Any]]:
        from app.leagues import LEAGUES, season_for

        league = next(l for l in LEAGUES if l.api_football_id == league_api_id)
        payload = await self._get(
            "/fixtures",
            {
                "league": league_api_id,
                "season": season_for(league, day),
                "date": day.isoformat(),
            },
        )
        return payload.get("response", [])

    async def get_fixture_statistics(self, fixture_api_id: int) -> list[dict[str, Any]]:
        payload = await self._get("/fixtures/statistics", {"fixture": fixture_api_id})
        return payload.get("response", [])

    async def get_fixture_players(self, fixture_api_id: int) -> list[dict[str, Any]]:
        """Estatísticas por jogador de uma partida (cartões, gols, etc.)."""
        payload = await self._get("/fixtures/players", {"fixture": fixture_api_id})
        return payload.get("response", [])

    async def get_team_recent_fixtures(self, team_api_id: int, last: int = 5) -> list[dict[str, Any]]:
        payload = await self._get("/fixtures", {"team": team_api_id, "last": last})
        return payload.get("response", [])

    async def get_odds(self, fixture_api_id: int) -> list[dict[str, Any]]:
        """Odds pré-jogo (fase 2). Disponível no plano grátis, mas atualizada
        apenas 1x/dia pela própria API-Football — não serve para comparação
        em tempo real entre casas nem para arbitragem (surebet)."""
        payload = await self._get("/odds", {"fixture": fixture_api_id})
        return payload.get("response", [])
