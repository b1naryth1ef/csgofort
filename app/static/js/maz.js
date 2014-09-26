maz = {
    search_xhr: null
}

var search_result_template = _.template('<a href="/item/<%= obj.id %>"  class="list-item" style="height: 60px; overflow: hidden;">'+
    '<div class="list-item-content"><img height="64px" src="/image/<%= obj.id %>" class="img-circle pull-left"><h1><%= obj.data.name %></h3>'+
    '</div></a>');

function run(route) {
    maz.setup_search();

    if (route === "" || route === "/") {
        maz.run_market_index()
    } else if (route === "/api") {
        maz.run_api_docs()
    } else if (route.lastIndexOf("/item", 0) === 0) {
        maz.run_item()
    }
}

maz.run_api_docs = function() {
    
}

maz.run_item = function () {
    $.ajax("/api/item/"+ITEM_ID+"/graph/value", {
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
                $("#community-alert").fadeIn();
            }

            $("#stat-unique").text(data.total_items.toLocaleString());
            $("#stat-listed").text(data.total_listings.toLocaleString());
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
            min: 50,
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
