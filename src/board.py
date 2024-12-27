from enum import Enum, auto
from typing import Tuple, Dict, Optional, Set, List
import uuid
from abc import ABC
import pprint

from src.util import GameItem
from src.player import Player
from src.piece import Settlement, Road, PieceType, Piece


class TileType(Enum):
    BRICK = "brick"
    STONE = "stone"
    WHEAT = "wheat"
    SHEEP = "sheep"
    WOOD = "wood"
    DESERT = "desert"
    UNKNOWN = "unknown"


class ResourceNumber(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE= 12


class TileSide(Enum):
    NORTH = 0
    NORTH_EAST = 1
    SOUTH_EAST = 2
    SOUTH = 3
    SOUTH_WEST = 4
    NORTH_WEST = 5

    @staticmethod
    def opposite(tile_side):
        return {
            TileSide.NORTH: TileSide.SOUTH,
            TileSide.NORTH_EAST: TileSide.SOUTH_WEST,
            TileSide.SOUTH_EAST: TileSide.NORTH_WEST,
            TileSide.SOUTH: TileSide.NORTH,
            TileSide.SOUTH_WEST: TileSide.NORTH_EAST,
            TileSide.NORTH_WEST: TileSide.SOUTH_EAST,
        }.get(tile_side)

    @staticmethod
    def wrap(side: int):
        return TileSide(side % len(TileSide))


class Tile(GameItem):
    def __init__(self):
        self.type = TileType.UNKNOWN
        self.resource_number: Optional[ResourceNumber] = None

        self.neighbors: Dict[TileSide, Tile] = {}
        self.edges: Dict[TileSide, Edge] = {}
        self.intersections: Dict[TileSide, Intersection] = {}

        super().__init__()

    def associate_neighbor(self, neighbor, side):
        if self.neighbors.get(side) == neighbor:
            return

        assert self.neighbors.get(side) is None
        self.neighbors[side] = neighbor

    def associate_edge(self, edge, side):
        if self.edges.get(side) == edge:
            return

        assert self.edges.get(side) is None
        self.edges[side] = edge

    def associate_intersection(self, intersection, side):
        if self.intersections.get(side) == intersection:
            return

        assert self.intersections.get(side) is None
        self.intersections[side] = intersection

    def bfs(self):
        visited = set()
        tiles = [self]

        while len(tiles) > 0:
            tile = tiles.pop(0)
            if tile in visited:
                continue

            visited.add(tile)
            for neighbor in self.neighbors.values():
                if neighbor not in visited:
                    tiles.append(neighbor)

            yield tile

    @property
    def farmable(self):
        return self.type != TileType.DESERT

    def serialize(self):
        return {
            "type": self.type.name
        }

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)


class Intersection(GameItem):
    def __init__(self):
        self.tiles: Set[Tile] = set()
        self.edges: Set[Edge] = set()

        self.settlement: Optional[Settlement] = None

        super().__init__()

    def associate_tile(self, tile: Tile):
        if tile in self.tiles:
            return

        assert len(self.tiles) < 3
        self.tiles.add(tile)

    def associate_edge(self, edge):
        if edge in self.edges:
            return

        assert len(self.edges) < 3
        self.edges.add(edge)

    def other_edges(self, edge):
        assert edge in self.edges
        for other_edge in self.edges:
            if other_edge == edge:
                continue
            yield other_edge

    def borders_house(self):
        # If an intersection contains a house, we can say it borders a house.
        if self.settlement is not None:
            return True

        # The intersection borders a house if any edge connects to an intersection with a house.
        for edge in self.edges:
            neighboring_intersection = edge.other_intersection(self)
            if neighboring_intersection.settlement is not None:
                return True

        return False

    def borders_road_for_player(self, player: Player):
        # A bordering edge must contain a road owned by the player.
        for edge in self.edges:
            road = edge.road
            if road is None:
                continue
            if road.player == player:
                return True

        return False


class Edge(GameItem):
    def __init__(self):
        self.tiles: Set[Tile] = set()
        self.intersections: Set[Intersection] = set()

        self.road: Optional[Road] = None

        super().__init__()

    def associate_tile(self, tile: Tile):
        if tile in self.tiles:
            return

        assert len(self.tiles) < 2
        self.tiles.add(tile)

    def associate_intersection(self, intersection: Intersection):
        if intersection in self.intersections:
            return

        assert len(self.intersections) < 2
        self.intersections.add(intersection)

    def other_intersection(self, intersection: Intersection):
        assert intersection in self.intersections
        set_ = self.intersections.copy()
        set_.remove(intersection)
        return set_.pop()

    def borders_settlement_for_player(self, player: Player):
        for intersection in self.intersections:
            if intersection.settlement is None:
                continue
            if intersection.settlement.player == player:
                return True
        return False

    def borders_road_for_player(self, player: Player):
        for intersection in self.intersections:
            for neighboring_edge in intersection.other_edges(self):
                road = neighboring_edge.road
                if road is None:
                    continue
                if road.player == player:
                    return True
        return False


