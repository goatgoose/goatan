import * as PIXI from 'pixi.js'
import {Graphics} from '@pixi/graphics';
import '@pixi/graphics-extras';
import {Viewport} from 'pixi-viewport'
import arrayShuffle from 'array-shuffle'
import Cookies from 'js-cookie'
import { io } from "socket.io-client"
import $ from "jquery";

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
app.renderer.backgroundColor = 0x59c8ff;

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
});
app.stage.addChild(viewport);

viewport
    .drag()
    .pinch()
    .wheel()
    .decelerate()

viewport.fit();
viewport.moveCenter(WORLD_WIDTH / 2, WORLD_HEIGHT / 2);
viewport.sortableChildren = true;

let spritesheet = await PIXI.Assets.load("/static/images/assets.json");

const TileSide = Object.freeze({
    NORTH: 0,
    NORTH_EAST: 1,
    SOUTH_EAST: 2,
    SOUTH: 3,
    SOUTH_WEST: 4,
    NORTH_WEST: 5,
});

const TILE_WIDTH = 33;
const TILE_HEIGHT = 28;
const TILE_HORIZONTAL_WIDTH = 17;
const TILE_DIAGONAL_WIDTH = (TILE_WIDTH - TILE_HORIZONTAL_WIDTH) / 2;

class Tile {
    constructor(viewport, x_pos, y_pos) {
        this.viewport = viewport;
        this.x_pos = x_pos;
        this.y_pos = y_pos;

        this.sprite = undefined;
    }

    static from_neighbor(viewport, neighbor, side) {
        let x_pos = neighbor.x_pos;
        let y_pos = neighbor.y_pos;

        switch (side) {
            case TileSide.NORTH:
                y_pos += TILE_HEIGHT;
                break;
            case TileSide.NORTH_EAST:
                y_pos += TILE_HEIGHT / 2;
                x_pos += TILE_WIDTH - TILE_DIAGONAL_WIDTH;
                break;
            case TileSide.SOUTH_EAST:
                y_pos -= TILE_HEIGHT / 2;
                x_pos += TILE_WIDTH - TILE_DIAGONAL_WIDTH;
                break;
            case TileSide.SOUTH:
                y_pos -= TILE_HEIGHT;
                break;
            case TileSide.SOUTH_WEST:
                y_pos -= TILE_HEIGHT / 2;
                x_pos = x_pos - TILE_WIDTH + TILE_DIAGONAL_WIDTH;
                break;
            case TileSide.NORTH_WEST:
                y_pos += TILE_HEIGHT / 2;
                x_pos = x_pos - TILE_WIDTH + TILE_DIAGONAL_WIDTH;
                break;
        }

        return new Tile(viewport, x_pos, y_pos);
    }

    draw_resource(resource_type) {
        if (this.sprite !== undefined) {
            this.viewport.removeChild(this.sprite);
        }

        let type_img = resource_type + ".png";
        this.sprite = new Sprite(spritesheet.textures[type_img]);
        this.viewport.addChild(this.sprite);
        this.sprite.position.set(this.x_pos, this.y_pos * -1);
        this.sprite.zIndex = 0;
    }
}

const EdgeOrientation = Object.freeze({
    HORIZONTAL: 0,
    RIGHT: 1,
    LEFT: 2
});

function edge_orientation_from_side(side) {
    switch (side) {
        case TileSide.NORTH:
        case TileSide.SOUTH:
            return EdgeOrientation.HORIZONTAL;
        case TileSide.NORTH_EAST:
        case TileSide.SOUTH_WEST:
            return EdgeOrientation.LEFT;
        case TileSide.SOUTH_EAST:
        case TileSide.NORTH_WEST:
            return EdgeOrientation.RIGHT;
    }
}

class Edge {
    constructor(viewport, x_pos, y_pos, orientation) {
        this.viewport = viewport;
        this.x_pos = x_pos;
        this.y_pos = y_pos;
        this.orientation = orientation;

        this.sprite = undefined;
    }

    static from_tile(viewport, tile, side) {
        let x_pos = tile.x_pos;
        let y_pos = tile.y_pos;

        switch (side) {
            case TileSide.NORTH:
                x_pos += TILE_WIDTH / 2;
                break;
            case TileSide.NORTH_EAST:
                x_pos += TILE_WIDTH - (TILE_DIAGONAL_WIDTH / 2);
                y_pos -= TILE_HEIGHT / 4;
                break;
            case TileSide.SOUTH_EAST:
                x_pos += TILE_WIDTH - (TILE_DIAGONAL_WIDTH / 2);
                y_pos -= TILE_HEIGHT - (TILE_HEIGHT / 4);
                break;
            case TileSide.SOUTH:
                x_pos += TILE_WIDTH / 2;
                y_pos -= TILE_HEIGHT;
                break;
            case TileSide.SOUTH_WEST:
                x_pos += TILE_DIAGONAL_WIDTH / 2;
                y_pos -= TILE_HEIGHT - (TILE_HEIGHT / 4);
                break;
            case TileSide.NORTH_WEST:
                x_pos += TILE_DIAGONAL_WIDTH / 2;
                y_pos -= TILE_HEIGHT / 4;
                break;
        }

        return new Edge(viewport, x_pos, y_pos, edge_orientation_from_side(side));
    }

