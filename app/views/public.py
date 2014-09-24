from flask import Blueprint

public = Blueprint("public", __name__)

@public.route("/")
def public_route_index():
    return "Hello World!"