from flask import Blueprint, request, jsonify, render_template
from marketdb import *
from manalytics import *
from collections import Counter

import json

from dateutil.rrule import *
from dateutil.relativedelta import relativedelta

market = Blueprint("market", __name__, subdomain="market")

with open("market/API.json", "r") as f:
    API_DOCS = json.load(f)

RATE_LIMIT_UPPER = 5000

@market.before_request
def before_market_request():
    KEY = "marketapi:limit:%s" % request.remote_addr

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

@market.route("/")
def market_route_index():
    return render_template("market/index.html")

@market.route("/api")
def market_route_api():
    return render_template("market/api.html", docs=API_DOCS)

@market.route("/api/status")
def market_route_status():
    # TODO: pipeline?
    return jsonify({
        "success": True,
        "quota": red.get("marketapi:limit:%s" % request.remote_addr),
        "ttl": red.ttl("marketapi:limit:%s" % request.remote_addr)
    })

@market.route("/api/info")
def market_route_info():
    """
    Returns information about the global dataset
    """
    latest = get_latest_mipps()

    return jsonify({
        "total_items": MarketItem.select().count(),
        "total_listings": sum(map(lambda i: i.volume if i.volume > 0 else 0, list(latest))),
        "latest": list(MarketItem.select(MarketItem.id).order_by(MarketItem.discovered.desc()).limit(1))[0].id,
        "value": get_market_value_total(),
        "success": True
    })

@market.route("/api/items")
def market_route_items():
    """
    A paginated endpoint for listing all items on the market
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

@market.route("/api/item/<id>")
def market_route_item(id):
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
        "item": mi.toDict()
    })

@market.route("/api/item/<id>/price")
def market_route_price(id):
    """
    Returns pricing information for a single item, given the items internal
    ID
    """
    try:
        mi = MarketItem.get(MarketItem.id == id)
    except MarketItem.DoesNotExist:
        return jsonify({
            "success": False,
            "error": "Invalid Item ID!"
        })

    return jsonify({
        "success": True,
        "price": mi.get_latest_mipp().toDict()
    })

@market.route("/api/item/<id>/history")
def market_route_history(id):
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

@market.route("/api/removed")
def market_route_removed():
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

@market.route("/api/aggregate")
def market_route_aggregate():
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
@market.route("/api/pricechanges")
def market_route_pricechanges():
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

@market.route("/api/graph/totalvalue")
def market_route_value_total():
    """
    Returns a graph of the total market value given a resolution
    """
    res = request.values.get("res", "week")
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

    data = {}
    for dt in ruleset:
        start = dt - datetime.timedelta(days=1)
        data[dt.strftime("%Y-%m-%d")] = get_market_value_total(start, dt)

    return jsonify({
        "data": data,
        "success": True
    })
