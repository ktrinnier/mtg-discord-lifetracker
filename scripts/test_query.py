from sqlalchemy.orm import Session
from app.db.session import engine
from app.db.models.player import PlayerModel

with Session(engine) as session:
    players = session.query(PlayerModel).all()

    for p in players:
        print(p.id, p.discord_user_id, p.display_name)