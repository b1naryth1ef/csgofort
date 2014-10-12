from flask import Blueprint, render_template, request, jsonify, g, redirect
from util import build_url, APIError, convert_steamid, reraise
from datetime import datetime, timedelta
from vacdb import VacList, VacID

vactrak = Blueprint("vactrak", __name__, subdomain="vactrak")

NEED_LOGIN = APIError("Must be logged in to track steam ids!")

@vactrak.route("/")
def vac_route_index():
    return render_template("vac/index.html")

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

    # TOOD: validate steamids plz
    for id in request.values.get("ids").split(","):
        if ':' in id:
            id = convert_steamid(id)

        try:
            q = VacID.get(VacID.steamid == int(id))
        except VacID.DoesNotExist:
            q = VacID()
            q.steamid = id
            q.last_crawl = datetime.utcnow() - timedelta(days=30)
            q.save()

        if q.id in v.tracked: continue
        v.tracked.append(q.id)

    try:
        v.validate()
    except Exception, e:
        reraise(APIError("Error Adding Tracked ID's: %s" % e))
    v.save()

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
