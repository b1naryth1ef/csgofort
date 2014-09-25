from flask import Blueprint, render_template, g

public = Blueprint("public", __name__)

@public.route("/")
def public_route_index():
    if not g.user:
        return render_template("landing.html")

    return render_template("index.html")

