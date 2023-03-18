
const app = new PIXI.Application({width: 256, height: 256});
document.body.appendChild(app.view);

app.renderer.view.style.position = "absolute";
app.renderer.view.style.display = "block";
app.renderer.autoDensity = true;
app.resizeTo = window;

function updateUIHeight(event) {
    document.getElementById("ui-container").style.height = window.innerHeight + "px";
}
window.addEventListener("resize", updateUIHeight);
window.addEventListener("load", updateUIHeight);
