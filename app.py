import logging

import flask
from flask import Flask, render_template, redirect, request, make_response
from game import Goatan, Player

app = Flask(__name__)


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


@app.route("/stream/<game_id>")
def stream(game_id):
    game = games.get(game_id)
    if game_id not in games:
        return f"Game not found: {game_id}", 400

    player_id = request.cookies.get("player_id")
    if not player_id:
        return f"Player not found: {player_id}", 400

    player = game.players.get(player_id)
    if not player:
        return f"Player not found: {player_id}", 400

    game.activate_player(player_id)

    def stream_message_queue():
        try:
            message_queue = player.message_queue
            while True:
                message = message_queue.get()
                yield message
        except GeneratorExit:
            print("stream closed")

    return flask.Response(stream_message_queue(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.run(port=8000, debug=True)
