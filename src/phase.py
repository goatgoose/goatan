from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

from src.piece import PieceType, Settlement, Road, Piece, House, PlayerPiece
from src.player import PlayerManager, Player
from src.board import Board, ResourceNumber
from src import error
from src.dice import D6


class GamePhase(ABC):
    def __init__(self, board: Board, players: PlayerManager):
        self._board: Board = board
        self._players: PlayerManager = players

        self._active_player_index = 0

    def place_piece(self, piece: Piece, location_id: str):
        if not self._piece_is_placeable(location_id, piece.type):
            raise error.InvalidAction(f"{piece.type.value} cannot be placed on {location_id}")

        self._board.set_piece(piece, location_id)
        self._piece_placed(location_id, piece)

    @property
    def active_player(self) -> Player:
        return self._players.get(self._active_player_index)

    @abstractmethod
    def _piece_is_placeable(self, location_id: str, piece_type: PieceType) -> bool:
        pass

    @abstractmethod
    def _piece_placed(self, location_id: str, piece: Piece):
        pass

    @abstractmethod
    def end_turn(self):
        pass

    @property
    @abstractmethod
    def finished(self):
        pass

    @abstractmethod
    def roll(self):
        pass

    @property
    @abstractmethod
    def roll_result(self) -> Optional[int]:
        pass

    @property
    @abstractmethod
    def expecting_roll(self) -> bool:
        pass

    @abstractmethod
    def serialize_hints(self):
        pass

    @staticmethod
    @abstractmethod
    def name():
        pass


class Game(GamePhase):
    def __init__(self, board: Board, players: PlayerManager):
        super().__init__(board, players)

        self._roll = None

    def _piece_is_placeable(self, location_id: str, piece_type: PieceType) -> bool:
        if self._roll is None:
            return False

        if piece_type == PieceType.HOUSE:
            return self._house_is_placeable(location_id)
        elif piece_type == PieceType.ROAD:
            return self._road_is_placeable(location_id)
        else:
            return False

    def _house_is_placeable(self, location_id: str) -> bool:
        intersection = self._board.intersections.get(location_id)
        if intersection is None:
            return False

        if intersection.settlement is not None:
            return False

        if not self.active_player.can_afford(House.cost()):
            return False

        if intersection.borders_house():
            return False

        if not intersection.borders_road_for_player(self.active_player):
            return False

        return True

    def _road_is_placeable(self, location_id: str) -> bool:
        edge = self._board.edges.get(location_id)
        if edge is None:
            return False

        if edge.road is not None:
            return False

        if not self.active_player.can_afford(Road.cost()):
            return False

        if not edge.borders_settlement_or_road_for_player(self.active_player):
            return False

        return True

    def _piece_placed(self, location_id: str, piece: Piece):
        if not isinstance(piece, PlayerPiece):
            return
        self.active_player.spend(piece.cost())

    def end_turn(self):
        if self._roll is None:
            raise error.InvalidAction("Roll must be made before ending turn")

        self._active_player_index += 1
        self._active_player_index = self._active_player_index % len(self._players)
        self._roll = None

    @property
    def finished(self):
        return False

    def roll(self):
        if self._roll is not None:
            raise error.InvalidAction("Already rolled")

        self._roll = D6(2).roll()
        value = sum(self._roll)
        if value == 7:
            return

        resource_number = ResourceNumber(value)
        for intersection in self._board.settled_intersections:
            player = intersection.settlement.player
            for resource_type in intersection.collect(resource_number):
                player.give(resource_type)

    @property
    def roll_result(self) -> Optional[int]:
        return self._roll

    @property
    def expecting_roll(self) -> bool:
        return self._roll is None

    def _placeable_settlements(self):
        for intersection in self._board.intersections.values():
            if self._house_is_placeable(intersection.id):
                yield intersection

    def _placeable_roads(self):
        for edge in self._board.edges.values():
            if self._road_is_placeable(edge.id):
                yield edge

    def serialize_hints(self):
        return {
            "intersections": {
                intersection.id: {
                    "type": PieceType.HOUSE.value,
                } for intersection in self._board.intersections.values()
                    if self._piece_is_placeable(intersection.id, PieceType.HOUSE)
            },
            "edges": {
                edge.id: {
                    "type": PieceType.ROAD.value,
                } for edge in self._board.edges.values()
                    if self._piece_is_placeable(edge.id, PieceType.ROAD)
            },
        }

    @staticmethod
    def name():
        return "game"


