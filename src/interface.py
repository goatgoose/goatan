from flask_socketio import Namespace, emit, ConnectionRefusedError
from typing import Dict

from src.game import GameManager, Goatan
from src.user import User


class GoatanNamespace(Namespace):
    def __init__(self, games: GameManager):
        self.games: GameManager = games

        super().__init__("/goatan")

    def on_connect(self, auth):
        print("client connected")
        print(auth)

        emit("game_state", "test")
