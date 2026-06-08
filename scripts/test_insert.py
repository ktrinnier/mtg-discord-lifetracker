from datetime import datetime, timezone

from app.db.session import engine
from app.db.models.player import PlayerModel
from sqlalchemy.orm import Session


with Session(engine) as session:
    player = PlayerModel(
        discord_user_id="123456789",
        display_name="Test Player",
        created_at=datetime.now(timezone.utc),
    )

    session.add(player)
    session.commit()

print("Inserted player")