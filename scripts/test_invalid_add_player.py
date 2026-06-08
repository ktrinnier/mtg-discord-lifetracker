from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    service.start_game(game.id)

    try:
        service.add_player_to_game(
            game_id=game.id,
            discord_user_id="333333333",
            display_name="Charlie",
        )
    except ValueError as e:
        print(e)