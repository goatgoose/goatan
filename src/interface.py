from flask_socketio import Namespace, emit
from typing import Dict

from src.game import GameManager


class GoatanNamespace(Namespace):
    def __init__(self, games: GameManager):
        self.games: GameManager = games

        super().__init__("/goatan")

    def on_connect(self, auth):
        print("client connected")
        print(auth)
        emit("response", {"data": "Connected"})
        return "test data"
