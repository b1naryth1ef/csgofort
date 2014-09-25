from flask import Blueprint, request, jsonify
from marketdb import *
from collections import Counter

marketdex = Blueprint("marketdex", __name__, subdomain="market")

@marketdex.route("/")
def marketdex_route_index():
    return jsonify({
        "routes": [
            {
                "name": "info",
                "route": "/info",
                "fmt": []
            },
            {
                "name": "items",
                "route": "/items",
                "fmt": []
            },
            {
                "name": "item",
                "route": "/item/<id>",
                "fmt": ["id"]
            },
            {
                "name": "price",
                "route": "/price/<id>",
                "fmt": ["id"]
            },
            {
                "name": "removed",
                "route": "/removed",
                "fmt": []
            }
        ]
    })
    return ":D"

@marketdex.route("/info")
def marketdex_route_info():
    return jsonify({
        "total_items": MarketItem.select().count(),
        "latest": list(MarketItem.select(MarketItem.id).order_by(MarketItem.discovered.desc()).limit(1))[0].id
    })

@marketdex.route("/items")
def marketdex_route_items():
    page = int(request.values.get("page", 1))
    per_page = int(request.values.get("per_page", 10))
    per_page = per_page if per_page <= 100 else 100

    results = map(lambda i: i.toDict(), list(MarketItem.select().order_by(MarketItem.id).paginate(page, per_page)))

    return jsonify({
        "results": results,
        "size": len(results),
        "success": True
    })

@marketdex.route("/item/<id>")
def marketdex_route_item(id):
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

@marketdex.route("/price/<id>")
def marketdex_route_price(id):
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

@marketdex.route("/removed")
def marketdex_route_removed():
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

@marketdex.route("/aggregate")
def marketdex_route_aggregate():
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

def identify_trend(q, trend=.7):
    up, down, none = 0, 0, 0

    last = None
    for mipp in q:
        if not last:
            last = mipp
            continue

        if last.median == mipp.median:
            none += 1

        if last.median < mipp.median:
            up += 1

        if last.median > mipp.median:
            down += 1

        last = mipp

    trend_c = int(len(q) * trend)

    print trend_c, up, down, none

    if up >= trend_c:
        return "UP"

    if down >= trend_c:
        return "DOWN"

    return "NONE"


@marketdex.route("/history/<id>")
def marketdex_route_history(id):
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

# TODO: cache this one!
@marketdex.route("/pricechanges")
def marktedex_route_pricechanges():
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
