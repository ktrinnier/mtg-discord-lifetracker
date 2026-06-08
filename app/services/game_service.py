from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.game import GameModel
from app.domain.enums import GameStatus

from app.db.models.player import PlayerModel
from app.db.models.game_participant import GameParticipantModel

from app.db.models.game_event import GameEventModel
from app.domain.enums import EventType


class GameService:
    def __init__(self, session: Session):
        self.session = session

    def create_game(self, guild_id: str) -> GameModel:
        game = GameModel(
            guild_id=guild_id,
            status=GameStatus.CREATED,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(game)
        self.session.commit()
        self.session.refresh(game)

        return game

    def add_player_to_game(
        self,
        game_id: str,
        discord_user_id: str,
        display_name: str,
    ) -> GameParticipantModel:

        game = (
            self.session.query(GameModel)
            .filter_by(id=game_id)
            .first()
        )

        if not game:
            raise ValueError(f"Game not found: {game_id}")

        if game.status != GameStatus.CREATED:
            raise ValueError(f"Cannot add player to game in status {game.status}")

        # 1. Find or create player
        player = (
            self.session.query(PlayerModel)
            .filter_by(discord_user_id=discord_user_id)
            .first()
        )

        if not player:
            player = PlayerModel(
                discord_user_id=discord_user_id,
                display_name=display_name,
                created_at=datetime.now(timezone.utc),
            )
            self.session.add(player)
            self.session.flush()  # gets player.id without commit

        # 2. Create participant link
        participant = GameParticipantModel(
            game_id=game_id,
            player_id=player.id,
            starting_life=40,
            current_life=40,
        )

        self.session.add(participant)
        self.session.commit()
        self.session.refresh(participant)

        return participant

    def adjust_life(
        self,
        participant_id: str,
        delta: int,
    ) -> GameParticipantModel:
        participant = (
            self.session.query(GameParticipantModel)
            .filter_by(id=participant_id)
            .first()
        )

        if not participant:
            raise ValueError(f"Participant not found: {participant_id}")

        participant.current_life += delta

        if (
            participant.current_life <= 0
            and participant.eliminated_at is None
        ):
            participant.eliminated_at = datetime.now(timezone.utc)

            elimination_event = GameEventModel(
                game_id=participant.game_id,
                player_id=participant.player_id,
                event_type=EventType.PLAYER_ELIMINATED,
                payload={
                    "reason": "life_total",
                },
                created_at=datetime.now(timezone.utc),
            )

            self.session.add(elimination_event)

        event = GameEventModel(
            game_id=participant.game_id,
            player_id=participant.player_id,
            event_type=EventType.LIFE_CHANGED,
            payload={"delta": delta},
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(event)
        self.session.commit()
        self.session.refresh(participant)

        return participant

    def adjust_poison(
        self,
        participant_id: str,
        delta: int,
    ) -> GameParticipantModel:
        participant = (
            self.session.query(GameParticipantModel)
            .filter_by(id=participant_id)
            .first()
        )

        if not participant:
            raise ValueError(f"Participant not found: {participant_id}")

        participant.poison_counters += delta

        if (
            participant.poison_counters >= 10
            and participant.eliminated_at is None
        ):
            participant.eliminated_at = datetime.now(timezone.utc)
            elimination_event = GameEventModel(
                game_id=participant.game_id,
                player_id=participant.player_id,
                event_type=EventType.PLAYER_ELIMINATED,
                payload={
                    "reason": "poison_counters",
                },
                created_at=datetime.now(timezone.utc),
            )

            self.session.add(elimination_event)

        event = GameEventModel(
            game_id=participant.game_id,
            player_id=participant.player_id,
            event_type=EventType.POISON_CHANGED,
            payload={"delta": delta},
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(event)
        self.session.commit()
        self.session.refresh(participant)

        return participant

    def get_game_participants(
        self,
        game_id: str,
    ) -> list[GameParticipantModel]:
        return (
            self.session.query(GameParticipantModel)
            .filter_by(game_id=game_id)
            .all()
        )

    def start_game(self, game_id: str) -> GameModel:
        game = (
            self.session.query(GameModel)
            .filter_by(id=game_id)
            .first()
        )

        if not game:
            raise ValueError(f"Game not found: {game_id}")

        if game.status != GameStatus.CREATED:
            raise ValueError(
                f"Cannot start game in status {game.status}"
            )

        game.status = GameStatus.ACTIVE
        game.started_at = datetime.now(timezone.utc)

        event = GameEventModel(
            game_id=game.id,
            event_type=EventType.GAME_STARTED,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(event)
        self.session.commit()
        self.session.refresh(game)

        return game

    def finish_game(self, game_id, winner_player_id) ->  GameModel:
        game = (
            self.session.query(GameModel)
            .filter_by(id=game_id)
            .first()
        )

        if not game:
            raise ValueError(f"Game not found: {game_id}")

        if game.status != GameStatus.ACTIVE:
            raise ValueError(
                f"Cannot finish game in status {game.status}"
            )

        game.status = GameStatus.FINISHED
        game.finished_at = datetime.now(timezone.utc)

        event = GameEventModel(
            game_id=game.id,
            payload = {
            "winner_player_id": winner_player_id,
            },
            player_id=winner_player_id,
            event_type=EventType.GAME_FINISHED,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(event)
        self.session.commit()
        self.session.refresh(game)

        return game

    def get_game_summary(self, game_id: str) -> dict:
        game = (
            self.session.query(GameModel)
            .filter_by(id=game_id)
            .first()
        )

        if not game:
            raise ValueError(f"Game not found: {game_id}")

        participants = self.get_game_participants(game_id)

        finish_event = (
            self.session.query(GameEventModel)
            .filter_by(
                game_id=game_id,
                event_type=EventType.GAME_FINISHED,
            )
            .first()
        )

        winner_player_id = None
        if finish_event and finish_event.payload:
            winner_player_id = finish_event.payload.get("winner_player_id")

        return {
            "game_id": game.id,
            "first_blood": self.get_first_blood(game_id),
            "status": game.status.value,
            "created_at": game.created_at,
            "started_at": game.started_at,
            "finished_at": game.finished_at,
            "winner_player_id": winner_player_id,
            "participants": [
                {
                    "player_id": p.player_id,
                    "display_name": p.player.display_name,
                    "life": p.current_life,
                    "poison_counters": p.poison_counters,
                    "participant_id": p.id,
                    "is_eliminated": p.eliminated_at is not None,
                    "eliminated_at": p.eliminated_at,
                }
                for p in participants
            ],
        }

    def get_player_stats(self, player_id: str) -> dict:
        wins = (
            self.session.query(GameEventModel)
            .filter_by(
                player_id=player_id,
                event_type=EventType.GAME_FINISHED,
            )
            .count()
        )

        participations = (
            self.session.query(GameParticipantModel)
            .filter_by(player_id=player_id)
            .count()
        )

        losses = participations - wins
        win_rate = (
            round((wins / participations) * 100, 2)
            if participations > 0
            else 0.0
        )

        return {
            "player_id": player_id,
            "games_played": participations,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate
        }
    
    def get_player_by_discord_id(
        self,
        discord_user_id: str,
    ) -> PlayerModel | None:
        return (
            self.session.query(PlayerModel)
            .filter_by(discord_user_id=discord_user_id)
            .first()
        )

    def get_leaderboard(self) -> list[dict]:
        players = self.session.query(PlayerModel).all()

        leaderboard = []

        for player in players:
            stats = self.get_player_stats(player.id)

            leaderboard.append(
                {
                    "player_id": player.id,
                    "discord_user_id": player.discord_user_id,
                    "display_name": player.display_name,
                    "games_played": stats["games_played"],
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "win_rate": stats["win_rate"],
                }
            )

        return sorted(
            leaderboard,
            key=lambda row: (row["wins"], row["win_rate"]),
            reverse=True,
        )

    def get_game_events(self, game_id: str) -> list[dict]:
        events = (
            self.session.query(GameEventModel)
            .filter_by(game_id=game_id)
            .order_by(GameEventModel.created_at)
            .all()
        )
        game = (
            self.session.query(GameModel)
            .filter_by(id=game_id)
            .first()
        )

        if not game:
            raise ValueError(f"Game not found: {game_id}")

        return [
            {
                "event_id": event.id,
                "game_id": event.game_id,
                "player_id": event.player_id,
                "event_type": event.event_type.value,
                "payload": event.payload,
                "created_at": event.created_at,
            }
            for event in events
        ]

    def get_active_games(self) -> list[dict]:
        games = (
            self.session.query(GameModel)
            .filter_by(status=GameStatus.ACTIVE)
            .all()
        )

        return [
            self.get_game_summary(game.id)
            for game in games
        ]

    def get_finished_games(self) -> list[dict]:
        games = (
            self.session.query(GameModel)
            .filter_by(status=GameStatus.FINISHED)
            .all()
        )

        return [
            self.get_game_summary(game.id)
            for game in games
        ]

    def get_first_blood(self, game_id: str) -> dict | None:
        events = (
            self.session.query(GameEventModel)
            .filter_by(
                game_id=game_id,
                event_type=EventType.LIFE_CHANGED,
            )
            .order_by(GameEventModel.created_at)
            .all()
        )

        for event in events:
            if not event.payload:
                continue

            delta = event.payload.get("delta")

            if delta is not None and delta < 0:
                player = (
                    self.session.query(PlayerModel)
                    .filter_by(id=event.player_id)
                    .first()
                )

                return {
                    "player_id": event.player_id,
                    "display_name": player.display_name if player else None,
                    "delta": delta,
                    "created_at": event.created_at,
                }

        return None

    def eliminate_player(
        self,
        participant_id: str,
    ) -> GameParticipantModel:
        participant = (
            self.session.query(GameParticipantModel)
            .filter_by(id=participant_id)
            .first()
        )

        if not participant:
            raise ValueError(f"Participant not found: {participant_id}")

        participant.eliminated_at = datetime.now(timezone.utc)

        event = GameEventModel(
            game_id=participant.game_id,
            player_id=participant.player_id,
            event_type=EventType.PLAYER_ELIMINATED,
            payload={
                "participant_id": participant.id,
            },
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(event)
        self.session.commit()
        self.session.refresh(participant)

        return participant