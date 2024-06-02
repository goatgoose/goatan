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

    def publish_event(self, data, event_type=None):
        message = f"data: {data}\n\n"
        if event_type is not None:
            message = f"event: {event_type}\n{message}"
        self.message_queue.put(message)

    @staticmethod
    def generate_id():
        return _generate_id()


class Goatan:
    def __init__(self):
        self.id = _generate_id()
        self.players = {}  # id : player

    def _publish_event(self, event):
        for player in self.players.values():
            player.publish_event(event)

    def register_player(self, player_id):
        if player_id in self.players:
            return

        self._publish_event(f"registered player: {player_id}")

        player = Player(player_id)
        self.players[player_id] = player
        print(f"Registered player {player_id} for {self.id}")

    def activate_player(self, player_id):
        player = self.players.get(player_id)
        assert player is not None

        player.publish_event(f"activated player: {player_id}")
        print(f"Player activated: {player_id}")
