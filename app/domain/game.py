from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import GameStatus


@dataclass
class Game:
    id: UUID
    guild_id: str

    status: GameStatus

    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None