import * as PIXI from 'pixi.js'
import {Graphics} from '@pixi/graphics';
import '@pixi/graphics-extras';
import {Viewport} from 'pixi-viewport'
import arrayShuffle from 'array-shuffle'
import Cookies from 'js-cookie'
import {io} from "socket.io-client"
import $ from "jquery";

import {standard_board_definition, standard_tile_set} from './standard_board'
import {Assets, Loader, Sprite, Spritesheet, TextStyle, Texture} from "pixi.js";

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

const color_to_hex = Object.freeze({
    "hint": 0xffffff,
    "white": 0xe3e0c1,
    "black": 0x1c1c1b,
    "blue": 0x176bbf,
    "green": 0x17bf3b,
    "red": 0xb32f25,
    "yellow": 0xbcdb1d,
});

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

        this.tile_sprite = undefined;
        this.number_tile_sprite = undefined;
        this.number_text_sprite = undefined;
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

    clear_resource() {
        if (this.tile_sprite !== undefined) {
            this.clear_number_tile();
            this.viewport.removeChild(this.tile_sprite);
        }
    }

    draw_resource(resource_type) {
        this.clear_resource();

        let type_img = resource_type + ".png";
        this.tile_sprite = new Sprite(spritesheet.textures[type_img]);
        this.viewport.addChild(this.tile_sprite);
        this.tile_sprite.position.set(this.x_pos, this.y_pos * -1);
        this.tile_sprite.zIndex = 0;
    }

    clear_number_tile() {
        if (this.number_text_sprite !== undefined) {
            assert(this.number_tile_sprite !== undefined);
            this.number_tile_sprite.removeChild(this.number_text_sprite);
        }
        if (this.number_tile_sprite !== undefined) {
            assert(this.tile_sprite !== undefined);
            this.tile_sprite.removeChild(this.number_tile_sprite);
        }
    }

    draw_number_tile(number) {
        this.clear_number_tile();

        this.number_tile_sprite = new Sprite(spritesheet.textures["number-tile.png"]);
        this.tile_sprite.addChild(this.number_tile_sprite);
        this.number_tile_sprite.position.set(11, 9);
        this.number_tile_sprite.zIndex = 1;

        this.number_text_sprite = new Sprite(spritesheet.textures[number + ".png"]);
        this.number_tile_sprite.addChild(this.number_text_sprite);
        this.number_text_sprite.zIndex = 2;

        let x_offset = (
            this.number_tile_sprite.texture.width
            - this.number_text_sprite.texture.width
        ) / 2;
        let y_offset = (
            this.number_tile_sprite.texture.height
            - this.number_text_sprite.texture.height
        ) / 2;
        this.number_text_sprite.position.set(x_offset, y_offset);
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

    clear_road() {
        if (this.sprite !== undefined) {
            this.viewport.removeChild(this.sprite);
        }
    }

    draw_road(color) {
        this.clear_road();

        this.sprite = new Sprite(spritesheet.textures[Edge.road_img(this.orientation)]);
        this.sprite.tint = color_to_hex[color];
        this.viewport.addChild(this.sprite);
        this.sprite.position.set(this.x_pos, this.y_pos * -1);
        this.sprite.zIndex = 1;
        this.sprite.anchor.set(0.5);

        return this.sprite;
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

    clear_house() {
        if (this.sprite !== undefined) {
            this.viewport.removeChild(this.sprite);
        }
    }

    draw_house(color) {
        this.clear_house();

        this.sprite = new Sprite(spritesheet.textures["house.png"]);
        this.sprite.tint = color_to_hex[color];
        this.viewport.addChild(this.sprite);
        this.sprite.position.set(this.x_pos, this.y_pos * -1);
        this.sprite.zIndex = 1;
        this.sprite.anchor.set(0.5);

        return this.sprite;
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

function draw_board(game_state) {
    console.log("draw board");
    console.log(game_state);

    let players = game_state["players"]["player_map"];
    let board = game_state["board"];
    let hints = game_state["hints"];

    let anchor_id = board["anchor_tile"];
    let anchor = new Tile(viewport, 0, 0);
    tiles[anchor_id] = anchor;
    anchor.draw_resource(board["tiles"][anchor_id]["type"]);
    let resource_number = board["tiles"][anchor_id]["resource_number"];
    if (resource_number !== null) {
        anchor.draw_number_tile(resource_number);
    }

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

                let road = board["pieces"]["edges"][edge_id];
                if (road !== undefined) {
                    let color = players[road["player"]]["color"];
                    edge.draw_road(color);
                }

                let road_hint = hints["edges"][edge_id];
                if (road_hint !== undefined && game_state["active_player"] === player_id) {
                    let sprite = edge.draw_road("hint");
                    sprite.eventMode = "static";
                    sprite.cursor = "pointer";
                    sprite.on("pointerdown", function () {
                        console.log("click edge: " + edge_id);
                        socket.emit("place", {
                            "piece_type": "road",
                            "item": edge_id,
                        });
                    });
                }
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
                neighbor.draw_resource(board["tiles"][neighbor_tile_id]["type"]);
                let resource_number = board["tiles"][neighbor_tile_id]["resource_number"];
                if (resource_number !== null) {
                    neighbor.draw_number_tile(resource_number);
                }
            }
        }

        for (let [side_name, intersection_id] of Object.entries(tile_def["intersections"])) {
            if (intersection_id in intersections) {
                continue;
            }

            let side = TileSide[side_name];
            let intersection = Intersection.from_tile(viewport, tile, side);
            intersections[intersection_id] = intersection;

            let piece = board["pieces"]["intersections"][intersection_id];
            if (piece !== undefined) {
                if (piece["type"] === "house") {
                    let color = players[piece["player"]]["color"];
                    intersection.draw_house(color);
                }
            }

            let piece_hint = hints["intersections"][intersection_id];
            if (piece_hint !== undefined && game_state["active_player"] === player_id) {
                let sprite = intersection.draw_house("hint");
                sprite.eventMode = "static";
                sprite.cursor = "pointer";
                sprite.on("pointerdown", function () {
                    console.log("click intersection: " + intersection_id);
                    socket.emit("place", {
                        "piece_type": "house",
                        "item": intersection_id,
                    });
                });
            }
        }
    }
}

