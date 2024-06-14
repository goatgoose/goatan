from flask import Flask, render_template, redirect, request, make_response
from flask_socketio import SocketIO, emit
from src.game import Goatan, GameManager
from src.interface import GoatanNamespace
from src.player import PlayerManager, Player

app = Flask(__name__)
socketio = SocketIO(app)

players = PlayerManager()
games = GameManager()
namespace = GoatanNamespace(games)
socketio.on_namespace(namespace)


@app.route("/")
def base():
    return render_template("index.html")


@app.route("/game/create")
def create_game():
    game = games.create_game()
    return redirect(f"/play/{game.id}")


@app.route("/play/<game_id>")
def play(game_id):
    game = games.get(game_id)
    if game is None:
        return f"Game not found: {game_id}", 400

    response = make_response(render_template("game.html", game_id=game_id))

    player_id = request.cookies.get("player_id")
    if not player_id:
        player = players.create_player()
        game.register_player(player)
        response.set_cookie("player_id", player.id)

    return response


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True, allow_unsafe_werkzeug=True)
