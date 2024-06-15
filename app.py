from flask import Flask, render_template, redirect, request, make_response
from flask_socketio import SocketIO, emit
from src.game import Goatan, GameManager
from src.interface import GoatanNamespace
from src.user import UserManager, User

app = Flask(__name__)
socketio = SocketIO(app)

users = UserManager()
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

    user_id = request.cookies.get("user_id")
    if user_id is None or users.get(user_id) is None:
        user = users.create_user()
        user_id = user.id
        response.set_cookie("user_id", user_id)

    return response


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True, allow_unsafe_werkzeug=True)