class Placement(GamePhase):
    class Turn:
        def __init__(self):
            self._finished = False
            self._placing_road = False

        @property
        def finished(self):
            return self._finished

        @property
        def placing_road(self):
            return not self.finished and self._placing_road

        @property
        def placing_house(self):
            return not self.finished and not self._placing_road

        def placed_road(self):
            assert self._placing_road
            assert not self._finished
            self._finished = True

        def placed_house(self):
            assert not self._placing_road
            assert not self._finished
            self._placing_road = True

    def __init__(self, board: Board, players: PlayerManager):
        super().__init__(board, players)

        self._finished = False
        self._turns_incrementing = True
        self._current_turn = Placement.Turn()

    def _piece_is_placeable(self, location_id: str, piece_type: PieceType) -> bool:
        if piece_type == PieceType.HOUSE:
            return self._house_is_placeable(location_id)
        elif piece_type == PieceType.ROAD:
            return self._road_is_placeable(location_id)
        else:
            return False

    def _house_is_placeable(self, location_id: str) -> bool:
        if not self._current_turn.placing_house:
            return False

        intersection = self._board.intersections.get(location_id)
        if intersection is None:
            return False

        if intersection.borders_house():
            return False

        return True

    def _road_is_placeable(self, location_id: str) -> bool:
        if not self._current_turn.placing_road:
            return False

        edge = self._board.edges.get(location_id)
        if edge is None:
            return False

        # Can't place a road on a road.
        if edge.road is not None:
            return False

        # During the placement phase, the road can only be placed next to the house that was just
        # placed, which is a house with no roads connected to it yet.
        borders_roadless_settlement = False
        for intersection in edge.intersections:
            settlement = intersection.settlement
            if settlement is None:
                continue
            if settlement.player != self.active_player:
                continue
            if not intersection.borders_road_for_player(self.active_player):
                borders_roadless_settlement = True
                break
        if not borders_roadless_settlement:
            return False

        return True

    def _piece_placed(self, location_id: str, piece: Piece):
        if piece.type == PieceType.HOUSE:
            # Resources are received for the second house placed.
            if not self._turns_incrementing:
                intersection = self._board.intersections[location_id]
                for resource_type in intersection.collect():
                    self.active_player.give(resource_type)
            self._current_turn.placed_house()
        elif piece.type == PieceType.ROAD:
            self._current_turn.placed_road()

    def end_turn(self):
        assert not self.finished

        if not self._current_turn.finished:
            raise error.InvalidAction("Turn is not finished")
        self._current_turn = Placement.Turn()

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

    def roll(self):
        raise error.InvalidAction("No rolling during placement phase")

    @property
    def roll_result(self) -> Optional[int]:
        return None

    @property
    def expecting_roll(self) -> bool:
        return False

    def _placeable_settlements(self):
        if not self._current_turn.placing_house:
            return []
        for intersection_id in self._board.intersections:
            if self._house_is_placeable(intersection_id):
                yield intersection_id, PieceType.HOUSE

    def _placeable_roads(self):
        if not self._current_turn.placing_road:
            return []
        for location_id in self._board.edges:
            if self._road_is_placeable(location_id):
                yield location_id, PieceType.ROAD

    def serialize_hints(self):
        return {
            "intersections": {
                intersection_id: {
                    "type": piece_type.value,
                } for intersection_id, piece_type in self._placeable_settlements()
            },
            "edges": {
                edge_id: {
                    "type": piece_type.value,
                } for edge_id, piece_type in self._placeable_roads()
            }
        }

    @staticmethod
    def name():
        return "placement"


