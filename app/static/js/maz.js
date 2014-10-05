
var maz = {
    search_xhr: null,

}

var search_result_template = _.template('<a href="/item/<%= obj.id %>"  class="list-item" style="height: 60px; overflow: hidden;">'+
    '<div class="list-item-content"><img height="64px" src="/image/<%= obj.id %>" class="img-circle pull-left"><h1><%= obj.data.name %></h3>'+
    '</div></a>');

var inventory_row_template = _.template('<tr value="<%= value * 100 %>"><td><a href="/item/<%= id %>"><%= name %></a></td><td>$<%= value %></td></tr>');

var changelog_row_template = _.template('<li class="list-group-item"><span class="<%= icon %>"></span> <%= msg %></li>')

// The entry point for all maz routes
function run(route) {
    maz.setup_search();

    if (route === "" || route === "/") {
        maz.run_market_index();
    } else if (route === "/api") {
        maz.run_api_docs();
    } else if (route.lastIndexOf("/item", 0) === 0) {
        maz.run_item();
    } else if (route === "/value") {
        maz.run_value();
    } else if (route === "/inventory") {
        maz.run_inventory();
    }
}

// Runs the inventory view
maz.run_inventory = function () {
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
}

maz.load_tracking_info = function () {
    $.ajax("/api/tracking/"+CONFIG.USER+"/graph/value", {
        success: function (data) {
            draw_inventory_graphs(data.data)
        }
    })

    $.ajax("/api/tracking/"+CONFIG.USER+"/history", {
        success: function (data) {
            _.each(data.data, function (v, k) {
                _.each(v.added, function(v1, k1) {
                    $.ajax("/api/asset/" + v1.split("_")[0], {
                        success: function (added_data) {
                            $("#changelog").append(changelog_row_template({
                                msg: "Added " + added_data.market_hash_name,
                                icon: "glyphicon glyphicon-plus-sign"
                            }))
                        }
                    })
                })

                _.each(v.removed, function(v1, k1) {
                    $.ajax("/api/asset/" + v1.split("_")[0], {
                        success: function (added_data) {
                            $("#changelog").append(changelog_row_template({
                                msg: "Removed " + added_data.market_hash_name,
                                icon: "glyphicon glyphicon-minus-sign"
                            }))
                        }
                    })
                })

            })
        }
    })
}

maz.load_value_info = function() {
    $.ajax("http://auth." + CONFIG.DOMAIN + "/inventory/" + CONFIG.USER, {
        success: function (data) {
            if (!data.success) {
                app.alert("<strong>Uh Oh!</strong> We can't grab your inventory! Looks like either your inventory is private, or the steam community is having some problems.");
                return;
            }

            $.ajax("/api/items/bulk", {
                data: {
                    "ids": _.map(data.inv, function (v, k) {
                        return v.i
                    }).join(",")
                },
                success: function(data) {
                    var value = 0;

                    _.each(data.results, function(v, k) {
                        try {
                            var data = inventory_row_template({
                                name: v.name,
                                value: v.price.med,
                                id: v.id
                            })

                            $("#inv-body").append(data)

                            if (v.price.med > 0) {
                                value = value + v.price.med;
                            }
                        } catch (err) {}
                    })

                    $("#worth").text(Math.floor(value));
                    app.sortTable($("#inv-table"), 'desc');
                }
            })
        }
    })
}

maz.run_api_docs = function() {
    
}

maz.run_item = function () {
    $.ajax("/api/item/"+ITEM_ID+"/graph/median", {
        success: function(data) {
            draw_item_graph(data.data);
        }
    })
}

maz.run_market_index = function() {
    $.ajax("/api/graph/totalvalue", {
        success: function(d1) {
            $.ajax("/api/graph/totalsize", {
                success: function(d2) {
                    draw_dashboard_graphs(d1.data, d2.data);
                }
            })
        }
    })

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
            $("#stat-value").text(data.totals.value.toLocaleString());
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
            min: 0,
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

    $(document).on("shown.bs.tab", graph_resizer);
    window.addEventListener('resize', graph_resizer);     
    graph_resizer();
}

function draw_item_graph(data) {

    var rlc = new Rickshaw.Graph( {
            element: document.getElementById("charts-lines"),
            renderer: 'line',
            interpolation: 'linear',
            min: 0,
            height: 250,
            padding: {
                top: .08,
            },
            series: [{color: "#2f9fe0",data: data_to_rickshaw(data), name: 'Value'}]
    });

    rlc.render();    

    var axes = new Rickshaw.Graph.Axis.Time({graph: rlc});
    var hoverDetail = new Rickshaw.Graph.HoverDetail({graph: rlc});
    axes.render();

    var rlc_resize = function() {                
                rlc.configure({
                        width: $("#charts-lines").width(),
                        height: $("#charts-lines").height()
                });
                rlc.render();
        }

    window.addEventListener('resize', rlc_resize); 
    rlc_resize();
}
