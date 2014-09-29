var admin = {
    last_q_count: 0,
    users_page: 1,
    edit_user_id: null,
}

var template_pg_relation = _.template('<tr value="<%= real %>"><td><%= name %></td><td><%= size %></td></tr>')
var template_users_row = _.template(
    '<tr data-id="<%= id %>"><td><%= id %></td><td><%= steamid %></td><td><%= nickname %></td><td><%= level %></td>' +
    '<td><button class="btn btn-default"><i class="fa fa-pencil"></i></button></td></tr>'
)

function run(route) {
    if (route === "" || route === "/") {
        admin.run_index();
    } else if (route === "/users") {
        admin.run_users();
    }
}

admin.run_users = function() {
    $("#users-table").delegate(".btn", "click", function (ev) {
        ev.stopImmediatePropagation();
        admin.edit_user_id = $(this).parent().parent().data("id");

        $("#user-modal").modal("show");
    })

    $.ajax("/api/users", {
        data: {
            page: admin.users_page
        },
        success: function (data) {
            _.each(data.users, function (v, k) {
                $("#users-body").append(template_users_row(v))
            })
        }
    })
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