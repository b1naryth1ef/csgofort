from flask import Blueprint, request, jsonify, render_template, send_file, g, redirect
from mazdb import *
from manalytics import *
from collections import Counter
from cStringIO import StringIO
from util import build_url

import json, random, functools, requests

import datetime
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta

maz = Blueprint("maz", __name__, subdomain="maz")

with open("maz/API.json", "r") as f:
    API_DOCS = json.load(f)

RATE_LIMIT_UPPER = 5000

@maz.before_request
def before_maz_request():
    """
    This function handles API rate limiting.
    """
    KEY = "maz:limit:%s" % request.remote_addr

    # API rate limiting
    if red.exists(KEY):
        if int(red.get(KEY)) > RATE_LIMIT_UPPER:
            res = jsonify({
                "success": False,
                "error": "Rate limit hit!",
                "ttl": red.ttl(KEY)
            })
            res.status_code = 429
            return res
        red.incr(KEY, 1)
    else:
        red.setex(KEY, 1, 5 * 60)

@maz.route("/")
def maz_route_index():
    return render_template("maz/index.html")

@maz.route("/inventory")
def maz_route_inventory():
    if not g.user:
        return redirect(build_url("auth", "login") + "?next=" + build_url("maz", "inventory"))
    return render_template("maz/inventory.html")

@maz.route("/item/<id>")
def maz_route_item(id):
    try:
        mi = MarketItem.select().where(MarketItem.id == id).get()
        mi.mipp = mi.get_latest_mipp()
    except MarketItem.DoesNotExist:
        return "", 404

    family = []
    for entry in mi.get_family_items():
        entry.mipp = entry.get_latest_mipp()
        family.append(entry)

    family = list(reversed(sorted(family, key=lambda i: i.mipp.median)))

    return render_template("maz/item.html", item=mi, family=family)

@maz.route("/image/<id>")
def maz_route_item_image(id):
    try:
        u = MarketItem.select(MarketItem.id, MarketItem.image).where(MarketItem.id == id).get()
    except MarketItem.DoesNotExist:
        return "", 404

    key = "itemimg:%s" % u.id
    if red.exists(key):
        buffered = StringIO(red.get(key))
    else:
        try:
            r = requests.get(u.image)
            r.raise_for_status()
        except:
            return "", 500

        # Cached for 12 hours
        buffered = StringIO(r.content)
        red.setex(key, r.content, (60 * 60 * 12))

    buffered.seek(0)
    return send_file(buffered, mimetype="image/jpeg")

@maz.route("/api")
def maz_route_api():
    return render_template("maz/api.html", docs=API_DOCS)

@maz.route("/api/status")
def maz_route_status():
    # TODO: pipeline?
    return jsonify({
        "success": True,
        "quota": red.get("maz:limit:%s" % request.remote_addr),
        "ttl": red.ttl("maz:limit:%s" % request.remote_addr),
    })

@maz.route("/api/info")
def maz_route_info():
    """
    Returns information about the global dataset
    """
    latest = get_latest_mipps()
    
    payload = {
        "totals": {
            "items": MarketItem.select().count(),
            "mipp": MarketItemPricePoint.select().count(),
            "mippdaily": MIPPDaily.select().count(),
            "listings": sum(map(lambda i: i.volume if i.volume > 0 else 0, list(latest))),
        },
        "value": get_market_value_total_now(),
        "status": {
            "api": 0,
            "community": int(red.get("maz:community_status") or 0),
        },
        "success": True
    }

    return jsonify(payload)

@maz.route("/api/items")
def maz_route_items():
    """
    A paginated endpoint for listing all items on the maz
    """
    page = int(request.values.get("page", 1))
    per_page = int(request.values.get("per_page", 10))
    per_page = per_page if per_page <= 100 else 100

    results = map(lambda i: i.toDict(), list(MarketItem.select().order_by(MarketItem.id).paginate(page, per_page)))

    return jsonify({
        "results": results,
        "size": len(results),
        "success": True
    })

@maz.route("/api/item/<id>")
def maz_route_api_item(id):
    """
    Returns information for a single item given a steam-market name or
    internal ID
    """
    try:
        if id.isdigit():
            mi = MarketItem.get(MarketItem.id == id)
        else:
            mi = MarketItem.get(MarketItem.name == id)
    except MarketItem.DoesNotExist:
        return jsonify({
            "success": False,
            "error": "Invalid Item ID!"
        })

    return jsonify({
        "success": True,
        "item": mi.toDict(),
    })

