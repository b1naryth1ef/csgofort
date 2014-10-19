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

// Handles a single tracked user
vac.route(function(id) {
    // Handles the untracking-button (remove from my list)
    $(".container").delegate("#untrack", "click", function (ev) {
        $.ajax("/api/untrack/"+id, {
            success: function (data) {
                if (data.success) {
                    app.alert("Removed user from your tracking list!", "success");
                    $("#untrack").hide();
                    $("#track").show();
                } else {
                    app.alert("Failed to remove user from your tracking list!");
                }
            }
        })
    })

    // Handles the tracking-button (add to my list)
    $(".container").delegate("#track", "click", function (ev) {
        $.ajax("/api/track/"+id, {
            success: function (data) {
                if (data.success) {
                    app.alert("Added user to your tracking list!", "success");
                    $("#track").hide();
                    $("#untrack").show();
                } else {
                    app.alert("Failed to add user to your tracking list!");
                }
            }
        })
    })

    // Grab the info payload for this VacID and render the page
    $.ajax("/api/info/"+id, {
        success: function (data) {
            $(".container").append(
                app.template(T.single_tracked_entry, {v: data.result})
            )
        }
    })

    // Attempt to see if we have this user tracked, and show buttons if so
    if (CONFIG.USER) {
        $.ajax("/api/info/tracked", {
            success: function (data) {
                if (!data.success) return;

                if ($.inArray(parseInt(id), data.result) != -1) {
                    $("#untrack").show();
                } else {
                    $("#track").show();
                }
            }
        })
    }
}, "/tracked/(.*)?");

vac.index = function() {
    if (CONFIG.USER) {
        vac.render_tracked_list();
    }
}