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
    def __init__(self, type_: TileType):
        self.type = type_

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

        self.settlement: Optional[Piece] = None

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

    def can_place_house(self, placement_phase: bool, player: Player) -> bool:
        # a house can't be placed if something is already built here
        if self.settlement is not None:
            return False

        # houses must be attached to a road owned by the player. this only applies when the game is
        # out of the placement phase.
        if not placement_phase:
            bordering_owned_road = False
            for edge in self.edges:
                if edge.road is not None and edge.road.player == player:
                    bordering_owned_road = True
                    break
            if not bordering_owned_road:
                return False

        # houses must be 2 edges away from other houses. if any edges are connected to a house, the
        # new house can't be placed.
        for edge in self.edges:
            neighboring_intersection = edge.other_intersection(self)
            if neighboring_intersection.settlement is not None:
                return False

        return True


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

    def can_place_road(self, player: Player) -> bool:
        # a road can't be placed if a road has already been placed.
        if self.road is not None:
            return False

        for intersection in self.intersections:
            settlement = intersection.settlement
            if settlement is None:
                # if the neighboring settlement doesn't exist, a bordering edge must contain a
                # player-owned road.
                for edge in intersection.other_edges(self):
                    if edge.road is not None and edge.road.player == player:
                        return True
            else:
                # otherwise, the neighboring settlement must be owned by the player.
                if settlement.player == player:
                    return True

        return False


class Board:
    def __init__(self):
        self.anchor_tile = None
        self.tiles: Dict[str, Tile] = {}
        self.edges: Dict[str, Edge] = {}
        self.intersections: Dict[str, Intersection] = {}

    @staticmethod
    def from_definition(definition: [dict]):
        pass

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

    @staticmethod
    def from_radius(radius: int):
        tile_depth: Dict[Tile, int] = {}

        center_tile = Tile(TileType.UNKNOWN)
        tile_depth[center_tile] = 0
        tiles = [center_tile]

        board = Board()
        while len(tiles) > 0:
            tile = tiles.pop(0)
            board.tiles[tile.id] = tile

            # create new neighboring tiles
            if tile_depth[tile] < radius:
                for tile_side in TileSide:
                    if tile_side in tile.neighbors:
                        continue

                    new_tile = Tile(TileType.UNKNOWN)
                    board.tiles[new_tile.id] = new_tile
                    tile_depth[new_tile] = tile_depth[tile] + 1
                    tiles.append(new_tile)

                    tile.neighbors[tile_side] = new_tile
                    new_tile.neighbors[TileSide.opposite(tile_side)] = tile

            # associate neighboring tiles with each other
            for tile_side in TileSide:
                tile_1 = tile.neighbors.get(tile_side)
                if not tile_1:
                    continue
                tile_2 = tile.neighbors.get(TileSide.wrap(tile_side.value + 1))
                if not tile_2:
                    continue

                tile_1_side, tile_2_side = {
                    TileSide.NORTH: (TileSide.SOUTH_EAST, TileSide.NORTH_WEST),
                    TileSide.NORTH_EAST: (TileSide.SOUTH, TileSide.NORTH),
                    TileSide.SOUTH_EAST: (TileSide.SOUTH_WEST, TileSide.NORTH_EAST),
                    TileSide.SOUTH: (TileSide.NORTH_WEST, TileSide.SOUTH_EAST),
                    TileSide.SOUTH_WEST: (TileSide.NORTH, TileSide.SOUTH),
                    TileSide.NORTH_WEST: (TileSide.NORTH_EAST, TileSide.SOUTH_WEST),
                }.get(tile_side)

                tile_1.neighbors[tile_1_side] = tile_2
                tile_2.neighbors[tile_2_side] = tile_1

        board._construct_edge_graph()
        board.anchor_tile = center_tile

        return board

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
                    "type": tile.type.name,
                } for tile in self.tiles.values()
            },
            "edges": {
                edge.id: {
                    "tiles": [tile.id for tile in edge.tiles]
                } for edge in self.edges.values()
            },
            "anchor_tile": self.anchor_tile.id,
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


if __name__ == '__main__':
    board = Board.from_radius(3)
    print(board)

    pprint.pprint(board.serialize())
