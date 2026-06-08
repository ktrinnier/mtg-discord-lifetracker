from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class GameParticipant:
    id: UUID

    game_id: UUID
    player_id: UUID

    starting_life: int = 40
    placement: int | None = None

    eliminated_at: datetime | None = None

    commander_name: str | None = None