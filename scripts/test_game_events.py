from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    p1 = service.add_player_to_game(
        game.id,
        "111111111",
        "Alice",
    )

    p2 = service.add_player_to_game(
        game.id,
        "222222222",
        "Bob",
    )

    service.start_game(game.id)
    service.adjust_life(p2.id, -5)

    service.finish_game(
        game.id,
        p1.player_id,
    )

    events = service.get_game_events(game.id)

    for event in events:
        print(event)