from abc import ABC, abstractmethod

from src.player import Player


class Event(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def serialize(self) -> dict:
        pass


class NewTurn(Event):
    def __init__(self, active_player: Player):
        self.active_player = active_player

    @property
    def name(self) -> str:
        return "new_turn"

    def serialize(self) -> dict:
        return {
            "active_player": self.active_player.id,
        }


