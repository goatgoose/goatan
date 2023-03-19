import * as PIXI from 'pixi.js'
import { Graphics } from '@pixi/graphics';
import '@pixi/graphics-extras';
import { Viewport } from 'pixi-viewport'

let canvas_container = document.getElementById("canvas-container");

const app = new PIXI.Application();
canvas_container.appendChild(app.view);

app.renderer.view.style.position = "absolute";
app.renderer.view.style.display = "block";
//app.renderer.autoDensity = true;
app.resizeTo = canvas_container;

// create viewport
const viewport = new Viewport({
    screenWidth: window.innerWidth,
    screenHeight: window.innerHeight,
    worldWidth: 1000,
    worldHeight: 1000,

    events: app.renderer.events // the interaction module is important for wheel to work properly when renderer.view is placed or scaled
})

// add the viewport to the stage
app.stage.addChild(viewport)

// activate plugins
viewport
    .drag()
    .pinch()
    .wheel()
    .decelerate()

// let wheat_tile = PIXI.Sprite.from("/static/assets/catan/tile_grain-resources.assets-684.png");
// let mask = new Graphics();
// mask.beginFill(0xffffff);
// mask.drawRoundedPolygon(255, 255, 210, 6, 10)
// mask.endFill();
//
// let container = new PIXI.Container();
// container.mask = mask;
// container.addChild(wheat_tile);
// container.position.set(0, 0);
// viewport.addChild(container);

// add a red box
const sprite = viewport.addChild(new PIXI.Sprite(PIXI.Texture.WHITE))
sprite.tint = 0xff0000
sprite.width = sprite.height = 100
sprite.position.set(100, 100)
