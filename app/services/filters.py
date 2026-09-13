from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, MatchStatus
from app.models.match_stats import MatchTeamStats
from app.models.team import Team


@dataclass
class TeamAverage:
    team_id: int
    team_name: str
    games_counted: int
    average: float


async def _recent_team_stats(session: AsyncSession, games_per_team: int) -> dict[int, list[MatchTeamStats]]:
    """Últimos N jogos finalizados de cada time, mais recentes primeiro."""
    result = await session.execute(
        select(MatchTeamStats, Match.kickoff_utc)
        .join(Match, Match.id == MatchTeamStats.match_id)
        .where(Match.status == MatchStatus.FINISHED)
        .order_by(Match.kickoff_utc.desc())
    )
    by_team: dict[int, list[MatchTeamStats]] = {}
    for stats, _kickoff in result.all():
        bucket = by_team.setdefault(stats.team_id, [])
        if len(bucket) < games_per_team:
            bucket.append(stats)
    return by_team


async def teams_ranked_by_average(
    session: AsyncSession, metric: str, games_per_team: int = 5, limit: int = 20
) -> list[TeamAverage]:
    """Ranking de times pela média de uma estatística (ex: 'corners', 'yellow_cards')
    nos últimos N jogos finalizados. Usado pelos filtros 'maior média de escanteios'
    e 'maior número de cartões' na lista de jogos do dia.
    """
    by_team = await _recent_team_stats(session, games_per_team)
    if not by_team:
        return []

    team_ids = list(by_team.keys())
    teams = {t.id: t for t in (await session.execute(select(Team).where(Team.id.in_(team_ids)))).scalars()}

    averages: list[TeamAverage] = []
    for team_id, games in by_team.items():
        values = [getattr(g, metric) for g in games if getattr(g, metric) is not None]
        if not values:
            continue
        team = teams.get(team_id)
        averages.append(
            TeamAverage(
                team_id=team_id,
                team_name=team.name if team else f"Time #{team_id}",
                games_counted=len(values),
                average=sum(values) / len(values),
            )
        )

    averages.sort(key=lambda a: a.average, reverse=True)
    return averages[:limit]
