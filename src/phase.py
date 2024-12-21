from abc import ABC, abstractmethod
from typing import Dict, List

from src.piece import PieceType
from src.player import PlayerManager, Player
from src.board import Board


class GamePhase(ABC):
    @property
    @abstractmethod
    def active_player(self) -> Player:
        pass

    @abstractmethod
    def placeable_pieces(self) -> Dict[str, List[PieceType]]:
        pass

    @abstractmethod
    def piece_is_placeable(self, item_id: str, piece_type: PieceType) -> bool:
        pass

    @abstractmethod
    def end_turn(self):
        pass

    @property
    @abstractmethod
    def finished(self):
        pass


class Placement(GamePhase):
    def __init__(self, board: Board, players: PlayerManager):
        self._board: Board = board
        self._players: PlayerManager = players

        self._finished = False
        self._active_player_index = 0
        self._turns_incrementing = True
        self._placing_road = False

    @property
    def active_player(self):
        return self._players.get(self._active_player_index)

    def placeable_pieces(self) -> Dict[str, List[PieceType]]:
        pass

    def piece_is_placeable(self, item_id: str, piece_type: PieceType) -> bool:
        pass

    def end_turn(self):
        assert not self.finished

        if self._active_player_index == len(self._players) - 1 and self._turns_incrementing:
            self._turns_incrementing = False
            return
        if self._active_player_index == 0 and not self._turns_incrementing:
            self._finished = True

        if self._turns_incrementing:
            self._active_player_index += 1
        else:
            self._active_player_index -= 1
        assert self._active_player_index < len(self._players)

    @property
    def finished(self):
        return self._finished
