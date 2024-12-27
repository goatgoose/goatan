from abc import ABC, abstractmethod
from src.board import Board, Tile, TileSide, TileType, ResourceNumber
from typing import Dict
import random


class TileProvider(ABC):
    @abstractmethod
    def get_tile(self) -> Tile:
        pass


class StandardProvider(TileProvider):
    TILES = [
        TileType.WOOD, TileType.WOOD, TileType.WOOD, TileType.WOOD,
        TileType.SHEEP, TileType.SHEEP, TileType.SHEEP, TileType.SHEEP,
        TileType.WHEAT, TileType.WHEAT, TileType.WHEAT, TileType.WHEAT,
        TileType.BRICK, TileType.BRICK, TileType.BRICK,
        TileType.STONE, TileType.STONE, TileType.STONE,
        TileType.DESERT,
    ]
    RESOURCE_NUMBERS = [
        ResourceNumber.TWO,
        ResourceNumber.THREE, ResourceNumber.THREE,
        ResourceNumber.FOUR, ResourceNumber.FOUR,
        ResourceNumber.FIVE, ResourceNumber.FIVE,
        ResourceNumber.SIX, ResourceNumber.SIX,
        ResourceNumber.EIGHT, ResourceNumber.EIGHT,
        ResourceNumber.NINE, ResourceNumber.NINE,
        ResourceNumber.TEN, ResourceNumber.TEN, ResourceNumber.TEN,
        ResourceNumber.ELEVEN, ResourceNumber.ELEVEN,
        ResourceNumber.TWELVE,
    ]

    def __init__(self):
        self.tiles = []
        self.resource_numbers = []

        self._fill_tile_pool()
        self._fill_resource_pool()

    def _fill_tile_pool(self):
        self.tiles = self.TILES.copy()
        random.shuffle(self.tiles)

    def _fill_resource_pool(self):
        self.resource_numbers = self.RESOURCE_NUMBERS.copy()
        random.shuffle(self.resource_numbers)

    def get_tile(self) -> Tile:
        # If a board is generated larger than the standard catan board, refresh the tile/resource pools to generate
        # tiles with the same probability.
        if len(self.tiles) == 0:
            self._fill_tile_pool()
        if len(self.resource_numbers) == 0:
            self._fill_resource_pool()

        # TODO: prevent neighboring 6s/8s
        tile = Tile()
        tile.type = self.tiles.pop()
        tile.resource_number = self.resource_numbers.pop()
        return tile


class Generator(ABC):
    @abstractmethod
    def generate(self) -> Board:
        pass


class StandardGenerator(Generator):
    PROVIDER = StandardProvider

    def __init__(self, radius=2):
        self.radius = radius
        self.provider = self.PROVIDER()

    def generate(self) -> Board:
        tile_depth: Dict[Tile, int] = {}

        center_tile = self.provider.get_tile()
        tile_depth[center_tile] = 0
        tiles = [center_tile]

        board = Board()
        while len(tiles) > 0:
            tile = tiles.pop(0)
            board.tiles[tile.id] = tile

            # create new neighboring tiles
            if tile_depth[tile] < self.radius:
                for tile_side in TileSide:
                    if tile_side in tile.neighbors:
                        continue

                    new_tile = self.provider.get_tile()
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

        board.initialize(center_tile)

        return board