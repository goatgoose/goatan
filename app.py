import logging

import flask
from flask import Flask, render_template, redirect, request, make_response
from flask_socketio import SocketIO, emit
from game import Goatan, Player

app = Flask(__name__)
socketio = SocketIO(app)


games: dict[str, Goatan] = {}  # id : game


@app.route("/")
def base():
    return render_template("index.html")


@app.route("/game/create")
def create_game():
    goatan = Goatan()
    game_id = goatan.id
    games[game_id] = goatan

    return redirect(f"/play/{game_id}")


@app.route("/play/<game_id>")
def play(game_id):
    if game_id not in games:
        return f"Game not found: {game_id}", 400
    game = games[game_id]

    response = make_response(render_template("game.html", game_id=game_id))

    player_id = request.cookies.get("player_id")
    if not player_id:
        player_id = Player.generate_id()
        response.set_cookie("player_id", player_id)

    if player_id not in game.players:
        game.register_player(player_id)

    return response


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("response", {"data": "Connected"})


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True, allow_unsafe_werkzeug=True)
