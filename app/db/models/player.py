from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    discord_user_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(datetime.timezone),
    )

    participants = relationship(
        "GameParticipantModel",
        back_populates="player",
    )