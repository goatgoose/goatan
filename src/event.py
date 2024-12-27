from abc import ABC, abstractmethod

from src.player import Player
from src.piece import PieceType
from src.util import GameItem


class Event(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass


class Sendable(Event):
    @abstractmethod
    def serialize(self) -> dict:
        pass


class Receivable(Event):
    @staticmethod
    @abstractmethod
    def deserialize(_dict: dict):
        pass


class GameState(Sendable):
    def __init__(self, game):
        self.game = game

    @property
    def name(self) -> str:
        return "game_state"

    def serialize(self) -> dict:
        return self.game.serialize()


class NewTurn(Sendable):
    def __init__(self, active_player: Player):
        self.active_player = active_player

    @property
    def name(self) -> str:
        return "new_turn"

    def serialize(self) -> dict:
        return {
            "active_player": self.active_player.id,
        }


class Place(Receivable):
    def __init__(self, piece_type: PieceType, item: GameItem):
        self.piece_type = piece_type
        self.item = item

    @property
    def name(self) -> str:
        return "place"

    @staticmethod
    def deserialize(_dict: dict):
        return Place(
            PieceType(_dict["piece_type"]),
            _dict["item"],
        )
