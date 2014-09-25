function print_landing_debug() {
    console.log("Oh hello there!");
    console.log("Looks like you've been digging around our source!");
    console.log("We're looking for people like you to help us build the best" +
        " trading, betting and analytics platform for CSGO!");
    console.log("If you have JS/Python/Go experience, and like helping out, even better!");
    console.log("If your interested in helping out, or just wanna look at what we've"+
        " got going on in the background, hit us up on steam!");
    console.log("http://steamcommunity.com/id/b1naryth1ef");
}

function set_topbar_colors() {
    $("#top1").css("background-color", pastel_colors());
    $("#top2").css("background-color", pastel_colors());
    $("#top3").css("background-color", pastel_colors());
}

function pastel_colors() {
    var r = (Math.round(Math.random()* 127) + 127).toString(16);
    var g = (Math.round(Math.random()* 127) + 127).toString(16);
    var b = (Math.round(Math.random()* 127) + 127).toString(16);
    return '#' + r + g + b;
}

print_landing_debug();
set_topbar_colors();