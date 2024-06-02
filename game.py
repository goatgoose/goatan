import string
import random
import queue


def _generate_id():
    return "".join([
        random.choice(string.ascii_lowercase + string.digits)
        for _ in range(8)
    ])


class Player:
    def __init__(self, id_):
        self.id = id_
        self.message_queue = queue.Queue()

    @staticmethod
    def generate_id():
        return _generate_id()


class Goatan:
    def __init__(self):
        self.id = _generate_id()
        self.players = {}  # id : player

    def register_player(self, player_id):
        player = Player(player_id)
        self.players[player_id] = player
