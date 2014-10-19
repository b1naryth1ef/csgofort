from flask import Blueprint, render_template, jsonify, g, redirect
from util import build_url, APIError, convert_steamid32, requires
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

@vactrak.route("/api/search")
@requires("q")
def vac_route_track(q):
    if not g.user:
        raise NEED_LOGIN

    if q.startswith("STEAM_"):
        q = convert_steamid32(q)
    elif q.isdigit():
        q = int(q)
    else:
        q = int(steam.getFromVanity(q) or 0)
        if not q:
            return jsonify({
                "success": True,
                "result": None
            })

    try:
        v = VacID.get(VacID.steamid == q)
    except VacID.DoesNotExist:
        v = VacID()
        v.steamid = q
        try:
            v.crawl()
        except:
            raise APIError("Invalid SteamID")
        v.save()

    return jsonify({
        "success": True,
        "result": v.id
    })

@vactrak.route("/api/track/<id>")
def vac_route_track_id(id):
    if not g.user:
        raise NEED_LOGIN

    try:
        vl = VacList.select(VacList.id).where(VacList.user == g.user).get()
    except VacList.DoesNotExist:
        raise APIError("You do not have any tracked users")

    try:
        assert VacID.select().where(VacID.id == id).count() == 1
    except:
        raise APIError("Invalid VacID id")

    # Atomic operation to add this ID to the VacList
    vl.append(int(id))
    return jsonify({"success": True})

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
def vac_route_info_all():
    if not g.user:
        raise NEED_LOGIN

    try:
        li = VacList.get(VacList.user == g.user)
    except VacList.DoesNotExist:
        raise APIError("No VacList for current user!")

    return jsonify({
        "success": True,
        "result": li.toDict()
    })

@vactrak.route("/api/info/<id>")
def vac_route_info_single(id):
    try:
        i = VacID.get(VacID.id == id)
    except VacID.DoesNotExist:
        raise APIError("Invalid VacID id")

    return jsonify({"success": True, "result": i.toDict()})

@vactrak.route("/api/info/tracked")
def vac_route_info_tracked():
    if not g.user:
        raise NEED_LOGIN

    try:
        li = VacList.select(VacList.tracked).where(VacList.user == g.user).get()
    except VacList.DoesNotExist:
        raise APIError("No VacList for current user!")

    return jsonify({
        "success": True,
        "result": li.tracked
    })
