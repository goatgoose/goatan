import * as PIXI from 'pixi.js'
import {Graphics} from '@pixi/graphics';
import '@pixi/graphics-extras';
import {Viewport} from 'pixi-viewport'

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

class Tile {
    size = 363;

    constructor(viewport, type) {
        this.viewport = viewport;
        this.type = type;

        this.sprite = PIXI.Sprite.from("/static/assets/catan/tile_grain-resources.assets-684.png");
        this.sprite.anchor.set(0.5);

        this.mask = new Graphics();
        this.mask.beginFill(0xffffff);
        this.mask.drawRoundedPolygon(0, 0, 210, 6, 4)
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

            if (side === 1) {
                x = from_x + this.size;
                y = from_y;
            }
        }

        this.mask.position.set(x, y);
        this.container.position.set(x, y);
    }
}

let tile1 = new Tile(viewport, "wheat");
tile1.place(null, null);

let tile2 = new Tile(viewport, "wheat");
tile2.place(tile1, 1);
