import * as PIXI from 'pixi.js'
import {Graphics} from '@pixi/graphics';
import '@pixi/graphics-extras';
import {Viewport} from 'pixi-viewport'
import arrayShuffle from 'array-shuffle'

import {standard_board_definition, standard_tile_set} from './standard_board'
import {Assets, Loader, Sprite, Spritesheet, Texture} from "pixi.js";

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

class Tile {
    width = 33;
    height = 28;
    horizontal_width = 17;
    edge_width = (this.width - this.horizontal_width) / 2;

    constructor(viewport, type) {
        this.viewport = viewport;
        this.type = type;

        let type_img = this.type + ".png";
        this.sprite = new Sprite(spritesheet.textures[type_img]);
    }

    place(x, y) {
        this.viewport.addChild(this.sprite);

        let x_pos = 0;
        let y_pos = 0;
        if (y % 2 === 0) {
            x_pos = x * (this.width + this.horizontal_width);
            y_pos = y * (this.height / 2);
        } else {
            y = y / 2;

            let x_offset = this.horizontal_width + this.edge_width;
            let y_offset = 0;

            x_pos = -x_offset + (x * (this.width + this.horizontal_width));
            y_pos = y_offset + (y * this.height);
        }

        // pixi y-axis is inverted
        y_pos *= -1;

        this.sprite.position.set(x_pos, y_pos);
    }
}

for (let tile_def of standard_board_definition) {
    let tile = new Tile(viewport, tile_def.type);
    tile.place(tile_def.x, tile_def.y);
}
