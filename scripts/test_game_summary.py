from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild")

    p1 = service.add_player_to_game(
        game_id=game.id,
        discord_user_id="111111111",
        display_name="Alice",
    )

    p2 = service.add_player_to_game(
        game_id=game.id,
        discord_user_id="222222222",
        display_name="Bob",
    )
    service.start_game(game.id)
    service.adjust_life(p2.id, -12)

    service.finish_game(
        game_id=game.id,
        winner_player_id=p1.player_id,
    )

    summary = service.get_game_summary(game.id)

    print(summary)