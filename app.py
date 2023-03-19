from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def base():
    return render_template("index.html")


@app.route("/play")
def play():
    return render_template("game.html")


if __name__ == '__main__':
    app.run()
