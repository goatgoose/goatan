import string
import random
import queue
from typing import Dict

from src.board import Board
from src.util import GameItem
from src.user import User


class GameManager:
    def __init__(self):
        self.games: Dict[str, Goatan] = {}

    def create_game(self):
        game = Goatan()
        self.games[game.id] = game
        return game

    def get(self, id_: str):
        return self.games.get(id_)


class Goatan(GameItem):
    def __init__(self):
        super().__init__()

        self.players = {}  # id : player
        self.board = Board.from_radius(1)

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
