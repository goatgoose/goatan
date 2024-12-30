import string
import random
import queue
from typing import Dict, Optional
from enum import Enum, auto
from flask_socketio import emit

from src.board import Board
from src import board_generator
from src.util import GameItem
from src.user import User
from src.player import PlayerManager, Player
from src import phase
from src import error
from src import event
from src.piece import PieceType, House, Road
from src.resource import Transaction
from src import victory


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
        self.phases = []
        self.phase: Optional[phase.GamePhase] = None
        self.win_condition = victory.VictoryPoint(5)

    @staticmethod
    def _generate_id():
        return "".join([
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(8)
        ])

    def emit_event(self, event_: event.Sendable, to=None):
        if to is None:
            to = self.id
        emit(
            event_.name,
            event_.serialize(),
            to=to,
        )

    def initialize(self, **kwargs):
        assert self.state == GameState.LOBBY

        radius = 2
        if "radius" in kwargs:
            radius = min(int(kwargs["radius"]), 10)
        generator = board_generator.StandardGenerator(radius=radius)
        self.board = generator.generate()

        self.state = GameState.PLACEMENT
        self.players.finalize()
        self.phases = [
            phase.Placement(self.board, self.players),
            phase.Game(self.board, self.players, self.win_condition),
            phase.Finished(self.board, self.players, self.win_condition),
        ]
        self.phase = self.phases.pop(0)

    def end_turn(self, player: Player):
        print(f"end turn for {player.id}")

        if self.phase is None:
            raise error.InvalidState()

        if player != self.phase.active_player:
            raise error.InvalidAction(f"{player.id} is not the active player")

        self.phase.end_turn()
        self._synchronize_game_state()

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
        self._synchronize_game_state()

    def roll(self, player: Player):
        print(f"roll for {player.id}")

        if self.phase.active_player != player:
            raise error.InvalidAction(f"{player.id} is not the active player")

        self.phase.roll()
        self._synchronize_game_state()

    def bank_trade(self, player: Player, transaction: Transaction):
        print(f"bank trade for {player.id}")

        if self.phase.active_player != player:
            raise error.InvalidAction(f"{player.id} is not the active player")

        self.phase.bank_trade(transaction)
        self._synchronize_game_state()

    def _synchronize_game_state(self):
        if self.phase.finished:
            self.phase = self.phases.pop(0)
        self.emit_event(event.GameState(self))

    def serialize(self):
        return {
            "board": self.board.serialize(),
            "hints": self.phase.serialize_hints(),
            "players": self.players.serialize(),
            "active_player": self.phase.active_player.id,
            "roll": self.phase.roll_result,
            "expecting_roll": self.phase.expecting_roll,
            "phase": self.phase.name(),
            "bank_trades": self.phase.serialize_bank_trades(),
            "victor": victor.serialize() if (victor := self.win_condition.victor(self.board)) is not None else None
        }
