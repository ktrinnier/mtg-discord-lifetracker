from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    participant = service.add_player_to_game(
        game_id=game.id,
        discord_user_id="123456789",
        display_name="Alice",
    )

    print(participant.id, participant.player_id, participant.game_id)