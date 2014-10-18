from flask import Blueprint, render_template, request, jsonify, g, redirect
from util import build_url, APIError, convert_steamid32, reraise
# from datetime import datetime, timedelta
from vacdb import VacList, VacID, steam

vactrak = Blueprint("vactrak", __name__, subdomain="vactrak")

NEED_LOGIN = APIError("Must be logged in to track steam ids!")

@vactrak.route("/")
def vac_route_index():
    return render_template("vac/index.html")

@vactrak.route("/tracked/<id>")
def vac_route_user(id):
    try:
        v = VacID.get(VacID.id == id)
    except VacID.DoesNotExist:
        return "Invalid VacID entry!", 404

    return render_template("vac/single.html", v=v)

@vactrak.route("/tracked")
def vac_route_tracked():
    if not g.user:
        redirect(build_url("auth", "login"))

@vactrak.route("/top")
def vac_route_top(): pass

@vactrak.route("/api/track")
def vac_route_track():
    if not g.user:
        raise NEED_LOGIN

    if not 'ids' in request.values:
        raise APIError("Must provide list of steam ids to track!")

    try:
        v = VacList.get(VacList.user == g.user)
    except VacList.DoesNotExist:
        v = VacList()
        v.user = g.user

    if not v.active:
        raise APIError("VacList not active!")

    added = []

    for id in request.values.get("ids").split(","):
        if id.startswith("STEAM_"):
            id = convert_steamid32(id)
        elif id.isdigit():
            id = int(id)
        else:
            id = steam.getFromVanity(id)
            if not id: continue

        try:
            q = VacID.get(VacID.steamid == int(id))
        except VacID.DoesNotExist:
            q = VacID()
            q.steamid = id

            # Try to grab the latest data, otherwise fail but still save
            try:
                q.crawl()
            except:
                q.save()

        if q.id in v.tracked: continue

        # TODO: atomic
        v.tracked.append(q.id)
        added.append(q.get_nickname())

    try:
        v.validate()
    except Exception, e:
        reraise(APIError("Error Adding Tracked ID's: %s" % e))
    v.save()

    return jsonify({"success": True, "added": added})

@vactrak.route("/api/untrack/<id>")
def vac_route_untrack(id):
    if not g.user:
        raise NEED_LOGIN

    try:
        vl = VacList.select(VacList.id).where(VacList.user == g.user).get()
    except VacList.DoesNotExist:
        raise APIError("You do not have any tracked users")

    # Atomic operation to remove this ID from the VacList
    vl.remove(id)
    return jsonify({"success": True})

@vactrak.route("/api/info")
def vac_route_list():
    if not g.user:
        raise NEED_LOGIN

    try:
        li = VacList.get(VacList.user == g.user)
    except VacList.DoesNotExist:
        return jsonify({
            "sucess": True,
            "result": {}
        })

    return jsonify({
        "success": True,
        "result": li.toDict()
    })
