"""
The auth views handle all user-related tasks. This includes logging in and
out of *all* services, and getting user information (such as profile-overview,
    avatars, etc)

"""

from flask import Blueprint, request, session, g, send_file, jsonify, render_template, redirect

# DB
from database import red
from fortdb import User

from app import openid, csgofort
from util import flashy, build_url, steam, APIError
from flask.ext.cors import cross_origin

import requests, json
from cStringIO import StringIO

auth = Blueprint("auth", __name__, subdomain="auth")

@auth.route("/")
def auth_render_index():
    if not g.user:
        return redirect(build_url("auth", "login"))
    return render_template("settings.html")

@auth.route("/login")
@openid.loginhandler
def auth_route_login():
    if g.user is not None:
        return flashy(u"You are already logged in!", u=build_url("", ""))

    return openid.try_login('http://steamcommunity.com/openid')

@auth.route("/logout")
def auth_route_logout():
    if 'redirect' in request.values or "realm" in request.values:
        url = build_url(request.values.get("realm", ""), request.values.get("redirect", ""))
    else:
        url = build_url("", "")

    if g.user:
        del session['id']
        return flashy(u"You have been logged out!", "success", u=url)
    return flashy(u"You are not currently logged in!", u=url)

@openid.after_login
def create_or_login(resp):
    match = steam.steam_id_re.search(resp.identity_url)
    sid = match.group(1)

    # Attempt to get a current user, otherwise create them
    try:
        g.user = User.select(User.id, User.steamid).where(User.steamid == sid).get()
    except User.DoesNotExist:
        g.user = User(steamid=sid)

        # HARDCOODE PARKOURRR
        if sid == "76561198037632722":
            g.user.level = User.Level.ADMIN

        g.user.save()

    # Set the sessionid and welcome the user back
    session['id'] = g.user.id

    return flashy(u"Welcome back %s!" % g.user.get_nickname(), "success", u=openid.get_next_url())

@csgofort.before_request
def before_request():
    g.user = None

    if request.path.startswith("/static"):
        return

    if 'id' in session:
        try:
            g.user = User.get(User.id == session['id'])
        except User.DoesNotExist:
            return flashy(u"Your session is invalid!", "error", u=build_url("", ""))

@auth.route("/avatar/<int:id>")
def auth_route_avatar(id):
    key = "avatar:%s" % id
    if red.exists(key):
        buffered = StringIO(red.get(key))
    else:
        data = steam.SteamAPI.new().getUserInfo(id)

        try:
            r = requests.get(data.get('avatarfull'))
            r.raise_for_status()
        except Exception:
            return "", 500

        # Cached for 1 hour
        buffered = StringIO(r.content)
        red.setex(key, r.content, (60 * 60))

    buffered.seek(0)
    return send_file(buffered, mimetype="image/jpeg")

def get_safe_inventory(user):
    try:
        item_data = steam.SteamMarketAPI(730).get_parsed_inventory(user.steamid)

        # Cached for 1 hour
        red.setex("inv:%s" % user.id, json.dumps(item_data), 60 * 60)
    except Exception:
        if not red.exists("inv:%s" % user.id):
            return jsonify({
                "success": False,
                "error": "Steam API is down, and no cached inventory is availbile!"
            })

        return jsonify({
            "success": True,
            "cached": True,
            "age": (60 * 60) - red.ttl("inv:%s" % user.id),
            "inv": json.loads(red.get("inv:%s" % user.id))
        })

    return jsonify({
        "success": True,
        "cached": False,
        "inv": item_data
    })

@auth.route("/settings")
def auth_settings():
    if not g.user:
        raise APIError("No Session")

    g.user.currency = request.values.get("currency", g.user.currency)

    try:
        g.user.save()
    except Exception:
        raise APIError("Invalid Data")

    return jsonify({"success": True})

@auth.route("/inventory/<int:id>", methods=["GET", "OPTIONS"])
@auth.route("/inventory", methods=["GET", "OPTIONS"])
@cross_origin(send_wildcard=True)
def auth_route_inventory(id=None):
    if not id and not g.user:
        return "", 400
    elif not id:
        id = g.user.id

    try:
        u = User.select(User.steamid).where(User.id == id).get()
    except User.DoesNotExist:
        return "", 404

    return get_safe_inventory(u)
