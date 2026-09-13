from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bookmaker(Base):
    """Uma casa de apostas (ex: Bet365, Pinnacle) cuja odds guardamos."""

    __tablename__ = "bookmakers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(60), unique=True)
    """Id do bookmaker na fonte de odds (varia por provedor)."""
    name: Mapped[str] = mapped_column(String(80))
