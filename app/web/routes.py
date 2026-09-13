from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.league import League
from app.models.match import Match
from app.models.team import Team
from app.services.filters import teams_ranked_by_average
from app.services.probability import get_probability_panel_placeholder
from app.services.team_form import get_team_form

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

FILTERS = {
    "corners": ("corners", "Maior média de escanteios"),
    "cards": ("yellow_cards", "Maior número de cartões"),
}


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, filtro: str | None = Query(None)):
    today = datetime.now(timezone.utc).date()
    day_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    async with async_session_factory() as session:
        result = await session.execute(
            select(Match)
            .where(Match.kickoff_utc >= day_start, Match.kickoff_utc < day_end)
            .order_by(Match.kickoff_utc)
        )
        matches = list(result.scalars())

        team_ids = {m.home_team_id for m in matches} | {m.away_team_id for m in matches}
        teams = {}
        league_ids = {m.league_id for m in matches}
        leagues = {}
        if team_ids:
            teams = {t.id: t for t in (await session.execute(select(Team).where(Team.id.in_(team_ids)))).scalars()}
        if league_ids:
            leagues = {
                l.id: l for l in (await session.execute(select(League).where(League.id.in_(league_ids)))).scalars()
            }

        ranking = None
        if filtro in FILTERS:
            metric, label = FILTERS[filtro]
            ranking = {"label": label, "items": await teams_ranked_by_average(session, metric)}

    matches_by_league: dict[str, list[dict]] = {}
    for match in matches:
        league_obj = leagues.get(match.league_id)
        league_name = league_obj.name if league_obj else "Outro"
        matches_by_league.setdefault(league_name, []).append(
            {
                "id": match.id,
                "home": teams.get(match.home_team_id),
                "away": teams.get(match.away_team_id),
                "kickoff_utc": match.kickoff_utc,
                "status": match.status.value,
                "home_score": match.home_score,
                "away_score": match.away_score,
            }
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "today": today,
            "matches_by_league": matches_by_league,
            "filters": FILTERS,
            "active_filter": filtro,
            "ranking": ranking,
            "has_any_match": bool(matches),
        },
    )


@router.get("/jogos/{match_id}", response_class=HTMLResponse)
async def match_detail(request: Request, match_id: int):
    async with async_session_factory() as session:
        match = await session.get(Match, match_id)
        if match is None:
            return HTMLResponse("Jogo não encontrado.", status_code=404)

        home_team = await session.get(Team, match.home_team_id)
        away_team = await session.get(Team, match.away_team_id)
        league = await session.get(League, match.league_id)

        home_recent = await get_team_form(session, match.home_team_id, league_id=None, limit=5)
        away_recent = await get_team_form(session, match.away_team_id, league_id=None, limit=5)
        home_in_league = await get_team_form(session, match.home_team_id, league_id=match.league_id, limit=10)
        away_in_league = await get_team_form(session, match.away_team_id, league_id=match.league_id, limit=10)

    probability = get_probability_panel_placeholder()

    return templates.TemplateResponse(
        "match_detail.html",
        {
            "request": request,
            "match": match,
            "home_team": home_team,
            "away_team": away_team,
            "league": league,
            "home_recent": home_recent,
            "away_recent": away_recent,
            "home_in_league": home_in_league,
            "away_in_league": away_in_league,
            "probability": probability,
        },
    )