class Board:
    def __init__(self):
        self.anchor_tile = None
        self.tiles: Dict[str, Tile] = {}
        self.edges: Dict[str, Edge] = {}
        self.intersections: Dict[str, Intersection] = {}

        # location_id : piece
        self._settlements: Dict[Player, Dict[str, Settlement]] = {}
        self._roads: Dict[Player, Dict[str, Road]] = {}

    def set_piece(self, piece: Piece, location_id: str):
        if isinstance(piece, Settlement):
            self.set_settlement(piece, location_id)
        elif isinstance(piece, Road):
            self.set_road(piece, location_id)
        else:
            raise ValueError(f"Invalid piece type: {piece}")

    def set_settlement(self, settlement: Settlement, location_id: str):
        intersection = self.intersections[location_id]
        intersection.settlement = settlement
        if settlement.player not in self._settlements:
            self._settlements[settlement.player] = {}
        self._settlements[settlement.player][location_id] = settlement

    def settlements(self, player: Player) -> Dict[str, Settlement]:
        settlements_for_player = self._settlements.get(player)
        if settlements_for_player is None:
            return dict()
        return settlements_for_player

    def all_settlements(self) -> Tuple[str, Settlement]:
        for settlements in self._settlements.values():
            for location_id, settlement in settlements.items():
                yield location_id, settlement

    def set_road(self, road: Road, location_id: str):
        edge = self.edges[location_id]
        edge.road = road
        if road.player not in self._roads:
            self._roads[road.player] = {}
        self._roads[road.player][location_id] = road

    def roads(self, player: Player) -> Dict[str, Road]:
        roads_for_player = self._roads.get(player)
        if roads_for_player is None:
            return dict()
        return roads_for_player

    def all_roads(self) -> Dict[str, Road]:
        for roads in self._roads.values():
            for location_id, road in roads.items():
                yield location_id, road

    @staticmethod
    def from_definition(definition: [dict]):
        pass

    def initialize(self, anchor_tile: Tile):
        self._construct_edge_graph()
        self.anchor_tile = anchor_tile

    def _construct_edge_graph(self):
        for tile in self.tiles.values():

            # create new intersections
            for side in TileSide:
                if side in tile.intersections:
                    continue

                intersection = Intersection()
                self.intersections[intersection.id] = intersection

                # associate the new intersection with the tile
                tile.intersections[side] = intersection
                intersection.associate_tile(tile)

                # if the tile has neighboring tiles, associate the new intersection with them too
                neighbor_0_intersect_side, neighbor_1_intersect_side = {
                    TileSide.NORTH: (TileSide.SOUTH_EAST, TileSide.SOUTH_WEST),
                    TileSide.NORTH_EAST: (TileSide.SOUTH, TileSide.NORTH_WEST),
                    TileSide.SOUTH_EAST: (TileSide.SOUTH_WEST, TileSide.NORTH),
                    TileSide.SOUTH: (TileSide.NORTH_WEST, TileSide.NORTH_EAST),
                    TileSide.SOUTH_WEST: (TileSide.NORTH, TileSide.SOUTH_EAST),
                    TileSide.NORTH_WEST: (TileSide.NORTH_EAST, TileSide.SOUTH)
                }.get(side)

                neighbor_0 = tile.neighbors.get(side)
                if neighbor_0 is not None:
                    neighbor_0.associate_intersection(intersection, neighbor_0_intersect_side)
                    intersection.associate_tile(neighbor_0)

                neighbor_1 = tile.neighbors.get(TileSide.wrap(side.value + 1))
                if neighbor_1 is not None:
                    neighbor_1.associate_intersection(intersection, neighbor_1_intersect_side)
                    intersection.associate_tile(neighbor_1)

            # create new edges
            for side in TileSide:
                if side in tile.edges:
                    continue

                edge = Edge()
                self.edges[edge.id] = edge

                edge.associate_tile(tile)
                tile.associate_edge(edge, side)

                neighbor = tile.neighbors.get(side)
                if neighbor is not None:
                    edge.associate_tile(neighbor)
                    neighbor.associate_edge(edge, TileSide.opposite(side))

            # connect edges to intersections
            for side in TileSide:
                edge = tile.edges.get(side)
                intersection = tile.intersections.get(side)

                edge.associate_intersection(intersection)
                intersection.associate_edge(edge)

                previous_intersection = tile.intersections.get(TileSide.wrap(side.value - 1))
                previous_intersection.associate_edge(edge)
                edge.associate_intersection(previous_intersection)

    def serialize(self):
        return {
            "tiles": {
                tile.id: {
                    "edges": {
                        side.name: edge.id for side, edge in tile.edges.items()
                    },
                    "intersections": {
                        side.name: intersection.id for side, intersection in tile.intersections.items()
                    },
                    "type": tile.type.value,
                    "resource_number": tile.resource_number.value if tile.resource_number is not None else None,
                } for tile in self.tiles.values()
            },
            "edges": {
                edge.id: {
                    "tiles": [tile.id for tile in edge.tiles]
                } for edge in self.edges.values()
            },
            "anchor_tile": self.anchor_tile.id,
            "pieces": {
                "intersections": {
                    intersection_id: {
                        "type": settlement.type.value,
                        "player": settlement.player.id,
                    } for intersection_id, settlement in self.all_settlements()
                },
                "edges": {
                    edge_id: {
                        "type": road.type.value,
                        "player": road.player.id,
                    } for edge_id, road in self.all_roads()
                }
            }
        }

    def tile_graph(self):
        graph: Dict[Tile, List[Tile]] = {}
        for tile in self.tiles.values():
            graph[tile] = list(tile.neighbors.values())
        return graph

    def __str__(self):
        return f"""
        len: {len(self.tiles)}
        """

    def __repr__(self):
        return str(self)
