var admin = {
    last_q_count: 0
}

var template_pg_relation = _.template('<tr value="<%= real %>"><td><%= name %></td><td><%= size %></td></tr>')

function run(route) {
    if (route === "" || route === "/") {
        admin.run_index();
    }
}

admin.run_index = function () {
    $.ajax("/api/stats", {
        success: function (data) {
            $("#stat-users").text(data.users)
        }
    })

    $.ajax("/api/postgres/status", {
        success: function (data) {
            _.each(data.relations, function (v, k) {
                $("#pg-relation-body").append(template_pg_relation(v))
            })
            app.sortTable($("#pg-relation-table"), 'desc');

            _.each(data.tables, function (v, k) {
                $("#pg-tsize-body").append(template_pg_relation(v))
            })
            app.sortTable($("#pg-tsize-table"), 'desc');
        }
    })



    admin.update_qps();
    setInterval(admin.update_qps, 3000);
}

admin.update_qps = function () {
    $.ajax("/api/postgres/queries", {
        success: function (data) {
            if (admin.last_q_count) {
                $("#stat-qps").text(
                    ((data.queries - admin.last_q_count) - 1)
                )
            }

            admin.last_q_count = data.queries;
        }
    })
}