from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    service.add_player_to_game(
        game.id,
        "111111111",
        "Alice",
    )

    participants = service.get_game_participants(game.id)

    for p in participants:
        print(p.player.display_name)