function set_active_player(player_id) {
    $(".player-content").removeClass("active");
    $("#player-content-" + player_id).addClass("active");
}

function update_dice(game_state) {
    let active_player = game_state["active_player"];
    let roll = game_state["roll"];
    let expecting_roll = game_state["expecting_roll"];

    let die_1 = $("#die-1");
    let die_2 = $("#die-2");

    if (roll === null) {
        die_1.css("visibility", "hidden");
        die_2.css("visibility", "hidden");
    } else {
        die_1.css("visibility", "visible");
        die_1.attr("src", "/static/images/assets/die-" + roll[0] + ".png");

        die_2.css("visibility", "visible");
        die_2.attr("src", "/static/images/assets/die-" + roll[1] + ".png");
    }

    let roll_button = $("#roll-button");
    if (expecting_roll && active_player === player_id) {
        roll_button.css("visibility", "visible");
    } else {
        roll_button.css("visibility", "hidden");
    }
}

let resources = {
    "brick": 0,
    "sheep": 0,
    "stone": 0,
    "wheat": 0,
    "wood": 0,
};
function update_resource_counts() {
    $(".resource-count").each(function () {
        $(this).text(resources[$(this).data("resource")]);
    });
}

// resource : count
// Where count is positive for items giving away and negative for items receiving.
let proposed_trade = {};

function reset_trade(show_new_trade_button) {
    update_resource_counts(resources);
    proposed_trade = {
        "brick": 0,
        "sheep": 0,
        "stone": 0,
        "wheat": 0,
        "wood": 0,
    };

    if (show_new_trade_button) {
        $("#new-trade-button").css("visibility", "visible");
    } else {
        $("#new-trade-button").css("visibility", "hidden");
    }

    $("#trade-menu").css("visibility", "hidden");
}
function update_trade_menu() {
    $(".resource-count").each(function () {
        let resource = $(this).data("resource");
        let html = resources[resource] + ' ' +
            '<a class="trade-counter trade-increment" data-resource="' + resource +'" style="cursor: pointer">+</a> ' +
            '<a class="trade-counter trade-decrement" data-resource="' + resource + '" style="cursor: pointer">-</a>';

        let proposed_count = proposed_trade[resource];
        if (proposed_count > 0) {
            html += '<span class="text-success">';
        } else if (proposed_count < 0) {
            html += '<span class="text-danger">';
        }
        html += " (" + proposed_trade[resource] + ")";
        html += "</span>";

        $(this).html(html);
    });

    $("#new-trade-button").css("visibility", "hidden");
    $("#trade-menu").css("visibility", "visible");

    $(".trade-increment").click(function () {
        let resource = $(this).data("resource");
        proposed_trade[resource]++;
        update_trade_menu();
    });
    $(".trade-decrement").click(function () {
        let resource = $(this).data("resource");
        if (resources[resource] + proposed_trade[resource] - 1 < 0) {
            return;
        }

        proposed_trade[resource]--;
        update_trade_menu();
    });
}

console.log("game id: " + game_id);
let user_id = await Cookies.get("user_id");
console.log(user_id);

let player_id = undefined;

let socket = io("/goatan", {
    auth: {
        game: game_id,
        user: user_id
    }
});
socket.on("connect", function (event) {
    console.log("socket connect");
});
socket.on("player_info", function (event) {
    console.log("player info");
    console.log(event);
    player_id = event["id"];
});
socket.on("game_state", function (event) {
    clear_board();
    draw_board(event);
    set_active_player(event["active_player"]);
    resources = event["players"]["player_map"][player_id]["resources"];
    update_resource_counts();
    update_dice(event);

    if (event["phase"] === "game" && !event["expecting_roll"] && event["active_player"] === player_id) {
        reset_trade(true);
    } else {
        reset_trade(false);
    }
});

$(document).ready(function () {
    $("#end-turn-button").click(function () {
        socket.emit("end_turn");
    });
    $("#roll-button").click(function () {
        socket.emit("roll");
    });

    $("#new-trade-button").click(function() {
        update_trade_menu();
    });
    $("#cancel-trade-button").click(function() {
        reset_trade(true);
    });
});
