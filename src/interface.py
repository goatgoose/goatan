from flask_socketio import Namespace, emit, ConnectionRefusedError
from typing import Dict

from src.game import GameManager, Goatan
from src.player import Player


class AuthenticatedPlayer:
    def __init__(self, game: Goatan, player: Player):
        self.game: Goatan = game
        self.player: Player = player

    @staticmethod
    def _authenticate(game_id, player_id, game_manager):
        if game_id is None or player_id is None:
            return None

        game = game_manager.get(game_id)
        if game is None:
            return None

        player = game.players.get(player_id)
        if player is None:
            return None

        return AuthenticatedPlayer(game, player)

    @staticmethod
    def authenticate(game_id, player_id, game_manager):
        authenticated = AuthenticatedPlayer._authenticate(game_id, player_id, game_manager)
        if authenticated is None:
            message = f"Invalid player ({player_id}) for game ({game_id})"
            print(message)
            raise ConnectionRefusedError(message)
        return authenticated


class GoatanNamespace(Namespace):
    def __init__(self, games: GameManager):
        self.games: GameManager = games

        super().__init__("/goatan")

    def on_connect(self, auth):
        print("client connected")
        print(auth)

        authenticated = AuthenticatedPlayer.authenticate(
            auth.get("game"),
            auth.get("player"),
            self.games,
        )

        emit("game_state", authenticated.game.serialize())
