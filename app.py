from flask import Flask, render_template, redirect, request, make_response
from flask_socketio import SocketIO, emit
from src.game import Goatan, Player, GameManager
from src.interface import GoatanNamespace

app = Flask(__name__)
socketio = SocketIO(app)


games = GameManager()
namespace = GoatanNamespace(games)
socketio.on_namespace(namespace)


@app.route("/")
def base():
    return render_template("index.html")


@app.route("/game/create")
def create_game():
    game_id = games.create_game()
    return redirect(f"/play/{game_id}")


@app.route("/play/<game_id>")
def play(game_id):
    game = games.get(game_id)
    if game is None:
        return f"Game not found: {game_id}", 400

    response = make_response(render_template("game.html", game_id=game_id))

    player_id = request.cookies.get("player_id")
    if not player_id:
        player_id = Player.generate_id()
        response.set_cookie("player_id", player_id)

    if player_id not in game.players:
        game.register_player(player_id)

    return response


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True, allow_unsafe_werkzeug=True)
