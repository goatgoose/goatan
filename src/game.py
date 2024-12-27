import string
import random
import queue
from typing import Dict, Optional
from enum import Enum, auto
from flask_socketio import emit

from src.board import Board
from src.util import GameItem
from src.user import User
from src.player import PlayerManager, Player
from src.phase import GamePhase, Placement
from src import error
from src import event
from src.piece import PieceType, House, Road


class GameManager:
    def __init__(self):
        self.games: Dict[str, Goatan] = {}

    def create_game(self):
        game = Goatan()
        self.games[game.id] = game
        return game

    def get(self, id_: str):
        return self.games.get(id_)


class GameState(Enum):
    LOBBY = auto()
    PLACEMENT = auto()
    GAME = auto()
    FINISHED = auto()


class Goatan(GameItem):
    def __init__(self):
        super().__init__()

        self.players = PlayerManager()
        self.state = GameState.LOBBY

        self.board = None
        self.phase: Optional[GamePhase] = None

    @staticmethod
    def _generate_id():
        return "".join([
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(8)
        ])

    def emit_event(self, event_: event.Sendable):
        emit(
            event_.name,
            event_.serialize(),
            to=self.id,
        )

    def initialize(self, **kwargs):
        assert self.state == GameState.LOBBY

        radius = 2
        if "radius" in kwargs:
            radius = min(int(kwargs["radius"]), 10)
        self.board = Board.from_radius(radius)

        self.state = GameState.PLACEMENT
        self.players.finalize()
        self.phase = Placement(self.board, self.players)

    def end_turn(self, player: Player):
        print(f"end turn for {player.id}")

        if self.phase is None:
            raise error.InvalidState()

        if player != self.phase.active_player:
            raise error.InvalidAction(f"{player.id} is not the active player")

        self.phase.end_turn()
        self.emit_event(event.GameState(self))

        if self.phase.finished:
            print("phase finished")

    def place(self, player: Player, piece_type: PieceType, location_id: str):
        print(f"place {piece_type} for {player.id} on id {location_id}")

        if self.phase.active_player != player:
            raise error.InvalidAction(f"{player.id} is not the active player")

        piece = {
            PieceType.ROAD: Road(player),
            PieceType.HOUSE: House(player),
        }.get(piece_type)

        if piece is None:
            raise error.InvalidAction(f"Invalid piece type {piece_type}")

        self.phase.place_piece(piece, location_id)

        self.emit_event(event.GameState(self))

    def serialize(self):
        return {
            "board": self.board.serialize(),
            "hints": self.phase.serialize_hints(),
            "players": self.players.serialize(),
            "active_player": self.phase.active_player.id,
        }
