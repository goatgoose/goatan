from abc import ABC, abstractmethod
from enum import Enum

from src.player import Player


class PieceType(Enum):
    HOUSE = "house"
    ROAD = "road"


class Piece(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def type(self) -> PieceType:
        pass


class PlayerPiece(Piece, ABC):
    def __init__(self, player: Player):
        super().__init__()
        self._player = player

    @property
    def player(self) -> Player:
        return self._player


class Settlement(PlayerPiece, ABC):
    def __init__(self, player: Player):
        super().__init__(player)

    @property
    @abstractmethod
    def gather_amount(self) -> int:
        pass


class House(Settlement):
    def __init__(self, player: Player):
        super().__init__(player)

    @property
    def type(self):
        return PieceType.HOUSE

    @property
    def gather_amount(self) -> int:
        return 1


class Road(PlayerPiece):
    def __init__(self, player: Player):
        super().__init__(player)

    @property
    def type(self) -> PieceType:
        return PieceType.ROAD
