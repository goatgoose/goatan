import string
import random


class Goatan:
    def __init__(self):
        self.id = "".join([
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(8)
        ])