@maz.route("/api/item/<id>/history")
def maz_route_history(id):
    """
    Returns a set of historical pricing data given the items internal ID
    """
    try:
        mi = MarketItem.get(MarketItem.id == id)
    except MarketItem.DoesNotExist:
        return jsonify({
            "success": False,
            "error": "Invalid Item ID!"
        })

    q = MarketItemPricePoint.select().where(
        MarketItemPricePoint.item == mi).order_by(
            MarketItemPricePoint.time.desc())
    q = list(q)

    return jsonify({
        "prices": map(lambda i: i.toDict(), q),
        "trend": identify_trend(q),
        "success": True,
    })

@maz.route("/api/removed")
def maz_route_removed():
    """
    Returns a list of items that have been removed from the market
    """
    page = int(request.values.get("page", 1))
    per_page = int(request.values.get("per_page", 10))
    per_page = per_page if per_page <= 100 else 100

    # items that are more than 10 days old
    ten_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=10)
    q = MarketItem.select().where(MarketItem.last_crawl <= ten_days_ago)
    results = map(lambda i: i.toDict(), q.paginate(page, per_page))

    return jsonify({
        "results": results,
        "size": len(results),
        "success": True
    })

@maz.route("/api/aggregate")
def maz_route_aggregate():
    """
    Returns aggergation data based on wear, skin, item, and stattrack.
    """
    wear = request.values.get("wear")
    skin = request.values.get("skin")
    item = request.values.get("item")
    stat = request.values.get("stat")

    parts = []

    if wear:
        parts.append((MarketItem.wear == wear))

    if skin:
        parts.append((MarketItem.skin == skin))

    if item:
        parts.append((MarketItem.item == item))

    if stat is not None:
        parts.append((MarketItem.stat == bool(stat)))

    if not len(parts):
        return jsonify({
            "success": False,
            "error": "No Query!"
        })

    results = list(MarketItem.select().where(reduce(lambda a, b: a & b, parts)))
    results_enc = map(lambda i: i.toDict(), results)

    mipps = filter(lambda i: i is not None, map(lambda i: i.get_latest_mipp(), results))

    average_price = sum(map(lambda i: i.median, mipps)) / len(results)
    volume = sum(map(lambda i: i.volume, mipps))

    wear = Counter(map(lambda i: i.wear, results))
    skin = Counter(map(lambda i: i.skin, results))
    item = Counter(map(lambda i: i.item, results))
    stat = len(filter(lambda i: i.stat, results))

    return jsonify({
        "info": {
            "average_price": average_price,
            "per_wear": wear,
            "per_skin": skin,
            "per_item": item,
            "stat": stat,
            "volume": volume
        },
        "results": results_enc,
        "size": len(results_enc),
        "success": True
    })

# TODO: cache this one! aggregate this!
@maz.route("/api/pricechanges")
def maz_route_pricechanges():
    # Last 30 minutes
    default_time_window = datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 30)

    drops = []

    for mi in MarketItem.select():
        q = MarketItemPricePoint.select().where(
            (MarketItemPricePoint.item == mi) &
            (MarketItemPricePoint.time >= default_time_window)
        ).order_by(MarketItemPricePoint.time.desc())
        
        if q.count() != 2:
            continue

        q = list(q)

        window = q[-1].median * .30

        diff = q[0].median - q[-1].median
        if abs(diff) >= window:
            if diff > 0:
                drops.append({
                    "id": mi.id,
                    "type": "rise",
                    "change": diff
                })
            else:
                drops.append({
                    "id": mi.id,
                    "type": "drop",
                    "change": diff
                })

    return jsonify({
        "success": True,
        "drops": drops
    })

def dategraph(f):
    @functools.wraps(f)
    def deco(*args, **kwargs):
        res = request.values.get("res", "month")
        if res not in ("week", "month", "year"):
            return jsonify({
                "error": "Invalid Data Resolution!",
                "success": False
            })

        if res == "week":
            ruleset = rrule(DAILY, count=7, dtstart=datetime.datetime.utcnow() - datetime.timedelta(days=6))

        if res == "month":
            ruleset = rrule(DAILY, count=30, dtstart=datetime.datetime.utcnow() - datetime.timedelta(days=29))

        if res == "year":
            ruleset = rrule(MONTHLY, count=12, dtstart=datetime.datetime.utcnow() - relativedelta(months=11))

        return f(ruleset, *args, **kwargs)
    return deco


