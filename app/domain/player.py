from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Player:
    id: UUID
    discord_user_id: str
    display_name: str
    created_at: datetime