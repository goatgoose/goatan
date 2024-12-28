from typing import Dict, Optional
import random
from enum import Enum

from src.util import GameItem
from src.user import User
from src.resource import ResourceType


class PlayerColor(Enum):
    WHITE = "white"
    BLACK = "black"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"


class Player(GameItem):
    def __init__(self, user_id, name, color: PlayerColor):
        super().__init__()

        self.user_id = user_id
        self.name = name
        self.color = color
        self.resources = {resource_type: 0 for resource_type in ResourceType}

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color.value,
            "resources": {resource_type.value: count for resource_type, count in self.resources.items()}
        }

    def give(self, resource_type: ResourceType):
        self.resources[resource_type] += 1


class PlayerManager:
    class Iterator:
        def __init__(self, players: [Player]):
            self._players = players
            self.index = 0

        def __next__(self):
            if self.index < len(self._players):
                player = self._players[self.index]
                self.index += 1
                return player
            else:
                raise StopIteration

    def __init__(self):
        self.finalized = False

        self._colors = [color for color in PlayerColor]
        random.shuffle(self._colors)

        self._players: [Player] = []
        self._player_for_user: Dict[str, Player] = {}  # User id : Player

    def register_user(self, user_id: str):
        if self.player_for_user(user_id) is not None:
            return

        assert not self.finalized
        assert len(self._colors) > 0

        player = Player(user_id, f"Player {len(self._players) + 1}", self._colors.pop())
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
            "players": [player.serialize() for player in self._players],
            "player_map": {player.id: player.serialize() for player in self._players}
        }

    def __len__(self):
        return len(self._players)

    def __iter__(self):
        return PlayerManager.Iterator(self._players)
