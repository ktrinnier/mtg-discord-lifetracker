from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class GameParticipantModel(Base):
    __tablename__ = "game_participants"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    game_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("games.id"),
        nullable=False,
    )

    player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("players.id"),
        nullable=False,
    )

    starting_life: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=40,
    )

    current_life: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=40,
    )

    poison_counters: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    placement: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    commander_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    eliminated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    player = relationship(
        "PlayerModel",
        back_populates="participants",
    )