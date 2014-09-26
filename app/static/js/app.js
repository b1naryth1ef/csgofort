
var app = {}

app.setup_top_menu = function() {
    $("#top-menu-toggle").click(function() {
        $("#left-side-navi").fadeIn();
        // if ($("#top-menu").is(":visible")) {
        //     $("#top-menu").fadeOut(180);
        //     $(".page-head").css("top", 0);
        //     $(".page-head").css("margin-top", 0);
        // } else {
        //     $("#top-menu").fadeIn(180);
        //     $(".page-head").css("top", ($("#top-menu").height() - 5));
        //     // $(".page-head").css("margin-top", $("#top-menu").height() + $("#main_header").height())
        // }
    })

    $(".topclick").click(function() {
        window.location.href = "http://" + $(this).attr("rel") + CONFIG.DOMAIN
    })
}


app.run = function(route) {
    run(route);
}
