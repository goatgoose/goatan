import * as PIXI from 'pixi.js'
import {Graphics} from '@pixi/graphics';
import '@pixi/graphics-extras';
import {Viewport} from 'pixi-viewport'
import arrayShuffle from 'array-shuffle'

import {standard_board_definition, standard_tile_set} from './standard_board'

let canvas_container = document.getElementById("canvas-container");

const app = new PIXI.Application();
canvas_container.appendChild(app.view);

app.renderer.view.style.position = "absolute";
app.renderer.view.style.display = "block";
//app.renderer.autoDensity = true;
app.resizeTo = canvas_container;

const viewport = new Viewport({
    screenWidth: window.innerWidth,
    screenHeight: window.innerHeight,
    worldWidth: 1000,
    worldHeight: 1000,

    events: app.renderer.events
})
app.stage.addChild(viewport)

viewport
    .drag()
    .pinch()
    .wheel()
    .decelerate()

function assert(condition, message) {
    if (!condition) {
        if (message) {
            throw message;
        } else {
            throw "Assertion failed";
        }
    }
}

class Tile {
    size = 370;

    texture_prefix = "/static/assets/catan";
    texture_map = {
        "clay": this.texture_prefix + "/tile_brick-resources.assets-408.png",
        "desert": this.texture_prefix + "/tile_desert-resources.assets-494.png",
        "wheat": this.texture_prefix + "/tile_grain-resources.assets-1014.png",
        "wood": this.texture_prefix + "/tile_lumber-resources.assets-1336.png",
        "ore": this.texture_prefix + "/tile_ore-resources.assets-1349.png",
        "water": this.texture_prefix + "/tile_water-resources.assets-1219.png",
        "sheep": this.texture_prefix + "/tile_wool-resources.assets-418.png"
    }

    constructor(viewport, type) {
        this.viewport = viewport;
        this.type = type;

        assert(type in this.texture_map);
        this.sprite = PIXI.Sprite.from(this.texture_map[type]);
        this.sprite.anchor.set(0.5);

        this.mask = new Graphics();
        this.mask.beginFill(0xffffff);
        //this.mask.drawRoundedPolygon(0, 0, 210, 6, 4)
        this.mask.drawRegularPolygon(0, 0, 214, 6);
        this.mask.endFill();

        this.container = new PIXI.Container();
        this.container.mask = this.mask;
        this.container.addChild(this.sprite);
        this.container.position.set(0, 0);
    }

    place(from_tile, side) {
        this.viewport.addChild(this.mask);
        this.viewport.addChild(this.container);

        let x = 0;
        let y = 0;
        if (from_tile) {
            let from_x = from_tile.container.position.x;
            let from_y = from_tile.container.position.y;

            switch (side) {
                case '0':
                    x = from_x + this.size;
                    y = from_y;
                    break;
                case '1':
                    x = from_x + (this.size / 2);
                    y = from_y + (this.size * 7 / 8) - 3;
                    break;
                case '2':
                    x = from_x - (this.size / 2);
                    y = from_y + (this.size * 7 / 8) - 3;
                    break;
                case '3':
                    x = from_x - this.size;
                    y = from_y;
                    break;
                case '4':
                    x = from_x - (this.size / 2);
                    y = from_y - (this.size * 7 / 8) + 3;
                    break;
                case '5':
                    x = from_x + (this.size / 2);
                    y = from_y - (this.size * 7 / 8) + 3
                    break;
                default:
                    assert(false);
                    break;
            }
        }

        this.mask.position.set(x, y);
        this.container.position.set(x, y);
    }
}

function create_board(board, tile_set) {
    tile_set = arrayShuffle([...tile_set]);

    let start_tile = new Tile(viewport, tile_set.pop());
    start_tile.place(null, null);
    let tiles = {
        0: start_tile
    }

    let tile_idx_queue = [0]
    while (tile_idx_queue.length > 0) {
        let current_idx = tile_idx_queue.shift();
        let current_tile = tiles[current_idx];

        let tile_definition = board[current_idx];
        for (let side in tile_definition.neighbors) {
            let neighbor_idx = tile_definition.neighbors[side];
            if (!(neighbor_idx in tiles)) {
                tile_idx_queue.push(neighbor_idx);

                let new_tile = new Tile(viewport, tile_set.pop());
                new_tile.place(current_tile, side);
                tiles[neighbor_idx] = new_tile;
            }
        }
    }
}

create_board(standard_board_definition, standard_tile_set);
