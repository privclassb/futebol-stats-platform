from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, MatchStatus
from app.models.match_stats import MatchTeamStats


@dataclass
class TeamFormSummary:
    games_counted: int
    avg_goals_scored: float | None
    avg_goals_conceded: float | None
    avg_corners: float | None
    avg_yellow_cards: float | None
    avg_red_cards: float | None


def _average(values: list[float]) -> float | None:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


async def get_team_form(
    session: AsyncSession, team_id: int, league_id: int | None = None, limit: int = 5
) -> TeamFormSummary:
    """Resumo de forma de um time: média de gols, cartões e escanteios.

    Sem `league_id`: últimos N jogos do time em qualquer competição.
    Com `league_id`: últimos N jogos do time NAQUELE campeonato específico
    (usado para comparar 'forma geral' com 'forma no torneio').
    """
    query = (
        select(Match, MatchTeamStats)
        .outerjoin(
            MatchTeamStats,
            (MatchTeamStats.match_id == Match.id) & (MatchTeamStats.team_id == team_id),
        )
        .where(
            Match.status == MatchStatus.FINISHED,
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
        )
        .order_by(Match.kickoff_utc.desc())
        .limit(limit)
    )
    if league_id is not None:
        query = query.where(Match.league_id == league_id)

    rows = (await session.execute(query)).all()

    goals_scored: list[float] = []
    goals_conceded: list[float] = []
    corners: list[float] = []
    yellow_cards: list[float] = []
    red_cards: list[float] = []

    for match, stats in rows:
        is_home = match.home_team_id == team_id
        scored = match.home_score if is_home else match.away_score
        conceded = match.away_score if is_home else match.home_score
        if scored is not None:
            goals_scored.append(scored)
        if conceded is not None:
            goals_conceded.append(conceded)
        if stats is not None:
            if stats.corners is not None:
                corners.append(stats.corners)
            if stats.yellow_cards is not None:
                yellow_cards.append(stats.yellow_cards)
            if stats.red_cards is not None:
                red_cards.append(stats.red_cards)

    return TeamFormSummary(
        games_counted=len(rows),
        avg_goals_scored=_average(goals_scored),
        avg_goals_conceded=_average(goals_conceded),
        avg_corners=_average(corners),
        avg_yellow_cards=_average(yellow_cards),
        avg_red_cards=_average(red_cards),
    )
