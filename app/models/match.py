from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_football_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)

    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"))
    season: Mapped[int] = mapped_column(Integer)
    round: Mapped[str | None] = mapped_column(String(60), nullable=True)

    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))

    kickoff_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"), default=MatchStatus.SCHEDULED
    )
    venue: Mapped[str | None] = mapped_column(String(120), nullable=True)

    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    league: Mapped["League"] = relationship(back_populates="matches")
    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])

    team_stats: Mapped[list["MatchTeamStats"]] = relationship(back_populates="match")
    player_stats: Mapped[list["PlayerMatchStats"]] = relationship(back_populates="match")
    odds_snapshots: Mapped[list["OddsSnapshot"]] = relationship(back_populates="match")
