
var maz = app.new_realm("maz", {
    search_xhr: null,
});

var search_result_template = _.template('<a href="/item/<%= obj.id %>"  class="list-item" style="height: 60px; overflow: hidden;">'+
    '<div class="list-item-content"><img height="64px" src="/image/<%= obj.id %>" class="img-circle pull-left"><h1><%= obj.data.name %></h3>'+
    '</div></a>');

var inventory_row_template = _.template('<tr value="<%= value * 100 %>"><td><a href="/item/<%= id %>"><%= name %></a></td><td><%= tvalue %></td></tr>');

var changelog_row_template = _.template('<span class="<%= cls %>"><span class="<%= icon %>"></span> <%= msg %></span>')
var changelog_row_base_template = _.template('<li id="<%= id %>" class="list-group-item"></li>')

maz.index = function() {
    var value_xhr = $.ajax("/api/graph/totalvalue");
    var size_xhr = $.ajax("/api/graph/totalsize");

    $.when(value_xhr, size_xhr).done(function (value_d, size_d) {
        draw_dashboard_graphs(value_d[0].data, size_d[0].data)
    });

    $.ajax("/api/info", {
        success: function(data) {
            if (!data.success) {
                app.alert("<strong>Uh Oh!</strong> Looks like we're having some server issues, please try refreshing the page in a few seconds.")
                return console.log("Failed to load market info");
            }

            if (data.community > 0) {
                app.alert("The Steam Community is experiencing some issues right now! This may effect the stability, accuracy and reliability of CS:GO Fort and it's services.");
            }

            $("#stat-unique").text(data.totals.items.toLocaleString());
            $("#stat-listed").text(data.totals.listings.toLocaleString());
            $("#stat-value").text(CONFIG.SYM + app.convert(data.totals.value).toLocaleString());
        }
    })
}

maz.setup = function () {
    maz.setup_search();
}

maz.route(function() {

}, "/api");

maz.route(function (id) {
    var median_xhr = $.ajax("/api/item/"+id+"/graph/median");
    var volume_xhr = $.ajax("/api/item/"+id+"/graph/volume");

    $.when(median_xhr, volume_xhr).done(function(median_d, volume_d) {
        draw_item_graph(median_d[0].data, volume_d[0].data);
    });
}, "/item/(.*)?")

maz.route(function () {
    $("#tracking-base").delegate("#tracking-enable-btn", "click", function (ev) {
        ev.stopImmediatePropagation();

        // Mark this button as disabled, works as a sudo-debounce
        $(this).addClass("disabled");

        // Make the API call
        $.ajax("/api/tracking/enable", {
            success: function (d1) {
                // Enable the button
                $(ev.currentTarget).removeClass("disabled");

                if (!d1.success) {
                    app.alert("<strong>Uh Oh!</strong> We couldn't enable inventory tracking for your account! Please insure your inventory is public, and try again shortly!");
                } else {
                    app.alert("Inventory Tracking Enabled!", "success");
                    $("#tracking-enabled").fadeIn();
                    $("#tracking-disabled").hide();
                }
            }
        })
    })

    $("#tracking-base").delegate("#tracking-disable-btn", "click", function (ev) {
        ev.stopImmediatePropagation();
        $(this).addClass("disabled");

        $.ajax("/api/tracking/disable", {
            success: function(d1) {
                $(ev.currentTarget).removeClass("disabled");
                app.alert("Inventory Tracking Disabled!", "success");
                $("#tracking-disabled").fadeIn();
                $("#tracking-enabled").hide();
            }
        })
    })

    maz.load_value_info();
    $.ajax("/api/tracking", {
        success: function (data) {
            if (!data.enabled) {
                $("#tracking-disabled").fadeIn();
            } else {
                $("#tracking-enabled").fadeIn();
                maz.load_tracking_info();
            }
        }
    })
}, "/inventory")

maz.route(function () {
    $.ajax("/api/graphmetric/community_response_time", {
        success: function (data) {
            draw_generic_graph("steam_community_response_time", "Steam Community Response Time", data.data);
        }
    })

    $.ajax("/api/graphmetric/request_time", {
        success: function(data) {
            draw_generic_graph("request_time", "Fort Response Time", data.data);
        }
    })

    $.ajax("/api/graphmetric/index_items_time", {
        success: function (data) {
            draw_generic_graph("index_items_time", "Item Index Time", data.data);
        }
    })
}, "/stats")

