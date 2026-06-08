from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.session import engine
from app.db.dependencies import get_session
from app.services.game_service import GameService
from app.schemas.request import (
    AddPlayerRequest,
    AdjustLifeRequest,
    AdjustPoisonRequest,
    FinishGameRequest,
)

router = APIRouter()

@router.get("/leaderboard")
def get_leaderboard(
    session: Session = Depends(get_session),
):
    service = GameService(session)
    return service.get_leaderboard()
router = APIRouter()

@router.post("/games")
def create_game(
    guild_id: str,
    session: Session = Depends(get_session),
    ) -> dict:
        service = GameService(session)

        game = service.create_game(guild_id)

        return {
            "game_id": game.id,
            "guild_id": game.guild_id,
            "status": game.status.value,
        }

@router.post("/games/{game_id}/players")
def add_player_to_game(
    game_id: str,
    request: AddPlayerRequest,
    session: Session = Depends(get_session),
) -> dict:
    service = GameService(session)

    participant = service.add_player_to_game(
        game_id=game_id,
        discord_user_id=request.discord_user_id,
        display_name=request.display_name,
    )

    return {
        "participant_id": participant.id,
        "game_id": participant.game_id,
        "player_id": participant.player_id,
        "current_life": participant.current_life,
    }

@router.post("/games/{game_id}/start")
def start_game(
    game_id: str,
    session: Session = Depends(get_session),
) -> dict:
    service = GameService(session)

    game = service.start_game(game_id)

    return {
        "game_id": game.id,
        "status": game.status.value,
        "started_at": game.started_at,
    }

@router.post("/games/{game_id}/finish")
def finish_game(
    game_id: str,
    request: FinishGameRequest,
    session: Session = Depends(get_session)
) -> dict:
    service = GameService(session)

    game = service.finish_game(
        game_id=game_id,
        winner_player_id=request.winner_player_id,
    )

    return {
        "game_id": game.id,
        "status": game.status.value,
        "started_at": game.started_at,
        "finished_at": game.finished_at,
        "winner_player_id": request.winner_player_id,
    }

@router.post("/participants/{participant_id}/life")
def adjust_life(
    participant_id: str,
    request: AdjustLifeRequest,
    session: Session = Depends(get_session)
) -> dict:
    service = GameService(session)

    participant = service.adjust_life(
        participant_id=participant_id,
        delta=request.delta,
    )

    return {
        "participant_id": participant.id,
        "current_life": participant.current_life,
    }

@router.get("/games/{game_id}")
def get_game(
    game_id: str,
    session: Session = Depends(get_session)
) -> dict:
    service = GameService(session)

    try:
        return service.get_game_summary(game_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@router.get("/games/{game_id}/events")
def get_game_events(
    game_id: str,
    session: Session = Depends(get_session),
) -> list[dict]:
    service = GameService(session)

    try:
        return service.get_game_events(game_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@router.get("/games")
def get_games(
    status: str | None = None,
    session: Session = Depends(get_session),
) -> list[dict]:
    service = GameService(session)

    if status == "active":
        return service.get_active_games()

    if status == "finished":
        return service.get_finished_games()

    return []

@router.post("/participants/{participant_id}/poison")
def adjust_poison(
    participant_id: str,
    request: AdjustPoisonRequest,
    session: Session = Depends(get_session),
) -> dict:
    service = GameService(session)

    participant = service.adjust_poison(
        participant_id=participant_id,
        delta=request.delta,
    )

    return {
        "participant_id": participant.id,
        "poison_counters": participant.poison_counters,
    }