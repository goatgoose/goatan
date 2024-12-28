import random
from abc import ABC, abstractmethod
from typing import Tuple


class Dice:
    def __init__(self, count: int = 1):
        self.count = count

    def roll(self) -> [int]:
        return [self._roll() for _ in range(self.count)]

    @abstractmethod
    def _roll(self) -> int:
        pass


class D6(Dice):
    def _roll(self):
        return random.randint(1, 6)
