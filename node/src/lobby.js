import { io } from "socket.io-client"
import Cookies from "js-cookie";
import $ from "jquery";

console.log("game id: " + game_id);
let user_id = await Cookies.get("user_id");
console.log(user_id);

let socket = io("/lobby", {
    auth: {
        game: game_id,
        user: user_id
    }
});
socket.on("connect", function() {
    console.log("lobby socket connect");
});
socket.on("player_update", function(event) {
    console.log("player_update");
    console.log(event);

    let player_div = $('#player_list');
    player_div.empty();
    for (let player_id of event["players"]) {
        player_div.append("<ul>" + player_id + "</ul>");
    }
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
