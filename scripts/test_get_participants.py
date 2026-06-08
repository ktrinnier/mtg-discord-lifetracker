from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    service.add_player_to_game(
        game_id=game.id,
        discord_user_id="111111111",
        display_name="Alice",
    )

    service.add_player_to_game(
        game_id=game.id,
        discord_user_id="222222222",
        display_name="Bob",
    )

    participants = service.get_game_participants(game.id)

    for participant in participants:
        print(
            f"participant_id={participant.id} "
            f"player_id={participant.player_id} "
            f"life={participant.current_life}"
        )