from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict

from src.player import Player
from src.resource import ResourceType


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

    @staticmethod
    @abstractmethod
    def cost() -> Dict[ResourceType, int]:
        pass


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

    @staticmethod
    def cost() -> Dict[ResourceType, int]:
        return {
            ResourceType.WOOD: 1,
            ResourceType.WHEAT: 1,
            ResourceType.SHEEP: 1,
            ResourceType.BRICK: 1,
        }


class Road(PlayerPiece):
    def __init__(self, player: Player):
        super().__init__(player)

    @property
    def type(self) -> PieceType:
        return PieceType.ROAD

    @staticmethod
    def cost() -> Dict[ResourceType, int]:
        return {
            ResourceType.WOOD: 1,
            ResourceType.BRICK: 1,
        }
