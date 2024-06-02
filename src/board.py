from enum import Enum, auto
from typing import Tuple, Dict, Optional, Set
import uuid
from abc import ABC


class BoardItem(ABC):
    def __init__(self):
        self.id = str(uuid.uuid4())


class TileType(Enum):
    BRICK = "brick"
    STONE = "stone"
    WHEAT = "wheat"
    SHEEP = "sheep"
    WOOD = "wood"
    DESERT = "desert"
    UNKNOWN = "unknown"


class Tile(BoardItem):
    def __init__(self,type_: TileType):
        self.type = type_

        self.edges: Dict[TileSide, Edge] = {}

        super().__init__()


class Intersection(BoardItem):
    def __init__(self):
        self.edges: [Edge] = []

        super().__init__()


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


class Edge(BoardItem):
    def __init__(self):
        self.tiles: Set[Tile] = set()

        super().__init__()

    def associate_tile(self, tile: Tile):
        assert len(self.tiles) < 2
        self.tiles.add(tile)

    def other_tile(self, tile: Tile):
        assert tile in self.tiles
        for other_tile in self.tiles:
            if tile != other_tile:
                return other_tile
        return None


class Board:
    def __init__(self):
        self.tiles: Dict[str, Tile] = {}
        self.edges: Dict[str, Edge] = {}
        self.intersections: Dict[str, Intersection] = {}

    @staticmethod
    def from_definition(definition: [dict]):
        pass

    @staticmethod
    def from_radius(radius: int):
        tile_depth: Dict[Tile: int] = {}

        center_tile = Tile(TileType.UNKNOWN)
        tile_depth[center_tile] = 0
        tiles = [center_tile]

        board = Board()
        while len(tiles) > 0:
            tile = tiles.pop(0)
            board.tiles[tile.id] = tile

            if tile_depth[tile] >= radius:
                continue

            # create a new neighboring tile for each empty border
            for tile_side in TileSide:
                if tile_side in tile.edges:
                    continue

                new_tile = Tile(TileType.UNKNOWN)
                board.tiles[new_tile.id] = new_tile
                tiles.append(new_tile)
                tile_depth[new_tile] = tile_depth[tile] + 1

                neighboring_edge = Edge()
                neighboring_edge.associate_tile(tile)
                neighboring_edge.associate_tile(new_tile)

                tile.edges[tile_side] = neighboring_edge
                new_tile.edges[TileSide.opposite(tile_side)] = neighboring_edge

            # connect each edge to its intersection
            for tile_side in TileSide:
                edge_1 = tile.edges[tile_side]
                edge_2 = tile.edges[TileSide.wrap(tile_side.value + 1)]

                if edge_1.f

            # connect each neighboring tile to its new neighbor
            for tile_side in TileSide:
                neighbor_1 = tile.edges[tile_side].other_tile(tile)
                neighbor_2 = tile.edges[TileSide.wrap(tile_side.value + 1)].other_tile(tile)




    def to_json(self):
        pass
