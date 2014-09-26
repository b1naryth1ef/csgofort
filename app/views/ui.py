from flask import Blueprint, render_template

ui = Blueprint("ui", __name__, subdomain="ui")

@ui.route("/itemselection")
def ui_route_item_selection():
    return render_template("ui/selection.html")