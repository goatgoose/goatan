from typing import Dict
import random

from src.util import GameItem
from src.user import User


class PlayerManager:
    def __init__(self):
        self.finalized = False

        self._players: [Player] = []
        self._player_for_user: Dict[str, Player] = {}  # User id : Player

    def register_user(self, user_id: str):
        if self.player_for_user(user_id) is not None:
            return

        assert not self.finalized
        player = Player(user_id, f"Player {len(self._players) + 1}")
        self._players.append(player)
        self._player_for_user[user_id] = player
        return player

    def remove_player(self, player):
        assert not self.finalized
        self._players.remove(player)
        if player.user_id in self._player_for_user:
            self._player_for_user.pop(player.user_id)

    def get(self, index: int):
        return self._players[index]

    def player_for_user(self, user_id: str):
        return self._player_for_user.get(user_id)

    def finalize(self):
        random.shuffle(self._players)
        self.finalized = True

    def serialize(self):
        return {
            "players": [player.serialize() for player in self._players]
        }


class Player(GameItem):
    def __init__(self, user_id, name):
        super().__init__()

        self.user_id = user_id
        self.name = name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }
