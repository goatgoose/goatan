from enum import Enum, auto
from typing import Tuple, Dict, Optional


class TileType(Enum):
    BRICK = "brick"
    STONE = "stone"
    WHEAT = "wheat"
    SHEEP = "sheep"
    WOOD = "wood"
    DESERT = "desert"
    UNKNOWN = "unknown"


class Coordinate:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class Tile:
    def __init__(self, coord: Coordinate, type_: TileType):
        self.coord = coord
        self.type = type_


class Intersection:
    def __init__(self):
        self.edges: [Edge] = []


class TileSide(Enum):
    NORTH = 0
    NORTH_EAST = 1
    SOUTH_EAST = 2
    SOUTH = 3
    SOUTH_WEST = 4
    NORTH_WEST = 5


class Edge:
    def __init__(self, coord: Coordinate, tile_side: TileSide):
        self.coord: Coordinate = coord
        self.tile_side: TileSide = tile_side

        self.right_tile: Optional[Tile] = None
        self.left_tile: Optional[Tile] = None

    @property
    def tiles(self):
        return [self.right_tile, self.left_tile]

    def neighbor_coord(self, tile_side: TileSide) -> Tuple[Coordinate, TileSide]:
        return {
            TileSide.NORTH: (Coordinate(self.coord.x, self.coord.y + 2), )
        }.get(tile_side)


class Board:
    def __init__(self):
        self.tiles: Dict[Coordinate, Tile] = {}
        self.edges: Dict[Tuple[Coordinate, TileSide], Edge] = {}

    @staticmethod
    def from_definition(definition: [dict]):
        board = Board()
        for tile_def in definition:
            x = tile_def["x"]
            y = tile_def["y"]
            coordinate = Coordinate(x, y)
            tile_type = TileType(tile_def["type"])
            tile = Tile(coordinate, tile_type)
            board.tiles[coordinate] = tile

        for tile in board.tiles.values():
            for tile_side in TileSide:
                coord, tile_side = {
                    TileSide.NORTH:
                }.get(tile_side)

        return board

    def to_json(self):
        pass
