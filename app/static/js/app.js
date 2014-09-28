
var JST = {
    alert: _.template('<div class="col-md-12"><div class="alert alert-<%= type %>">' +
        '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' +
        '<strong>Uh Oh!</strong> <%= msg %></div></div>')
}

var app = {}

app.alert = function(msg, type) {
    console.log(":^)")
    if (type === undefined) {
        type = "danger";
    }
    $("#alerts").append(JST.alert({
        "msg": msg,
        "type": type
    }))
}

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
