from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LeagueConfig:
    slug: str
    """Identificador curto usado internamente, ex: 'premier_league'."""
    name: str
    country: str
    api_football_id: int
    """Id da liga na API-Football (conferir em /leagues caso a temporada mude de id)."""
    calendar_season: bool
    """True para campeonatos que rodam dentro de um único ano civil (ex: Brasileirão).
    False para campeonatos 'cruzados' que começam num ano e terminam no seguinte
    (ex: Premier League 2026/27), onde a API-Football usa o ano de INÍCIO como season."""


LEAGUES: list[LeagueConfig] = [
    LeagueConfig("premier_league", "Premier League", "Inglaterra", 39, calendar_season=False),
    LeagueConfig("la_liga", "La Liga", "Espanha", 140, calendar_season=False),
    LeagueConfig("serie_a", "Serie A", "Itália", 135, calendar_season=False),
    LeagueConfig("primeira_liga", "Primeira Liga", "Portugal", 94, calendar_season=False),
    LeagueConfig("bundesliga", "Bundesliga", "Alemanha", 78, calendar_season=False),
    LeagueConfig("brasileirao", "Brasileirão Série A", "Brasil", 71, calendar_season=True),
    LeagueConfig("champions_league", "UEFA Champions League", "Europa", 2, calendar_season=False),
    LeagueConfig("libertadores", "CONMEBOL Libertadores", "América do Sul", 13, calendar_season=True),
]


def season_for(league: LeagueConfig, day: date) -> int:
    """Resolve o 'season' (ano) que a API-Football espera para uma data.

    Campeonatos europeus são identificados pelo ano em que começam (ex: a
    temporada 2026/27, que roda de ago/2026 a mai/2027, é 'season=2026' o ano
    inteiro). Campeonatos de ano civil (Brasileirão) usam o próprio ano.
    """
    if league.calendar_season:
        return day.year
    return day.year if day.month >= 7 else day.year - 1
