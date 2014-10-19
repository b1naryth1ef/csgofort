
var JST = {
    alert: _.template('<div class="col-md-12"><div class="alert alert-<%= type %>">' +
        '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' +
        '<%= msg %></div></div>')
}

var app = {
    templates: {},
    realms: {}
}

app.new_realm = function(name, obj) {
    app.realms[name] = $.extend({
        app: app,
        name: name,
        routes: {},
        setup: function () {},
        route: function(f) {
            _.each(Array.prototype.slice.apply(arguments).slice(1), function (v) {
                this.routes[v] = f;
            }, this);
        }
    }, obj);

    return app.realms[name];
}

app.run = function(route) {
    $.ajax("http://maz."+ CONFIG.DOMAIN +"/api/symbol", {
        data: {
            "cur": CONFIG.USER.cur
        },
        success: function (data) {
            CONFIG.SYM = data.symbol;
        }
    })

    // Simple URL parser :^|
    var parser = document.createElement('a');
    parser.href = route;
    parser.realm = parser.hostname.split(".", 1);

    // Check if realm exists
    if (!this.realms[parser.realm]) {
        console.log("ERROR: cannot find realm handler with name `"+parser.realm+"`.");
        return;
    }

    // Setup the realm
    realm = this.realms[parser.realm];
    realm.setup();

    // Special case for index page
    if (!parser.pathname || parser.pathname === "/") {
        return realm.index();
    }

    // Pattern match the route
    for (k in realm.routes) {
        var q = parser.pathname.match(new RegExp(k));
        if (q && q.length) {
            console.log("Matched: "+k);
            realm.routes[k].apply(realm, q.slice(1));
            return;
        }
    }

    console.log("ERROR: cannot find route handler with name `"+parser.pathname+"`.");
}

// Pushes a frontend alert
app.alert = function(msg, type) {
    if (type === undefined) {
        type = "danger";
    }
    $("#alerts").append(JST.alert({
        "msg": msg,
        "type": type
    }))
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

app.template = function(t, args) {
    args["CONFIG"] = CONFIG;
    args["app"] = app;

    return t(args);
}

app.get_avatar_for = function(sid) {
    return "http://auth."+CONFIG.DOMAIN+"/avatar/"+sid;
}

