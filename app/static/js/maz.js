function run(route) {
    console.log(1)
    if (route === "" || route === "/") {
        run_market_index()
    } else if (route === "/api") {
        run_api_docs()
    }
}

function run_api_docs() {
    
}

function run_market_index() {
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