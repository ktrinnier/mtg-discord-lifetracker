from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import engine
from app.db.dependencies import get_session
from app.services.game_service import GameService

router = APIRouter()

@router.get("/leaderboard")
def get_leaderboard(
    session: Session = Depends(get_session),
) -> list[dict]:
    service = GameService(session)

    return service.get_leaderboard()

@router.get("/players/{discord_user_id}/stats")
def get_player_stats(
    discord_user_id: str,
    session: Session = Depends(get_session)
) -> dict:
    service = GameService(session)

    player = service.get_player_by_discord_id(
        discord_user_id
    )

    if not player:
        raise HTTPException(
        status_code=404,
        detail="Player not found",
    )

    return service.get_player_stats(
        player.id,
    )