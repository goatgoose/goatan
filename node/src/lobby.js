import { io } from "socket.io-client"
import Cookies from "js-cookie";
import $ from "jquery";

console.log("game id: " + game_id);
let user_id = await Cookies.get("user_id");
console.log(user_id);

let player_id = undefined;

let socket = io("/lobby", {
    auth: {
        game: game_id,
        user: user_id
    }
});
socket.on("connect", function(event) {
    console.log("lobby socket connect");
});
socket.on("player_update", function(event) {
    console.log("player_update");
    console.log(event);

    let player_div = $('#player_list');
    player_div.empty();
    for (let player of event["players"]) {
        let player_string = player["name"];
        if (player["id"] === player_id) {
            player_string += " (you)";
        }
        player_div.append("<ul>" + player_string + "</ul>");
    }
});
socket.on("player_id", function(event) {
    console.log("player_id");
    console.log(event);

    player_id = event["player_id"];
});
socket.on("game_start", function(event) {
    window.location.replace(event["route"]);
});

$(document).ready(function() {
    $("#start-game-button").click(function(){
        let form_data = $("#settings-form").serializeArray();
        socket.emit("game_init", form_data);
    });
});
