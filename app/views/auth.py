"""
The auth views handle all user-related tasks. This includes logging in and
out of *all* services, and getting user information (such as profile-overview,
    avatars, etc)

"""

from flask import Blueprint, request, session, g, send_file
from database import User, red
from app import openid, csgofort
from util import flashy, build_url, steam

import requests
from cStringIO import StringIO

auth = Blueprint("auth", __name__, subdomain="auth")

@auth.route("/login")
@openid.loginhandler
def auth_route_login():
    if g.user is not None:
        return flashy("You are already logged in!", u=build_url("", ""))
    return openid.try_login('http://steamcommunity.com/openid')

@auth.route("/logout")
def auth_route_logout():
    if 'redirect' in request.values or "realm" in request.values:
        url = build_url(request.values.get("realm", ""), request.values.get("redirect", ""))
    else:
        url = build_url("", "")

    if g.user:
        del session['id']
        return flashy("You have been logged out!", "success", u=url)
    return flashy("You are not currently logged in!", u=url)

@openid.after_login
def create_or_login(resp):
    match = steam.steam_id_re.search(resp.identity_url)
    sid = match.group(1)

    # Attempt to get a current user, otherwise create them
    try:
        g.user = User.select(User.id, User.steamid).where(User.steamid == sid).get()
    except User.DoesNotExist:
        g.user = User(steamid=sid)
        g.user.save()

    # Set the sessionid and welcome the user back
    session['id'] = g.user.id
    return flashy("Welcome back %s!" % g.user.get_nickname(), "success", u=build_url("", ""))

@csgofort.before_request
def before_request():
    g.user = None

    if request.path.startswith("/static"):
        return

    if 'id' in session:
        try:
            g.user = User.get(User.id == session['id'])
        except User.DoesNotExist:
            return flashy("Your session is invalid!", "error", u=build_url("", ""))

@auth.route("/avatar/<int:id>")
def auth_route_avatar(id):
    try:
        u = User.select(User.steamid).where(User.id == id).get()
    except User.DoesNotExist:
        return "", 404

    key = "avatar:%s" % u.id
    if red.exists(key):
        buffered = StringIO(red.get(key))
    else:
        data = steam.SteamAPI.new().getUserInfo(u.steamid)

        try:
            r = requests.get(data.get('avatarfull'))
            r.raise_for_status()
        except:
            return "", 500

        # Cached for 15 minutes
        buffered = StringIO(r.content)
        red.setex(key, r.content, (60 * 15))

    buffered.seek(0)
    return send_file(buffered, mimetype="image/jpeg")