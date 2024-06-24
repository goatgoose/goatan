from abc import ABC, abstractmethod
from enum import Enum

from src.player import Player


class PieceType(Enum):
    HOUSE = 0
    ROAD = 1


class Piece(ABC):
    def __init__(self):
        pass


class PlayerPiece(Piece):
    def __init__(self, player: Player):
        super().__init__()

        self.player = player


class Settlement(PlayerPiece):
    def __init__(self, player: Player):
        super().__init__(player)


class House(Settlement):
    def __init__(self, player: Player):
        super().__init__(player)


class Road(PlayerPiece):
    def __init__(self, player: Player):
        super().__init__(player)
