
var app = {}

app.setup_top_menu = function() {
    $("#logo").click(function() {
        if ($("#topmenu").is(":visible")) {
            $("#topmenu").fadeOut(180);
            $("#main_header").css("top", 0);
            $("#main_wrapper").css("margin-top", 0);
        } else {
            $("#topmenu").fadeIn(180);
            $("#main_header").css("top", ($("#topcont").height() - 5));
            $("#main_wrapper").css("margin-top", $("#topcont").height() + $("#main_header").height())
        }
    })

    $(".topclick").click(function() {
        window.location.href = "http://" + $(this).attr("rel") + CONFIG.DOMAIN
    })
}


app.run = function(route) {
    run(route);
}
