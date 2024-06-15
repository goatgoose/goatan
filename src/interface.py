from flask_socketio import Namespace, emit, ConnectionRefusedError, join_room
from flask import request
from typing import Dict, Optional

from src.game import GameManager, Goatan
from src.user import User
from src.player import Player


class Authenticated:
    def __init__(self, game: Goatan, user: User):
        self.game: Goatan = game
        self.user: User = user

    @staticmethod
    def _authenticate(token: dict, games: GameManager):
        game_id = token.get("game")
        user_id = token.get("user")
        if game_id is None or user_id is None:
            return None

        game = games.get(game_id)
        if game is None:
            return None

        player = game.players.player_for_user(user_id)
        if player is None:
            return None

        return Authenticated(game, player)

    @staticmethod
    def from_token(token: dict, games: GameManager):
        auth = Authenticated._authenticate(token, games)
        if auth is None:
            raise ConnectionRefusedError("Invalid user for game")
        return auth


class GoatanNamespace(Namespace):
    NAMESPACE = "/goatan"

    def __init__(self, games: GameManager):
        self.games: GameManager = games

        super().__init__(self.NAMESPACE)

    def on_connect(self, auth):
        print("client connected")
        print(auth)
        # print(f"session id: {request.sid}")

        authenticated = Authenticated.from_token(auth, self.games)
        join_room(authenticated.game.id, namespace=self.NAMESPACE)

        emit("game_state", authenticated.game.serialize())
