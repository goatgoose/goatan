from enum import Enum, auto
from typing import Tuple, Dict, Optional, Set, List
import uuid
from abc import ABC
import pprint


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


class Tile(BoardItem):
    def __init__(self, type_: TileType):
        self.type = type_

        self.neighbors: Dict[TileSide, Tile] = {}
        self.edges: Dict[TileSide, Edge] = {}
        self.intersections: Dict[TileSide, Intersection] = {}

        super().__init__()

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

    def __str__(self):
        return self.id

    def __repr__(self):
        return str(self)


class Intersection(BoardItem):
    def __init__(self):
        self.edges: Set[Edge] = set()

        super().__init__()


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

        return board

    def to_json(self):
        pass

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
    board = Board.from_radius(2)
    print(board)

    pprint.pprint(board.tile_graph())
