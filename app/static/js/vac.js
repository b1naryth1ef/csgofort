var vac = app.new_realm("vactrak", {});

vac.setup = function () {
    vac.bind_search();
}

vac.bind_search = function() {
    $("#top-search").keydown(function (ev) {
        if (ev.which == 13) {
            $.ajax("/api/track", {
                data: {
                    ids: $("#top-search-box").val()
                },
                success: function(data) {
                    $("#top-search-box").val("")
                    if (data.success && data.added.length) {
                        app.alert("Added " + data.added.join(", ") + " to tracking list!", "success");
                        vac.render_tracked_list();
                    } else if (!data.added.length) {
                        app.alert("That user is already on your tracking list!", "warning");
                    } else {
                        app.alert("Failed to add user to tracking list! Please make sure the STEAMID is correct!");
                    }
                }
            });
        }
    });
}

vac.render_tracked_list = function () {
    $.ajax("/api/info", {
        success: function (data) {
            $("#tracked-body").empty();
            _.each(data.result.tracked, function (v, k) {
                $("#tracked-body").append(
                    app.template(T.tracked_table_row, {v: v})
                );
            });
        }
    });
}

vac.route(function(id) {
    $.ajax("/api/info/"+id, {
        success: function (data) {
            console.log(data)
            $(".container").append(
                app.template(T.single_tracked_entry, {v: data.result})
            )
        }
    })
}, "/tracked/(.*)?");

vac.index = function() {
    if (CONFIG.USER) {
        vac.render_tracked_list();
    }
}