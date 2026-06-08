from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy knows they exist
from app.db.models.player import PlayerModel
from app.db.models.game import GameModel
from app.db.models.game_participant import GameParticipantModel
from app.db.models.game_event import GameEventModel

Base.metadata.create_all(engine)