from abc import ABC, abstractmethod
import uuid


class GameItem(ABC):
    def __init__(self):
        self.id = self._generate_id()

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4())

    def __eq__(self, other):
        if other is None:
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
