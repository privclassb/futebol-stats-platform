from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.leagues import LEAGUES, LeagueConfig
from app.models.league import League
from app.models.match import Match
from app.models.match_stats import MatchTeamStats
from app.models.player import Player
from app.models.player_stats import PlayerMatchStats
from app.models.team import Team
from app.providers.api_football.client import ApiFootballClient, ApiFootballError
from app.providers.api_football.mapper import FixtureData, TeamRef, map_fixture, map_player_stats, map_team_stats

logger = logging.getLogger(__name__)


async def ensure_league(session: AsyncSession, league_config: LeagueConfig) -> League:
    result = await session.execute(
        select(League).where(League.api_football_id == league_config.api_football_id)
    )
    league = result.scalar_one_or_none()
    if league is None:
        league = League(
            api_football_id=league_config.api_football_id,
            name=league_config.name,
            country=league_config.country,
            slug=league_config.slug,
        )
        session.add(league)
        await session.flush()
    return league


async def ensure_team(session: AsyncSession, team_ref: TeamRef) -> Team:
    result = await session.execute(select(Team).where(Team.api_football_id == team_ref.api_football_id))
    team = result.scalar_one_or_none()
    if team is None:
        team = Team(api_football_id=team_ref.api_football_id, name=team_ref.name, logo_url=team_ref.logo_url)
        session.add(team)
        await session.flush()
    return team


async def ensure_player(session: AsyncSession, player_api_id: int, name: str, team_id: int) -> Player:
    result = await session.execute(select(Player).where(Player.api_football_id == player_api_id))
    player = result.scalar_one_or_none()
    if player is None:
        player = Player(api_football_id=player_api_id, name=name, team_id=team_id)
        session.add(player)
        await session.flush()
    elif player.team_id != team_id:
        player.team_id = team_id
    return player


async def upsert_fixture(session: AsyncSession, league: League, fixture: FixtureData) -> Match:
    home_team = await ensure_team(session, fixture.home_team)
    away_team = await ensure_team(session, fixture.away_team)

    result = await session.execute(select(Match).where(Match.api_football_id == fixture.api_football_id))
    match = result.scalar_one_or_none()
    if match is None:
        match = Match(api_football_id=fixture.api_football_id, league_id=league.id)
        session.add(match)

    match.season = fixture.season
    match.round = fixture.round
    match.home_team_id = home_team.id
    match.away_team_id = away_team.id
    match.kickoff_utc = fixture.kickoff_utc
    match.status = fixture.status
    match.venue = fixture.venue
    match.home_score = fixture.home_score
    match.away_score = fixture.away_score

    await session.flush()
    return match


async def sync_daily_fixtures(session: AsyncSession, provider: ApiFootballClient, day: date) -> list[Match]:
    """Busca os jogos do dia de todos os campeonatos configurados e grava no banco.

    Uma falha em uma liga (ex: cota da API estourada no meio do processo) não
    derruba as outras — é logada e a ingestão segue para a próxima liga.
    """
    synced: list[Match] = []
    for league_config in LEAGUES:
        try:
            raw_fixtures = await provider.get_fixtures_by_date(league_config.api_football_id, day)
        except ApiFootballError:
            logger.exception("Falha ao buscar jogos de %s", league_config.name)
            continue

        league = await ensure_league(session, league_config)
        for raw in raw_fixtures:
            match = await upsert_fixture(session, league, map_fixture(raw))
            synced.append(match)

    await session.commit()
    return synced


async def sync_match_statistics(session: AsyncSession, provider: ApiFootballClient, match: Match) -> None:
    """Busca e grava estatísticas de time e jogador de UMA partida já finalizada.

    Chamado sob demanda (não no job diário) para não estourar a cota do plano
    grátis com partidas que ninguém está olhando ainda.
    """
    try:
        raw_team_stats = await provider.get_fixture_statistics(match.api_football_id)
        raw_player_stats = await provider.get_fixture_players(match.api_football_id)
    except ApiFootballError:
        logger.exception("Falha ao buscar estatísticas da partida %s", match.api_football_id)
        return

    await session.execute(
        MatchTeamStats.__table__.delete().where(MatchTeamStats.match_id == match.id)
    )
    await session.execute(
        PlayerMatchStats.__table__.delete().where(PlayerMatchStats.match_id == match.id)
    )

    home_team = await session.get(Team, match.home_team_id)
    away_team = await session.get(Team, match.away_team_id)
    team_api_to_id = {home_team.api_football_id: match.home_team_id, away_team.api_football_id: match.away_team_id}

    for raw_entry in raw_team_stats:
        stats = map_team_stats(raw_entry)
        team_id = team_api_to_id.get(stats.team_api_id)
        if team_id is None:
            continue
        session.add(
            MatchTeamStats(
                match_id=match.id,
                team_id=team_id,
                corners=stats.corners,
                yellow_cards=stats.yellow_cards,
                red_cards=stats.red_cards,
                shots_total=stats.shots_total,
                shots_on_target=stats.shots_on_target,
                possession_pct=stats.possession_pct,
                fouls=stats.fouls,
                offsides=stats.offsides,
            )
        )

    for raw_team_entry in raw_player_stats:
        team_id = team_api_to_id.get(raw_team_entry["team"]["id"])
        if team_id is None:
            continue
        for player_stat in map_player_stats(raw_team_entry):
            player = await ensure_player(session, player_stat.player_api_id, player_stat.player_name, team_id)
            session.add(
                PlayerMatchStats(
                    match_id=match.id,
                    player_id=player.id,
                    team_id=team_id,
                    minutes_played=player_stat.minutes_played,
                    goals=player_stat.goals,
                    assists=player_stat.assists,
                    yellow_cards=player_stat.yellow_cards,
                    red_cards=player_stat.red_cards,
                    shots_total=player_stat.shots_total,
                    shots_on_target=player_stat.shots_on_target,
                    rating=player_stat.rating,
                )
            )

    await session.commit()
