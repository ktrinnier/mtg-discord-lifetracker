from sqlalchemy.orm import Session

from app.db.session import engine
from app.services.game_service import GameService


with Session(engine) as session:
    service = GameService(session)

    leaderboard = service.get_leaderboard()

    for row in leaderboard:
        print(
            row["display_name"],
            row["wins"],
            row["losses"],
            f'{row["win_rate"]}%'
        )