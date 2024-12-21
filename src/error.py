from abc import ABCMeta, abstractmethod


class GameError(Exception, metaclass=ABCMeta):
    def __init__(self, message: str = ""):
        super().__init__(message)

        self._message: str = message

    @property
    @abstractmethod
    def error_type(self) -> str:
        pass

    def message(self) -> str:
        msg = self.error_type
        if len(self._message) > 0:
            msg += f": {self._message}"
        return msg

    def serialize(self) -> dict:
        return {
            "error": self.message()
        }


class InvalidAction(GameError):
    def __init__(self, message: str = ""):
        super().__init__(message)

    @property
    def error_type(self) -> str:
        return "Invalid action"


class InvalidState(GameError):
    def __init__(self, message: str = ""):
        super().__init__(message)

    @property
    def error_type(self) -> str:
        return "Invalid state"


