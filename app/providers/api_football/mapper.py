from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.models.match import MatchStatus

_STATUS_MAP: dict[str, MatchStatus] = {
    "TBD": MatchStatus.SCHEDULED,
    "NS": MatchStatus.SCHEDULED,
    "1H": MatchStatus.LIVE,
    "HT": MatchStatus.LIVE,
    "2H": MatchStatus.LIVE,
    "ET": MatchStatus.LIVE,
    "BT": MatchStatus.LIVE,
    "P": MatchStatus.LIVE,
    "SUSP": MatchStatus.LIVE,
    "INT": MatchStatus.LIVE,
    "LIVE": MatchStatus.LIVE,
    "FT": MatchStatus.FINISHED,
    "AET": MatchStatus.FINISHED,
    "PEN": MatchStatus.FINISHED,
    "PST": MatchStatus.POSTPONED,
    "CANC": MatchStatus.CANCELLED,
    "ABD": MatchStatus.CANCELLED,
    "AWD": MatchStatus.FINISHED,
    "WO": MatchStatus.FINISHED,
}


@dataclass
class TeamRef:
    api_football_id: int
    name: str
    logo_url: str | None


@dataclass
class FixtureData:
    api_football_id: int
    league_api_id: int
    season: int
    round: str | None
    kickoff_utc: datetime
    status: MatchStatus
    venue: str | None
    home_team: TeamRef
    away_team: TeamRef
    home_score: int | None
    away_score: int | None


@dataclass
class TeamStatsData:
    team_api_id: int
    corners: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None
    shots_total: int | None = None
    shots_on_target: int | None = None
    possession_pct: float | None = None
    fouls: int | None = None
    offsides: int | None = None


@dataclass
class PlayerStatsData:
    player_api_id: int
    player_name: str
    team_api_id: int
    minutes_played: int | None = None
    goals: int | None = None
    assists: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None
    shots_total: int | None = None
    shots_on_target: int | None = None
    rating: float | None = None


def map_fixture(raw: dict[str, Any]) -> FixtureData:
    fixture = raw["fixture"]
    league = raw["league"]
    teams = raw["teams"]
    goals = raw.get("goals", {})

    return FixtureData(
        api_football_id=fixture["id"],
        league_api_id=league["id"],
        season=league["season"],
        round=league.get("round"),
        kickoff_utc=datetime.fromisoformat(fixture["date"]),
        status=_STATUS_MAP.get(fixture["status"]["short"], MatchStatus.SCHEDULED),
        venue=(fixture.get("venue") or {}).get("name"),
        home_team=TeamRef(teams["home"]["id"], teams["home"]["name"], teams["home"].get("logo")),
        away_team=TeamRef(teams["away"]["id"], teams["away"]["name"], teams["away"].get("logo")),
        home_score=goals.get("home"),
        away_score=goals.get("away"),
    )


def _parse_percent(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace("%", "").strip()
        if not value:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


_TEAM_STAT_FIELD_BY_TYPE = {
    "Corner Kicks": "corners",
    "Yellow Cards": "yellow_cards",
    "Red Cards": "red_cards",
    "Total Shots": "shots_total",
    "Shots on Goal": "shots_on_target",
    "Ball Possession": "possession_pct",
    "Fouls": "fouls",
    "Offsides": "offsides",
}


def map_team_stats(raw_entry: dict[str, Any]) -> TeamStatsData:
    """`raw_entry` é um item da lista retornada por /fixtures/statistics."""
    data = TeamStatsData(team_api_id=raw_entry["team"]["id"])
    for stat in raw_entry.get("statistics", []):
        field = _TEAM_STAT_FIELD_BY_TYPE.get(stat["type"])
        if field is None:
            continue
        value = stat["value"]
        if field == "possession_pct":
            setattr(data, field, _parse_percent(value))
        else:
            setattr(data, field, int(value) if value is not None else None)
    return data


def map_player_stats(raw_team_entry: dict[str, Any]) -> list[PlayerStatsData]:
    """`raw_team_entry` é um item da lista retornada por /fixtures/players
    (um item por time, cada um com vários jogadores dentro)."""
    team_api_id = raw_team_entry["team"]["id"]
    results: list[PlayerStatsData] = []
    for player_entry in raw_team_entry.get("players", []):
        player = player_entry["player"]
        stats = (player_entry.get("statistics") or [{}])[0]
        games = stats.get("games") or {}
        shots = stats.get("shots") or {}
        goals = stats.get("goals") or {}
        cards = stats.get("cards") or {}
        rating_raw = games.get("rating")

        results.append(
            PlayerStatsData(
                player_api_id=player["id"],
                player_name=player["name"],
                team_api_id=team_api_id,
                minutes_played=games.get("minutes"),
                goals=goals.get("total"),
                assists=goals.get("assists"),
                yellow_cards=cards.get("yellow"),
                red_cards=cards.get("red"),
                shots_total=shots.get("total"),
                shots_on_target=shots.get("on"),
                rating=float(rating_raw) if rating_raw is not None else None,
            )
        )
    return results
