import pprint
from flask_socketio import Namespace, emit, ConnectionRefusedError, join_room, send
from flask import request
from typing import Dict, Optional
from abc import ABCMeta, abstractmethod

from src.game import GameManager, Goatan, GameState
from src.user import User
from src.player import Player
from src import error
from src import event


class Authenticated:
    def __init__(self, game: Goatan, player: Player):
        self.game: Goatan = game
        self.player: Player = player

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

    def __str__(self):
        return f"{self.game}, {self.player}"

    def __repr__(self):
        return str(self)


class AuthenticatedNamespace(Namespace, metaclass=ABCMeta):
    def __init__(self, games: GameManager):
        self.games: GameManager = games
        self.auths: Dict[str, Authenticated] = {}  # sid : auth

        super().__init__(self.namespace_str)

    @property
    @abstractmethod
    def namespace_str(self) -> str:
        pass

    def register_socket(self, sid: str, token: dict) -> Authenticated:
        auth = Authenticated.from_token(token, self.games)
        self.auths[sid] = auth
        return auth

    def unregister_socket(self, sid: str):
        if sid in self.auths:
            self.auths.pop(sid)

    def get_auth(self, sid: str) -> Authenticated:
        return self.auths.get(sid)


class GoatanNamespace(AuthenticatedNamespace):
    def __init__(self, games: GameManager):
        super().__init__(games)

    @property
    def namespace_str(self) -> str:
        return "/goatan"

    def on_connect(self, token):
        print("client connected")
        print(token)
        # print(f"session id: {request.sid}")

        auth = self.register_socket(request.sid, token)
        join_room(auth.game.id, namespace=self.namespace)

        auth.game.emit_event(event.PlayerInfo(auth.player), to=request.sid)
        auth.game.emit_event(event.GameState(auth.game))

    def on_disconnect(self):
        self.unregister_socket(request.sid)

    def on_end_turn(self):
        auth = self.get_auth(request.sid)

        try:
            auth.game.end_turn(auth.player)
        except error.InvalidAction as e:
            # TODO: return message
            print(e.message())

    def on_place(self, _dict):
        auth = self.get_auth(request.sid)
        place = event.Place.deserialize(_dict)
        try:
            auth.game.place(auth.player, place.piece_type, place.item)
        except error.InvalidAction as e:
            # TODO: return message
            print(e.message())


class LobbyNamespace(AuthenticatedNamespace):
    def __init__(self, games: GameManager):
        super().__init__(games)

    @property
    def namespace_str(self) -> str:
        return "/lobby"

    def _create_player(self, token):
        game_id = token.get("game")
        user_id = token.get("user")
        if game_id is None or user_id is None:
            return None

        game = self.games.get(game_id)
        if game is None:
            return None

        player = game.players.player_for_user(user_id)
        if player is None:
            game.players.register_user(user_id)

    def on_connect(self, token):
        print("client connected to lobby")
        print(token, request.sid)

        self._create_player(token)
        auth = self.register_socket(request.sid, token)
        join_room(auth.game.id, namespace=self.namespace)

        emit("player_id", {"player_id": auth.player.id})

        emit(
            "player_update",
            auth.game.players.serialize(),
            to=auth.game.id,
        )

    def on_disconnect(self):
        print("client disconnected from lobby")

        auth = self.get_auth(request.sid)
        if auth is None:
            return
        if auth.game.state != GameState.LOBBY:
            return

        auth.game.players.remove_player(auth.player)
        self.unregister_socket(request.sid)

        emit(
            "player_update",
            auth.game.players.serialize(),
            to=auth.game.id,
        )

    def on_game_init(self, settings):
        print("game init")

        init_args = {}
        for setting in settings:
            init_args[setting["name"]] = setting["value"]
        pprint.pprint(init_args)

        auth = self.get_auth(request.sid)
        auth.game.initialize(**init_args)

        emit(
            "game_start",
            {
                "route": f"/game/play/{auth.game.id}"
            },
            to=auth.game.id,
        )
