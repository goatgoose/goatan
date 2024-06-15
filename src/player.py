from typing import Dict

from src.util import GameItem
from src.user import User


class PlayerManager:
    def __init__(self):
        self._players: Dict[str, Player] = {}
        self._player_for_user: Dict[str, Player] = {}  # User id : Player id

    def register_user(self, user: User):
        player = Player()
        self._players[player.id] = player
        self._player_for_user[user.id] = player
        return player

    def get(self, id_: str):
        return self._players.get(id_)

    def player_for_user(self, user_id: str):
        return self._player_for_user.get(user_id)


class Player(GameItem):
    def __init__(self):
        super().__init__()
