
const app = new PIXI.Application({width: 256, height: 256});
document.body.appendChild(app.view);

app.renderer.view.style.position = "absolute";
app.renderer.view.style.display = "block";
app.renderer.autoDensity = true;
app.resizeTo = window;

const Application = PIXI.Application,
    Sprite = PIXI.Sprite,
    Container = PIXI.Container,
    Graphics = PIXI.Graphics,
    Ticker = PIXI.Ticker,
    Rectangle = PIXI.Rectangle,
    Point = PIXI.Point

let wheat_tile = Sprite.from("/static/assets/catan/tile_grain-resources.assets-684.png");
let mask = new Graphics();
mask.beginFill(0xffffff);
mask.drawRoundedPolygon(255, 255, 210, 6, 10)
mask.endFill();

let container = new Container();
container.mask = mask;
container.addChild(wheat_tile);
container.position.set(0, 0);
app.stage.addChild(container);

// https://github.com/davidfig/pixi-viewport/issues/124
// https://www.jetbrains.com/help/webstorm/using-webpack.html#install_and_configure_webpack