maz.load_tracking_info = function () {
    $.ajax("/api/tracking/"+CONFIG.USER.id+"/graph/value", {
        success: function (data) {
            draw_inventory_graphs(data.data)
        }
    })

    function add_item(key, category, data) {
        msg_prefix = category.charAt(0).toUpperCase() + category.slice(1);
        $(key).html(changelog_row_template({
            msg: msg_prefix + " " + data.market_hash_name,
            icon: "glyphicon glyphicon-plus-sign",
            cls: (category == "added" ? "success" :"danger"),
            value: key
        }))
    }

    // TODO: maybe do a proper sort?
    $.ajax("/api/tracking/"+CONFIG.USER.id+"/history", {
        success: function (data) {
            _.each(data.data, function (v, k) {
                _.each(v.added, function(v1, k1) {
                    $("#changelog").append(changelog_row_base_template({
                        id: "added-"+k1+"-"+k
                    }))
                    $.ajax("/api/asset/" + v1.split("_")[0], {
                        success: function (d1) {
                            add_item("#added"+"-"+k1+"-"+k, "added", d1)
                        }
                    })
                })

                _.each(v.removed, function(v1, k1) {
                    $("#changelog").append(changelog_row_base_template({
                        id: "removed-"+k1+"-"+k
                    }))
                    $.ajax("/api/asset/" + v1.split("_")[0], {
                        success: function (d1) {
                            add_item("#removed"+"-"+k1+"-"+k, "removed", d1)
                        }
                    })
                })
            })
        }
    })
}

maz.load_value_info = function() {
    $.ajax("http://auth." + CONFIG.DOMAIN + "/inventory/" + CONFIG.USER.id, {
        success: function (data) {
            if (!data.success) {
                app.alert("<strong>Uh Oh!</strong> We can't grab your inventory! Looks like either your inventory is private, or the steam community is having some problems.");
                return;
            }

            $.ajax("/api/items/bulk", {
                data: {
                    "ids": _.map(data.inv, function (v, k) {
                        return v.i
                    }).join(","),
                    "cur": CONFIG.USER.cur
                },
                success: function(assets) {
                    $("#loader").fadeOut()
                    var value = 0;

                    // TODO: instead of repeating items have a count?
                    _.each(data.inv, function(v, k) {
                        var entry = assets.results[v.i];

                        // Might be a shitty weird item
                        if (!entry || !entry.price) {
                            return;
                        }

                        var content = inventory_row_template({
                            name: entry.name,
                            tvalue: CONFIG.SYM + entry.price.med.toLocaleString(),
                            value: entry.price.med,
                            id: entry.id
                        });

                        $("#inv-body").append(content);
                        if (entry.price.med > 0) {
                            value = value + entry.price.med;
                        }
                    })

                    $("#worth").text(CONFIG.SYM + value.toLocaleString());
                    app.sortTable($("#inv-table"), 'desc');
                }
            })
        }
    })
}

maz.setup_search = function() {
    $("#top-search").keydown(function (ev) {
        // If a current search query is running, just cancel it now
        if (maz.search_xhr) {
            maz.search_xhr.abort();
            maz.search_xhr = null;
        }

        // Grab the true value from the search bar, if it's empty just close
        //  the search dropdown.
        var val = $("#top-search-box").val() + String.fromCharCode(ev.which);
        if (!val) {
            $("#top-search-drop").addClass("closed")
            $("#top-search-drop").removeClass("open")
            return;
        }

        // Open a XHR request, store it so we can cancel it if need be
        maz.search_xhr = $.ajax("/api/search", {
            data: {
                name: val,
                size: 10
            },
            success: function (data) {
                $("#search-results").empty()

                _.each(data.results, function (v, k) {
                    if (v.score < 1) return;
                    $("#search-results").append(search_result_template({
                        obj: v
                    }))
                })

                $("#top-search-drop").removeClass("closed")
                $("#top-search-drop").addClass("open")
            }
        })
    });
}

function data_to_rickshaw(data) {
    var dat = [];
    _.each(data, function (v, k) {
        dat.push({
            x: parseInt(k),
            y: v
        })
    })
    return dat;
}

