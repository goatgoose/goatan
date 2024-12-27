from flask import Flask, render_template, redirect, request, make_response
from flask_socketio import SocketIO, emit
from src.game import Goatan, GameManager, GameState
from src.interface import GoatanNamespace, LobbyNamespace
from src.user import UserManager, User

app = Flask(__name__)
socketio = SocketIO(app)

users = UserManager()
games = GameManager()

game_namespace = GoatanNamespace(games)
socketio.on_namespace(game_namespace)

lobby_namespace = LobbyNamespace(games)
socketio.on_namespace(lobby_namespace)


def error_page(message):
    return make_response(render_template("error.html", message=message))


@app.route("/")
def base():
    return render_template("index.html")


@app.route("/game/create")
def create_game():
    game = games.create_game()
    return redirect(f"/game/join/{game.id}")


@app.route("/game/join/<game_id>")
def join_game(game_id):
    game = games.get(game_id)
    if game is None:
        return error_page(f"Game not found: {game_id}")

    if game.state == GameState.LOBBY:
        return redirect(f"/game/lobby/{game.id}")
    else:
        return redirect(f"/game/play/{game.id}")


@app.route("/game/lobby/<game_id>")
def lobby(game_id):
    game = games.get(game_id)
    if game is None:
        return error_page(f"Game not found: {game_id}")

    if game.state != GameState.LOBBY:
        return error_page(f"Invalid game state: {game.state.name}")

    response = make_response(render_template("lobby.html", game_id=game_id))

    user_id = request.cookies.get("user_id")
    if user_id is None or users.get(user_id) is None:
        user = users.create_user()
        response.set_cookie("user_id", user.id)

    return response


@app.route("/game/play/<game_id>")
def play(game_id):
    game = games.get(game_id)
    if game is None:
        return error_page(f"Game not found: {game_id}")

    if game.state == GameState.LOBBY:
        return error_page(f"Invalid game state: {game.state.name}")

    user_id = request.cookies.get("user_id")
    if user_id is None or users.get(user_id) is None:
        return error_page(f"User not found: {user_id}")

    player = game.players.player_for_user(user_id)
    if player is None:
        return error_page(f"User did not join the game: {user_id}")

    player_list = game.players.serialize()["players"]
    for player_dict in player_list:
        if player_dict["id"] == player.id:
            player_dict["name"] = player_dict["name"] + " (you)"
            break

    return make_response(render_template(
        "game.html",
        game_id=game_id,
        players=player_list,
    ))


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True, allow_unsafe_werkzeug=True)
