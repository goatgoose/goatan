from typing import Dict

from src.util import GameItem


class PlayerManager:
    def __init__(self):
        self.players: Dict[str, Player] = {}

    def create_player(self):
        player = Player()
        self.players[player.id] = player
        return player

    def get(self, id_: str):
        return self.players.get(id_)


class Player(GameItem):
    def __init__(self):
        super().__init__()
