"""schema inicial

Revision ID: 0001
Revises:
Create Date: 2026-09-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_football_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("country", sa.String(80), nullable=False),
        sa.Column("slug", sa.String(60), nullable=False),
        sa.Column("logo_url", sa.String(255), nullable=True),
        sa.UniqueConstraint("api_football_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_leagues_api_football_id", "leagues", ["api_football_id"])

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_football_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("short_name", sa.String(40), nullable=True),
        sa.Column("country", sa.String(80), nullable=True),
        sa.Column("logo_url", sa.String(255), nullable=True),
        sa.UniqueConstraint("api_football_id"),
    )
    op.create_index("ix_teams_api_football_id", "teams", ["api_football_id"])

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_football_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("position", sa.String(20), nullable=True),
        sa.Column("nationality", sa.String(80), nullable=True),
        sa.Column("photo_url", sa.String(255), nullable=True),
        sa.UniqueConstraint("api_football_id"),
    )
    op.create_index("ix_players_api_football_id", "players", ["api_football_id"])

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("api_football_id", sa.Integer(), nullable=False),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round", sa.String(60), nullable=True),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("kickoff_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "scheduled", "live", "finished", "postponed", "cancelled",
                name="match_status",
            ),
            nullable=False,
            server_default="scheduled",
        ),
        sa.Column("venue", sa.String(120), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.UniqueConstraint("api_football_id"),
    )
    op.create_index("ix_matches_api_football_id", "matches", ["api_football_id"])
    op.create_index("ix_matches_kickoff_utc", "matches", ["kickoff_utc"])

    op.create_table(
        "match_team_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("corners", sa.Integer(), nullable=True),
        sa.Column("yellow_cards", sa.Integer(), nullable=True),
        sa.Column("red_cards", sa.Integer(), nullable=True),
        sa.Column("shots_total", sa.Integer(), nullable=True),
        sa.Column("shots_on_target", sa.Integer(), nullable=True),
        sa.Column("possession_pct", sa.Float(), nullable=True),
        sa.Column("fouls", sa.Integer(), nullable=True),
        sa.Column("offsides", sa.Integer(), nullable=True),
    )
    op.create_index("ix_match_team_stats_match_id", "match_team_stats", ["match_id"])
    op.create_index("ix_match_team_stats_team_id", "match_team_stats", ["team_id"])

    op.create_table(
        "player_match_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("minutes_played", sa.Integer(), nullable=True),
        sa.Column("goals", sa.Integer(), nullable=True),
        sa.Column("assists", sa.Integer(), nullable=True),
        sa.Column("yellow_cards", sa.Integer(), nullable=True),
        sa.Column("red_cards", sa.Integer(), nullable=True),
        sa.Column("shots_total", sa.Integer(), nullable=True),
        sa.Column("shots_on_target", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
    )
    op.create_index("ix_player_match_stats_match_id", "player_match_stats", ["match_id"])
    op.create_index("ix_player_match_stats_player_id", "player_match_stats", ["player_id"])
    op.create_index("ix_player_match_stats_team_id", "player_match_stats", ["team_id"])

    op.create_table(
        "bookmakers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(60), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.UniqueConstraint("external_id"),
    )

    op.create_table(
        "odds_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("bookmaker_id", sa.Integer(), sa.ForeignKey("bookmakers.id"), nullable=False),
        sa.Column("market", sa.String(60), nullable=False),
        sa.Column("selection", sa.String(40), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_closing_line", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_odds_snapshots_match_id", "odds_snapshots", ["match_id"])
    op.create_index("ix_odds_snapshots_bookmaker_id", "odds_snapshots", ["bookmaker_id"])
    op.create_index("ix_odds_snapshots_market", "odds_snapshots", ["market"])
    op.create_index("ix_odds_snapshots_captured_at", "odds_snapshots", ["captured_at"])

    op.create_table(
        "probability_estimates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("market", sa.String(60), nullable=False),
        sa.Column("selection", sa.String(40), nullable=False),
        sa.Column("probability_pct", sa.Float(), nullable=False),
        sa.Column("fair_odds", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(40), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_probability_estimates_match_id", "probability_estimates", ["match_id"])
    op.create_index("ix_probability_estimates_market", "probability_estimates", ["market"])
    op.create_index("ix_probability_estimates_computed_at", "probability_estimates", ["computed_at"])


def downgrade() -> None:
    op.drop_table("probability_estimates")
    op.drop_table("odds_snapshots")
    op.drop_table("bookmakers")
    op.drop_table("player_match_stats")
    op.drop_table("match_team_stats")
    op.drop_table("matches")
    op.drop_table("players")
    op.drop_table("teams")
    op.drop_table("leagues")
    sa.Enum(name="match_status").drop(op.get_bind(), checkfirst=True)
