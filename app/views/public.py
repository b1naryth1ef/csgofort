from flask import Blueprint, render_template

public = Blueprint("public", __name__)

@public.route("/")
def public_route_index():
    return render_template("landing.html")