function draw_inventory_graphs(d1) {
    var rdc = new Rickshaw.Graph( {
            element: document.getElementById("inventory-chart"),
            renderer: 'area',
            width: $("#inventory-chart").width(),
            height: 250,
            padding: {top: .08},
            series: [
                {color: "#2f9fe0", data: data_to_rickshaw(d1), name: 'Estimated Inventory Value'},
            ],
    } );

    rdc.render();

    var rdc_resize = function() {
            rdc.configure({
                    width: $("#inventory-chart").width(),
                    height: $("#inventory-chart").height()
            });
            rdc.render();
    }

    var hoverDetail = new Rickshaw.Graph.HoverDetail({graph: rdc});

    window.addEventListener('resize', rdc_resize);

    rdc_resize();
}

function draw_dashboard_graphs(d1, d2) {
    var dash_graph = new Rickshaw.Graph( {
            element: document.getElementById("dashboard-chart"),
            renderer: 'area',
            width: $("#dashboard-chart").width(),
            height: 250,
            series: [
                {color: "#1FCC7B", data: data_to_rickshaw(d1), name: 'Estimated Market Value'},
                {color: "#F6BB42", data: data_to_rickshaw(d2), name: 'Estimated Market Volume'}
            ],
    });

    var graph_resizer = function() {
        dash_graph.configure({
                width: $("#dashboard-chart").width(),
                height: $("#dashboard-chart").height()
        });

        dash_graph.render();
    }

    var formatter = function(series, x, y) {
            var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>';
            var content = series.name + ": " + parseInt(y).toLocaleString() + '<br>' + date;
            return content;
        }

    var dash_graph_hover = new Rickshaw.Graph.HoverDetail( {
        graph: dash_graph,
        formatter: formatter
    });

    window.addEventListener('resize', graph_resizer);
    graph_resizer();
}

function draw_generic_graph(el, name, data) {
    var graph = new Rickshaw.Graph( {
            element: document.getElementById(el),
            renderer: 'line',
            interpolation: 'linear',
            min: 0,
            height: 250,
            padding: {top: .08},
            series: [
                {color: "#1FCC7B", data: data_to_rickshaw(data), name: name}
            ]
    });

    new Rickshaw.Graph.Axis.Time({graph: graph}).render();

    var formatter = function(series, x, y) {
        var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>';
        var content = series.name + ": " + y.toLocaleString() + '<br>' + date;
        return content;
    }

    new Rickshaw.Graph.HoverDetail( {
        graph: graph,
        formatter: formatter
    });

    var resize_eve = function() {
        graph.configure({
                width: $("#"+el).width(),
                height: $("#"+el).height()
        });
        graph.render();
    }

    window.addEventListener('resize', resize_eve);
    resize_eve();
}

function draw_item_graph(d1, d2) {
    var graph_value = new Rickshaw.Graph( {
            element: document.getElementById("item-graph-value"),
            renderer: 'line',
            interpolation: 'linear',
            min: 0,
            height: 250,
            padding: {top: .08},
            series: [
                {color: "#1FCC7B", data: data_to_rickshaw(d1), name: 'Value'}
            ]
    });

    var graph_volume = new Rickshaw.Graph( {
            element: document.getElementById("item-graph-volume"),
            renderer: 'line',
            interpolation: 'linear',
            min: 0,
            height: 250,
            padding: {
                top: .08,
            },
            series: [
                {color: "#F6BB42", data: data_to_rickshaw(d2), name: 'Volume'}
            ]
    });

    new Rickshaw.Graph.Axis.Time({graph: graph_value}).render();
    new Rickshaw.Graph.Axis.Time({graph: graph_volume}).render();

    var formatter = function(series, x, y) {
        var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>';
        var content = series.name + ": " + y.toLocaleString() + '<br>' + date;
        return content;
    }

    new Rickshaw.Graph.HoverDetail( {
        graph: graph_value,
        formatter: formatter
    });

    new Rickshaw.Graph.HoverDetail( {
        graph: graph_volume,
        formatter: formatter
    });

    var resize_eve = function() {
        graph_value.configure({
                width: $("#item-graph-value").width(),
                height: $("#item-graph-value").height()
        });
        graph_value.render();

        graph_volume.configure({
                width: $("#item-graph-volume").width(),
                height: $("#item-graph-volume").height()
        });
        graph_volume.render();
    }

    $(document).on("shown.bs.tab", resize_eve);
    window.addEventListener('resize', resize_eve);
    resize_eve();
}
