from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    game = service.create_game("test-guild-123")

    print(game.id, game.guild_id, game.status)