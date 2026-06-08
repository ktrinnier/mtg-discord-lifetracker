from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import EventType


@dataclass
class GameEvent:
    id: UUID

    game_id: UUID
    player_id: UUID

    event_type: EventType

    payload: dict | None = None

    metadata: dict | None = None

    created_at: datetime | None = None