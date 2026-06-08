from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    try:
        service.finish_game(
            game.id,
            "some-player-id",
        )
    except ValueError as e:
        print(e)