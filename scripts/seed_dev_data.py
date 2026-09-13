"""Popula o banco com dados de exemplo, para ver o dashboard funcionando
sem depender da chave da API-Football (útil para conferir a interface).

Uso:
    docker compose exec app python -m scripts.seed_dev_data
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from app.db.session import async_session_factory
from app.leagues import LEAGUES
from app.models.match import Match, MatchStatus
from app.models.match_stats import MatchTeamStats
from app.models.team import Team
from app.services.ingestion import ensure_league

TEAM_NAMES = {
    "premier_league": ["Manchester United", "Liverpool", "Arsenal", "Chelsea"],
    "la_liga": ["Real Madrid", "Barcelona", "Atlético de Madrid", "Sevilla"],
    "serie_a": ["Juventus", "Inter de Milão", "AC Milan", "Napoli"],
    "primeira_liga": ["Benfica", "Porto", "Sporting", "Braga"],
    "bundesliga": ["Bayern de Munique", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen"],
    "brasileirao": ["Flamengo", "Palmeiras", "São Paulo", "Corinthians"],
    "champions_league": ["Manchester City", "Real Madrid", "Bayern de Munique", "PSG"],
    "libertadores": ["Flamengo", "River Plate", "Palmeiras", "Boca Juniors"],
}


async def seed() -> None:
    async with async_session_factory() as session:
        now = datetime.now(timezone.utc)

        for idx, league_config in enumerate(LEAGUES):
            # Reaproveita a liga se ela já existir (ex: criada por uma
            # ingestão real anterior) em vez de tentar duplicar — evita
            # violar a constraint de api_football_id único.
            league = await ensure_league(session, league_config)

            names = TEAM_NAMES[league_config.slug]
            teams = []
            for i, name in enumerate(names):
                team = Team(api_football_id=league_config.api_football_id * 1000 + i, name=name)
                session.add(team)
                await session.flush()
                teams.append(team)

            # 5 jogos passados (finalizados) entre os times, com estatísticas,
            # pra "últimos 5 jogos" e os rankings terem o que mostrar.
            fixture_api_seq = league_config.api_football_id * 10_000
            for i in range(5):
                home, away = teams[i % 4], teams[(i + 1) % 4]
                match = Match(
                    api_football_id=fixture_api_seq + i,
                    league_id=league.id,
                    season=2026,
                    round=f"Rodada {i + 1}",
                    home_team_id=home.id,
                    away_team_id=away.id,
                    kickoff_utc=now - timedelta(days=7 * (5 - i)),
                    status=MatchStatus.FINISHED,
                    home_score=(i % 3),
                    away_score=((i + 1) % 3),
                )
                session.add(match)
                await session.flush()

                session.add(MatchTeamStats(
                    match_id=match.id, team_id=home.id,
                    corners=4 + i, yellow_cards=1 + (i % 3), red_cards=0,
                    shots_total=10 + i, shots_on_target=4 + i, possession_pct=52.0, fouls=8, offsides=1,
                ))
                session.add(MatchTeamStats(
                    match_id=match.id, team_id=away.id,
                    corners=3 + i, yellow_cards=2 + (i % 2), red_cards=0,
                    shots_total=8 + i, shots_on_target=3 + i, possession_pct=48.0, fouls=9, offsides=2,
                ))

            # 1 jogo "hoje", ainda não realizado, pra aparecer na tela inicial.
            today_match = Match(
                api_football_id=fixture_api_seq + 99,
                league_id=league.id,
                season=2026,
                round="Rodada 6",
                home_team_id=teams[0].id,
                away_team_id=teams[1].id,
                kickoff_utc=now.replace(hour=16, minute=0, second=0, microsecond=0) + timedelta(minutes=idx),
                status=MatchStatus.SCHEDULED,
            )
            session.add(today_match)

        await session.commit()
    print("Dados de exemplo criados com sucesso.")


if __name__ == "__main__":
    asyncio.run(seed())
