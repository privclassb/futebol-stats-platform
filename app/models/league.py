from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_football_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(60), unique=True)
    """Identificador curto usado internamente, ex: 'premier_league'."""
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    matches: Mapped[list["Match"]] = relationship(back_populates="league")
