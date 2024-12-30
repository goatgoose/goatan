from abc import ABC, abstractmethod
from typing import Optional
from src.board import Board
from src.player import Player


class WinCondition(ABC):
    @abstractmethod
    def victor(self, board: Board) -> Optional[Player]:
        pass


class VictoryPoint(WinCondition):
    def __init__(self, required_points: int):
        self.required_points = required_points

    def victor(self, board: Board) -> Optional[Player]:
        points = {}
        for intersection in board.settled_intersections:
            player = intersection.settlement.player
            if player not in points:
                points[player] = 0
            points[player] += 1

            if points[player] >= self.required_points:
                return player

        return None
