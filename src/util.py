from abc import ABC, abstractmethod
import uuid


class GameItem(ABC):
    def __init__(self):
        self.id = self._generate_id()

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4())
