import string
import random
import queue
from typing import Dict
from enum import Enum, auto

from src.board import Board
from src.util import GameItem
from src.user import User
from src.player import PlayerManager, Player


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

    @staticmethod
    def _generate_id():
        return "".join([
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(8)
        ])

    def serialize(self):
        return {
            "board": self.board.serialize(),
        }

    def initialize(self, **kwargs):
        assert self.state == GameState.LOBBY

        radius = 2
        if "radius" in kwargs:
            radius = min(int(kwargs["radius"]), 10)
        self.board = Board.from_radius(radius)

        self.state = GameState.PLACEMENT
