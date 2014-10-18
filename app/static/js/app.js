
var JST = {
    alert: _.template('<div class="col-md-12"><div class="alert alert-<%= type %>">' +
        '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' +
        '<%= msg %></div></div>')
}

var app = {
    templates: {}
}

app.alert = function(msg, type) {
    if (type === undefined) {
        type = "danger";
    }
    $("#alerts").append(JST.alert({
        "msg": msg,
        "type": type
    }))
}

app.setup = function() {}

app.run = function(route) {
    $.ajax("http://maz."+ CONFIG.DOMAIN +"/api/symbol", {
        data: {
            "cur": CONFIG.USER.cur
        },
        success: function (data) {
            CONFIG.SYM = data.symbol
        }
    })

    app.setup();
    run(route);
}

// Sorts a table by the value
app.sortTable = function(table, order) {
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

app.convert = function(value, f, async) {
    if (CONFIG.USER.cur === "USD") {
        return value;
    }

    $.ajax("http://maz."+ CONFIG.DOMAIN +"/api/convert", {
        async: async || true,
        data: {
            from: "USD",
            to: CONFIG.USER.cur,
            value: value
        },
        success: function(data) {
            f(data.value)
        }
    })
}
