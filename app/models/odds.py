from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OddsSnapshot(Base):
    """Uma cotação de odds capturada em um instante, de uma casa, para um mercado.

    Guardamos SNAPSHOTS (não só "a odd atual") de propósito: é isso que permite
    comparar odds entre casas num mesmo momento (value bet / surebet) e comparar
    a odd de abertura com a odd de fechamento do jogo (CLV - Closing Line Value).
    """

    __tablename__ = "odds_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    bookmaker_id: Mapped[int] = mapped_column(ForeignKey("bookmakers.id"), index=True)

    market: Mapped[str] = mapped_column(String(60), index=True)
    """Ex: 'match_winner', 'over_under_2_5', 'both_teams_to_score'."""
    selection: Mapped[str] = mapped_column(String(40))
    """Ex: 'home', 'draw', 'away', 'over', 'under', 'yes', 'no'."""

    price: Mapped[float] = mapped_column(Float)
    """Odd decimal (ex: 2.10)."""

    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_closing_line: Mapped[bool] = mapped_column(default=False)
    """Marca a última cotação capturada antes do apito inicial (base do CLV)."""

    match: Mapped["Match"] = relationship(back_populates="odds_snapshots")
    bookmaker: Mapped["Bookmaker"] = relationship()


class ProbabilityEstimate(Base):
    """Nossa própria estimativa de probabilidade/odd justa para um mercado.

    Calculada pelo módulo de probabilidade (fase 2/3) a partir das odds de
    múltiplas casas + estatísticas históricas. Guardar o histórico de estimativas
    (não só a mais recente) permite comparar a evolução da nossa previsão.
    """

    __tablename__ = "probability_estimates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)

    market: Mapped[str] = mapped_column(String(60), index=True)
    selection: Mapped[str] = mapped_column(String(40))

    probability_pct: Mapped[float] = mapped_column(Float)
    """Probabilidade estimada, de 0 a 100."""
    fair_odds: Mapped[float] = mapped_column(Float)
    """Odd justa correspondente (100 / probability_pct)."""

    model_version: Mapped[str] = mapped_column(String(40))
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    match: Mapped["Match"] = relationship()