@maz.route("/api/graph/totalvalue")
@dategraph
def maz_route_value_total(rule):
    """
    Returns a graph of the total market value given a resolution
    """

    data = {}
    for dt in list(rule)[:-1]:
        # start = dt - datetime.timedelta(days=1)
        # get_market_value_total(start, dt)
        data[int(dt.strftime('%s'))] = get_market_value_total_day(dt)

    return jsonify({
        "data": data,
        "success": True
    })

@maz.route("/api/graph/listings")
@dategraph
def maz_route_listings(rule):
    data = {}
    for dt in rule:
        data[int(dt.strftime('%s'))] = random.randint(100000, 999999)

    return jsonify({
        "data": data,
        "success": True,
    })

@maz.route("/api/item/<id>/graph/<attrib>")
@dategraph
def maz_route_item_graph_value(rule, id, attrib):
    try:
        mi = MarketItem.get(MarketItem.id == id)
    except MarketItem.DoesNotExist:
        return jsonify({
            "success": False,
            "error": "Invalid Item ID!"
        })

    data = {}
    for dt in list(rule)[:-1]:
        try:
            val = getattr(mi.get_daily_mipp(dt), attrib, 0)
        except:
            val = 0
        data[int(dt.strftime('%s'))] = val

    return jsonify({
        "data": data,
        "success": True,
    })


SEARCH_ATTRIBS = ["name", "skin", "wear", "item"]

@maz.route("/api/search")
def maz_route_search():
    query = {
        attrib: request.values.get(attrib) + "*" for attrib in SEARCH_ATTRIBS if attrib in request.values
    }

    if not query:
        return jsonify({
            "success": False,
            "error": "You must specifiy a search query!"
        })

    result = es.search(
        index='marketitems',
        doc_type='marketitem',
        body={
            'query': {
                'filtered': {
                    'query': {
                        'match': query
                    },
                }
            },
            "size": 25
        }
    )

    if result['hits']['total']:
        results = map(lambda i: {
            "id": i["_id"],
            "data": i["_source"],
            "score": i["_score"]
        }, result['hits']['hits'])
        return jsonify({
            "results": results,
            "size": len(results),
            "success": True
        })
    else:
        return jsonify({
            "results": [],
            "size": 0,
            "success": False
        })

    return jsonify(result)

@maz.route("/api/tracking")
def maz_route_tracking():
    if not g.user:
        return "", 401

    try:
        inv = Inventory.get(Inventory.user == g.user)
    except Inventory.DoesNotExist:
        return jsonify({
                "success": True,
                "enabled": False
            })

    return jsonify({
        "success": True,
        "enabled": inv.active,
        "inventory": inv.toDict()
    })

@maz.route("/api/tracking/enable")
def maz_route_tracking_enable():
    if not g.user:
        return "", 401

    try:
        Inventory.get(Inventory.user == g.user)
    except Inventory.DoesNotExist:
        i = Inventory()
        i.user = g.user

        try:
            i.get_latest()
        except:
            return jsonify({
                "success": False,
                "error": "Inventory is private!"
            })
        i.save()
        print i.id

    return jsonify({"success": True})

@maz.route("/api/tracking/disable")
def maz_route_tracking_disable():
    if not g.user:
        return "", 401

    try:
        i = Inventory.get(Inventory.user == g.user)
    except Inventory.DoesNotExist:
        return jsonify({"success": True})

    i.active = False
    i.save()
    return jsonify({"success": True})

@maz.route("/api/tracking/<id>/history/<field>")
def maz_route_tracking_history(id, field):
    try:
        i = Inventory.get(Inventory.user == id)
    except Inventory.DoesNotExist:
        return jsonify({
            "success": False,
            "data": {}
        })

    q = InventoryPricePoint.select().where(InventoryPricePoint.inv == i).limit(32).order_by(InventoryPricePoint.time.desc())

    data = {}
    for entry in q:
        data[int(entry.time.strftime('%s'))] = getattr(entry, field, 0)

    return jsonify({
        "data": data,
        "success": True,
    })
