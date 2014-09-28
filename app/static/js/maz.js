maz = {
    search_xhr: null
}

var search_result_template = _.template('<a href="/item/<%= obj.id %>"  class="list-item" style="height: 60px; overflow: hidden;">'+
    '<div class="list-item-content"><img height="64px" src="/image/<%= obj.id %>" class="img-circle pull-left"><h1><%= obj.data.name %></h3>'+
    '</div></a>');

var inventory_row_template = _.template('<tr value="<%= value * 100 %>"><td><a href="/item/<%= id %>"><%= name %></a></td><td>$<%= value %></td></tr>');

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

function sortTable(table, order) {
    var asc   = order === 'asc',
        tbody = table.find('tbody');

    tbody.find('tr').sort(function(a, b) {
        if (asc) {
            return parseInt($(a).attr("value")) - parseInt($(b).attr("value"));
        } else {
            return parseInt($(b).attr("value")) - parseInt($(a).attr("value"));
        }
    }).appendTo(tbody);
}

maz.run_inventory = function () {
    maz.run_value();
    $.ajax("/api/tracking", {
        success: function (data) {
            if (!data.enabled) {
                $("#tracking-disabled").fadeIn();

                $("#tracking-enable-btn").click(function (ev) {
                    $(this).addClass("disabled");
                    $.ajax("/api/tracking/enable", {
                        success: function (d1) {
                            if (!d1.success) {
                                app.alert("We couldn't enable inventory tracking for your account! Please insure your inventory is public, and try again shortly!");
                            } else {
                                app.alert("Inventory Tracking Enabled!", "success");
                                $(this).removeClass("disabled");
                                $("#tracking-enabled").fadeIn();
                                $("#tracking-disabled").hide();
                            }
                        }
                    })
                });
            } else {
                $("#tracking-enabled").fadeIn();

                $("#tracking-disable-btn").click(function (ev) {
                    $(this).addClass("disabled");
                    $.ajax("/api/tracking/disable", {
                        success: function(d1) {
                            app.alert("Inventory Tracking Disabled!", "success");
                            $(this).removeClass("disabled");
                            $("#tracking-disabled").fadeIn();
                            $("#tracking-enabled").hide();
                        }
                    })
                })

                $.ajax("/api/tracking/history", {
                    success: function (data) {
                        draw_inventory_graphs(data.data)
                    }
                })
            }
        }
    })
}

maz.run_value = function() {
    var value = 0;
    var finished = 0;

    $.ajax("http://auth." + CONFIG.DOMAIN + "/inventory/" + CONFIG.USER, {
        success: function (data) {
            if (!data.success) {
                app.alert("We can't grab your inventory! Looks like either your inventory is private, or the steam community is having some problems.");
                return;
            }

            _.each(data.inv, function (v, k) {
                $.ajax("/api/item/" + v.i, {
                    complete: function() {
                        finished++;

                        if (finished >= data.inv.length) {
                            sortTable($("#inv-table"), 'desc');
                        }
                    },
                    success: function(idd) {
                        try {
                            var data = inventory_row_template({
                                name: idd.item.name,
                                value: idd.item.price.med,
                                id: idd.item.id
                            })

                            $("#inv-body").append(data)

                            if (idd.item.price.med > 0) {
                                value = value + idd.item.price.med;
                            }

                            $("#worth").text(Math.floor(value));
                        } catch (err) {}
                    }
                })
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
            draw_dashboard_graphs(d1.data);
        }
    })

    $.ajax("/api/info", {
        success: function(data) {
            if (!data.success) {
                return console.log("Failed to load market info");
            }

            if (data.community > 0) {
                app.alert("The Steam Community is experiencing some issues right now! This may effect the stability, accuracy and reliability of CS:GO Fort and it's services.");
            }

            $("#stat-unique").text(data.totals.items.toLocaleString());
            $("#stat-listed").text(data.totals.listings.toLocaleString());
            $("#stat-value").text(data.value.toLocaleString());
            $("#stats").fadeIn();
        }
    })
}

maz.setup_search = function() {
    $("#top-search").keydown(function (ev) {
        console.log(ev);
        if (this.search_xhr) {
            this.search_xhr.abort();
            this.search_xhr = null;
        }

        var val = $("#top-search-box").val() + String.fromCharCode(ev.which);
        if (!val) {
            $("#top-search-drop").addClass("closed")
            $("#top-search-drop").removeClass("open")
            return;
        }

        this.search_xhr = $.ajax("/api/search", {
            data: {
                name: val
            },
            success: function (data) {
                $("#search-results").empty()

                var count = 0;
                _.each(data.results, function (v, k) {
                    if (count > 10) return;
                    if (v.score < 2) return;
                    count++
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
    var dat = [], inc = 0;
    _.each(data, function (v, k) {
        inc++;
        dat.push({
            x: inc,
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

function draw_dashboard_graphs(d1) {
    var rdc = new Rickshaw.Graph( {
            element: document.getElementById("dashboard-chart"),
            renderer: 'area',
            width: $("#dashboard-chart").width(),
            height: 250,
            series: [
                {color: "#2f9fe0", data: data_to_rickshaw(d1), name: 'Estimated Market Value'},
            ],
    } );

    rdc.render();

    var rdc_resize = function() {                
            rdc.configure({
                    width: $("#dashboard-chart").width(),
                    height: $("#dashboard-chart").height()
            });
            rdc.render();
    }

    var hoverDetail = new Rickshaw.Graph.HoverDetail({graph: rdc});

    window.addEventListener('resize', rdc_resize);        

    rdc_resize();
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
