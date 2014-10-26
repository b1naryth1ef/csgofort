var auth = app.new_realm("auth", {});

var currency_row_template = _.template('<option value="<%= name %>" <% if (sel) { %>selected="selected"<% } %>><%= name %></option>')

auth.index = function () {
    $.ajax("http://maz."+ CONFIG.DOMAIN +"/api/currencies", {
        success: function (data) {
            _.each(data.result, function (v, k) {
                $("#currency").append(currency_row_template({name: v, sel: CONFIG.USER.cur == v}))
            })
        }
    })

    $("#save").click(function (ev) {
        $.ajax("/settings", {
            data: {
                "currency": $("#currency").val()
            },
            success: function (data) {
                if (data.success) {
                    app.alert("Saved!", "success")
                } else {
                    app.alert("Error Saving!", "danger")
                }
            }
        })
    })
}

