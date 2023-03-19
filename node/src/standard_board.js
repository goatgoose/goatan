export let standard_tile_set = [
    "clay", "clay", "clay",
    "ore", "ore", "ore",
    "wheat", "wheat", "wheat", "wheat",
    "sheep", "sheep", "sheep", "sheep",
    "wood", "wood", "wood", "wood",
    "desert"
]

export let standard_board_definition = {
    0: {
        neighbors: {
            0: 1,
            1: 4,
            2: 3
        }
    },
    1: {
        neighbors: {
            0: 2,
            1: 5,
            2: 4,
            3: 0
        }
    },
    2: {
        neighbors: {
            1: 6,
            2: 5,
            3: 1
        }
    },
    3: {
        neighbors: {
            0: 4,
            1: 8,
            2: 7,
            5: 0
        }
    },
    4: {
        neighbors: {
            0: 5,
            1: 9,
            2: 8,
            3: 3,
            4: 0,
            5: 1
        }
    },
    5: {
        neighbors: {
            0: 6,
            1: 10,
            2: 9,
            3: 4,
            4: 1,
            5: 2
        }
    },
    6: {
        neighbors: {
            1: 11,
            2: 10,
            3: 5,
            4: 2
        }
    },
    7: {
        neighbors: {
            0: 8,
            1: 12,
            5: 3
        }
    },
    8: {
        neighbors: {
            0: 9,
            1: 13,
            2: 12,
            3: 7,
            4: 3,
            5: 4
        }
    },
    9: {
        neighbors: {
            0: 10,
            1: 14,
            2: 13,
            3: 8,
            4: 4,
            5: 5
        }
    },
    10: {
        neighbors: {
            0: 11,
            1: 15,
            2: 14,
            3: 9,
            4: 5,
            5: 6
        }
    },
    11: {
        neighbors: {
            2: 15,
            3: 10,
            4: 6
        }
    },
    12: {
        neighbors: {
            0: 13,
            1: 16,
            4: 7,
            5: 8
        }
    },
    13: {
        neighbors: {
            0: 14,
            1: 17,
            2: 16,
            3: 12,
            4: 8,
            5: 9
        }
    },
    14: {
        neighbors: {
            0: 15,
            1: 18,
            2: 17,
            3: 13,
            4: 9,
            5: 10
        }
    },
    15: {
        neighbors: {
            2: 18,
            3: 14,
            4: 10,
            5: 11
        }
    },
    16: {
        neighbors: {
            0: 17,
            4: 12,
            5: 13
        }
    },
    17: {
        neighbors: {
            0: 18,
            3: 16,
            4: 13,
            5: 14
        }
    },
    18: {
        neighbors: {
            3: 17,
            4: 14,
            5: 15
        }
    }
}