    static road_img(orientation) {
        switch (orientation) {
            case EdgeOrientation.HORIZONTAL:
                return "road-flat.png";
            case EdgeOrientation.RIGHT:
                return "road-right.png";
            case EdgeOrientation.LEFT:
                return "road-left.png";
        }
    }

    draw_road() {
        if (this.sprite !== undefined) {
            this.viewport.removeChild(this.sprite);
        }

        this.sprite = new Sprite(spritesheet.textures[Edge.road_img(this.orientation)]);
        this.viewport.addChild(this.sprite);
        this.sprite.position.set(this.x_pos, this.y_pos * -1);
        this.sprite.zIndex = 1;
        this.sprite.anchor.set(0.5);
    }
}

class Intersection {
    constructor(viewport, x_pos, y_pos) {
        this.viewport = viewport;
        this.x_pos = x_pos;
        this.y_pos = y_pos;
    }

    static from_tile(viewport, tile, side) {
        let x_pos = tile.x_pos;
        let y_pos = tile.y_pos;

        switch (side) {
            case TileSide.NORTH:
                x_pos += TILE_DIAGONAL_WIDTH + TILE_HORIZONTAL_WIDTH;
                break;
            case TileSide.NORTH_EAST:
                x_pos += TILE_WIDTH;
                y_pos -= TILE_HEIGHT / 2;
                break;
            case TileSide.SOUTH_EAST:
                x_pos += TILE_DIAGONAL_WIDTH + TILE_HORIZONTAL_WIDTH;
                y_pos -= TILE_HEIGHT;
                break;
            case TileSide.SOUTH:
                x_pos += TILE_DIAGONAL_WIDTH;
                y_pos -= TILE_HEIGHT;
                break;
            case TileSide.SOUTH_WEST:
                y_pos -= TILE_HEIGHT / 2;
                break;
            case TileSide.NORTH_WEST:
                x_pos += TILE_DIAGONAL_WIDTH;
                break;
        }

        return new Intersection(viewport, x_pos, y_pos);
    }

    draw_house() {
        if (this.sprite !== undefined) {
            this.viewport.removeChild(this.sprite);
        }

        this.sprite = new Sprite(spritesheet.textures["house.png"]);
        this.viewport.addChild(this.sprite);
        this.sprite.position.set(this.x_pos, this.y_pos * -1);
        this.sprite.zIndex = 1;
        this.sprite.anchor.set(0.5);
    }
}

let tiles = {};
let edges = {};
let intersections = {};

function clear_board() {
    viewport.removeChildren();
    tiles = {};
    edges = {};
    intersections = {};
}

function draw_board(board) {
    console.log("draw board");
    console.log(board);

    let anchor_id = board["anchor_tile"];
    let anchor = new Tile(viewport, 0, 0);
    tiles[anchor_id] = anchor;
    anchor.draw_resource("wood");

    let tile_ids = [anchor_id];
    while (tile_ids.length > 0) {
        let tile_id = tile_ids.shift();
        assert(tile_id in tiles);
        let tile = tiles[tile_id];

        let tile_def = board["tiles"][tile_id];
        for (let [side_name, edge_id] of Object.entries(tile_def["edges"])) {
            let side = TileSide[side_name];
            let edge_def = board["edges"][edge_id];

            if (!(edge_id in edges)) {
                let edge = Edge.from_tile(viewport, tile, side);
                edges[edge_id] = edge;
                edge.draw_road();
            }

            let neighbor_tile_id = undefined;
            for (let edge_tile_id of edge_def["tiles"]) {
                if (edge_tile_id !== tile_id) {
                    neighbor_tile_id = edge_tile_id;
                }
            }

            if (neighbor_tile_id !== undefined && !(neighbor_tile_id in tiles)) {
                let neighbor = Tile.from_neighbor(viewport, tile, side);
                tiles[neighbor_tile_id] = neighbor;
                tile_ids.push(neighbor_tile_id);
                neighbor.draw_resource("wood");
            }
        }

        for (let [side_name, intersection_id] of Object.entries(tile_def["intersections"])) {
            if (intersection_id in intersections) {
                continue;
            }

            let side = TileSide[side_name];
            let intersection = Intersection.from_tile(viewport, tile, side);
            intersections[intersection_id] = intersection;
            intersection.draw_house();
        }
    }
}

function set_active_player(player_id) {
    $(".player-content").removeClass("active");
    $("#player-content-" + player_id).addClass("active");
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
    clear_board();
    draw_board(event["board"]);

    set_active_player(event["active_player"]);
});
