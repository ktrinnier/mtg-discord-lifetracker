from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    participant = service.add_player_to_game(
        game_id=game.id,
        discord_user_id="987654321",
        display_name="Bob",
    )

    updated = service.adjust_life(
        participant_id=participant.id,
        delta=-5,
    )

    print(updated.current_life)