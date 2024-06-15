import * as PIXI from 'pixi.js'
import {Graphics} from '@pixi/graphics';
import '@pixi/graphics-extras';
import {Viewport} from 'pixi-viewport'
import arrayShuffle from 'array-shuffle'
import Cookies from 'js-cookie'
import { io } from "socket.io-client"

import {standard_board_definition, standard_tile_set} from './standard_board'
import {Assets, Loader, Sprite, Spritesheet, Texture} from "pixi.js";

function assert(condition, message) {
    if (!condition) {
        if (message) {
            throw new Error(message);
        } else {
            throw new Error("Assertion failed");
        }
    }
}

let canvas_container = document.getElementById("canvas-container");

const app = new PIXI.Application();
canvas_container.appendChild(app.view);

app.renderer.view.style.position = "absolute";
app.renderer.view.style.display = "block";
//app.renderer.autoDensity = true;
app.resizeTo = canvas_container;

// https://github.com/loksland/pixel-art-game-test/blob/main/README.md
PIXI.BaseTexture.defaultOptions.scaleMode = PIXI.SCALE_MODES.NEAREST;
app.view.style.imageRendering = 'pixelated';
const PIXEL_SCALE = 1;
app.stage.scale.set(PIXEL_SCALE, PIXEL_SCALE);

const WORLD_WIDTH = 200;
const WORLD_HEIGHT = 200;
const viewport = new Viewport({
    screenWidth: window.innerWidth,
    screenHeight: window.innerHeight,
    worldWidth: WORLD_WIDTH,
    worldHeight: WORLD_HEIGHT,

    events: app.renderer.events
})
app.stage.addChild(viewport)

viewport
    .drag()
    .pinch()
    .wheel()
    .decelerate()

viewport.fit();
viewport.moveCenter(WORLD_WIDTH / 2, WORLD_HEIGHT / 2);

let spritesheet = await PIXI.Assets.load("/static/images/assets.json");

const Side = Object.freeze({
    NORTH: 0,
    NORTH_EAST: 1,
    SOUTH_EAST: 2,
    SOUTH: 3,
    SOUTH_WEST: 4,
    NORTH_WEST: 5,
});

class Tile {
    width = 33;
    height = 28;
    horizontal_width = 17;
    edge_width = (this.width - this.horizontal_width) / 2;

    constructor(viewport, type) {
        this.viewport = viewport;
        this.type = type;

        this.x_pos = 0;
        this.y_pos = 0;

        let type_img = this.type + ".png";
        this.sprite = new Sprite(spritesheet.textures[type_img]);
    }

    place(x_pos, y_pos) {
        this.x_pos = x_pos;
        this.y_pos = y_pos;

        this.viewport.addChild(this.sprite);
        // pixi y-axis is inverted
        this.sprite.position.set(this.x_pos, this.y_pos * -1);
    }

    place_beside(tile, side) {
        let x_pos = tile.x_pos;
        let y_pos = tile.y_pos;

        switch (side) {
            case Side.NORTH:
                y_pos += this.height;
                break;
            case Side.NORTH_EAST:
                y_pos += this.height / 2;
                x_pos += this.width - this.edge_width;
                break;
            case Side.SOUTH_EAST:
                y_pos -= this.height / 2;
                x_pos += this.width - this.edge_width;
                break;
            case Side.SOUTH:
                y_pos -= this.height;
                break;
            case Side.SOUTH_WEST:
                y_pos -= this.height / 2;
                x_pos = x_pos - this.width + this.edge_width;
                break;
            case Side.NORTH_WEST:
                y_pos += this.height / 2;
                x_pos = x_pos - this.width + this.edge_width;
                break;
        }

        this.place(x_pos, y_pos);
    }
}

let tiles = {};
let edges = {};
let intersections = {};

function draw_board(board) {
    console.log("draw board");
    console.log(board);

    let anchor_id = board["anchor_tile"];
    let anchor = new Tile(viewport, "wood");
    tiles[anchor_id] = anchor;
    anchor.place(0, 0);

    let tile_ids = [anchor_id];
    while (tile_ids.length > 0) {
        let tile_id = tile_ids.shift();
        assert(tile_id in tiles);
        let tile = tiles[tile_id];

        let tile_def = board["tiles"][tile_id];
        for (let [side_name, edge_id] of Object.entries(tile_def["edges"])) {
            let edge_def = board["edges"][edge_id];

            let neighbor_tile_id = undefined;
            for (let edge_tile_id of edge_def["tiles"]) {
                if (edge_tile_id !== tile_id) {
                    neighbor_tile_id = edge_tile_id;
                }
            }

            if (neighbor_tile_id === undefined) {
                continue;
            }
            if (neighbor_tile_id in tiles) {
                continue;
            }

            let neighbor = new Tile(viewport, "wood");
            tiles[neighbor_tile_id] = neighbor;
            tile_ids.push(neighbor_tile_id);

            let side = Side[side_name];
            neighbor.place_beside(tile, side);
        }
    }
}

console.log("game id: " + game_id);
let user_id = await Cookies.get("user_id");
console.log(user_id);

let socket = io("/goatan", {
    auth: {
        game: game_id,
        user: user_id
    }
});
socket.on("connect", function() {
    console.log("socket connect");
});
socket.on("game_state", function(event) {
    draw_board(event["board"]);
});
