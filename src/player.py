from typing import Dict

from src.util import GameItem
from src.user import User


class PlayerManager:
    def __init__(self):
        self._players: Dict[str, Player] = {}
        self._player_for_user: Dict[str, Player] = {}  # User id : Player

    def register_user(self, user_id: str):
        if self.player_for_user(user_id) is not None:
            return

        player = Player(user_id)
        self._players[player.id] = player
        self._player_for_user[user_id] = player
        return player

    def remove_player(self, player):
        if player.id in self._players:
            self._players.pop(player.id)
        if player.user_id in self._player_for_user:
            self._player_for_user.pop(player.user_id)

    def get(self, id_: str):
        return self._players.get(id_)

    def player_for_user(self, user_id: str):
        return self._player_for_user.get(user_id)

    def serialize_player_list(self):
        return [player_id for player_id in self._players.keys()]


class Player(GameItem):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
