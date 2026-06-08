from pydantic import BaseModel


class AddPlayerRequest(BaseModel):
    discord_user_id: str
    display_name: str

class AdjustLifeRequest(BaseModel):
    delta: int

class AdjustPoisonRequest(BaseModel):
    delta: int

class FinishGameRequest(BaseModel):
    winner_player_id: str