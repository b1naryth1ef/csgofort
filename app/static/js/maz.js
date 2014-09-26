function run(route) {
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
        success: function(data) {
            if (data.success) {
                draw_dashboard_graphs(data.data);
            } else {
                console.log("Failed to load market value graph");
            }
        }
    })

    $.ajax("/api/info", {
        success: function(data) {
            if (!data.success) {
                return console.log("Failed to load market info");
            }

            $("#stat-unique").text(data.total_items.toLocaleString());
            $("#stat-listed").text(data.total_listings.toLocaleString());
            $("#stat-value").text(data.value.toLocaleString());
            $("#stats").fadeIn();
        }
    })
}

function draw_dashboard_graphs(data) {
    key = ["x"].concat(_.keys(data))
    val = ["value"].concat(_.values(data))

    c3.generate({
        bindto: '#market_value',
        data: {
            x: 'x',
            columns: [
                key,
                val
            ],
            types: {
                'value': 'line'
            }
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    culling: false,
                    fit: true,
                    format: "%A %B %d"
                }
            },
            y : {
                tick: {
                    format: d3.format("$,")
                }
            }
        },
        point: {
            r: '4',
            focus: {
                expand: {
                    r: '5'
                }
            }
        },
        bar: {
            width: {
                ratio: 0.4 // this makes bar width 50% of length between ticks
            }
        },
        grid: {
            x: {
                show: true
            },
            y: {
                show: true
            }
        },
        color: {
            pattern: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        }
    });

        $(window).on("debouncedresize", function() {
            c3_7_days_chart.resize();
        });
}