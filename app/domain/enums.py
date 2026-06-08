from enum import Enum


class GameStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    FINISHED = "finished"


class EventType(str, Enum):
    GAME_CREATED = "game_created"
    GAME_STARTED = "game_started"
    LIFE_CHANGED = "life_changed"
    POISON_CHANGED = "poison_changed"
    PLAYER_ELIMINATED = "player_eliminated"
    GAME_FINISHED = "game_finished"
    PLAYER_JOINED = "player_joined"