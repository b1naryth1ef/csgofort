"""
This tool constantly crawls and aggregates data from the steam community
market, and dumps it into our database. It's meant to constantly run and
paces itself (while remaining error-safe) to avoid getting blocked by steam
"""

from util.steam import SteamMarketAPI
from mazdb import *
from fortdb import GraphMetric
from util import with_timing

# Date shit
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *

import time, requests, logging

api = SteamMarketAPI(730)
log = logging.getLogger(__name__)

def index_all_items():
    """
    Iterates over every item in the steam community market listing, and
    adds it to the db. If its a new item, it will also query the nameid
    to check if its a bulk or normal item.

    NB: Because of the way the steam listing works, this function expects
    to not always get ALL items back. Sometimes items disappear (because
        they lack volume) from the market for months at a time.
    """

    start = time.time()

    pages = int(api.get_item_count() / 100.0) + 2
    for page_n in range(pages):
        log.info("Reading page %s of %s" % (page_n, pages))

        # Get a listing of items
        items = api.list_items(sort="name", start=page_n * 100, count=100)

        # Iterate over the listing and parse all items into the database
        #  if they no longer exist, otherwise just update the last_crawl
        #  time.
        for item_name in items:
            try:
                try:
                    mi = MarketItem.get(MarketItem.name == item_name)
                except MarketItem.DoesNotExist:
                    log.debug("Crawled new MarketItem `%s`" % item_name)
                    mi = MarketItem(name=item_name, discovered=datetime.utcnow())
                    mi.item, mi.skin, mi.wear, mi.stat, mi.holo, mi.mkit = api.parse_item_name(mi.name)
                    meta = api.get_item_meta(mi.name)
                    mi.nameid = meta["nameid"]
                    mi.image = meta["image"]
                    mi.classid = meta["classid"]

                # Support for old items
                if not mi.classid:
                    mi.classid = api.get_item_meta(mi.name)["classid"]

                log.debug("Updated MarketItem %s on crawl" % mi.name)
                mi.last_crawl = datetime.utcnow()
                mi.save()
            except Exception:
                log.exception("Failed to add item `%s` to DB!" % item_name)

    GraphMetric.mark("index_items_time", time.time() - start)
    log.info("Index Rescanned in %ss, size is: %s" % (time.time() - start, MarketItem.select().count()))

def index_all_prices():
    """
    Creates new MIPP's for every market item in the database.
    """
    log.info("Re-pricing %s items!" % MarketItem.select().count())
    start = time.time()
    for item in MarketItem.select().naive().iterator():
        item.store_price()
    GraphMetric.mark("index_prices_time", time.time() - start)

def index_all_images():
    log.info("Re-indexing all %s item images!" % MarketItem.select().count())
    for item in MarketItem.select().naive().iterator():
        item.image = api.get_item_meta(item.name)["image"]
        if item.image:
            item.save()

def check_community_status():
    log.info("Checking Steam Community status...")
    for _ in range(5):
        try:
            r, ti = with_timing(requests.get, ("http://steamcommunity.com/market/", ))
            GraphMetric.mark("community_rcode_%s" % r.status_code, 1)
            r.raise_for_status()
            GraphMetric.mark("community_response_time", ti)
            red.incr("maz:community_status", -1)
            break
        except Exception:
            time.sleep(5)
    else:
        if int(red.get("maz:community_status") or 0) < 5:
            red.incr("maz:community_status", 1)

def build_single_daily_mipp(item, yesterday, today):
    q = list(MarketItemPricePoint.select().where(
        (MarketItemPricePoint.item == item) &
        (MarketItemPricePoint.time >= yesterday) &
        (MarketItemPricePoint.time <= today)
    ))

    if not len(q):
        return False

    m = MIPPDaily()
    m.item = item
    m.volume = sum(map(lambda i: i.volume, q)) / len(q)
    m.lowest = sum(map(lambda i: i.lowest, q)) / len(q)
    m.median = sum(map(lambda i: i.median, q)) / len(q)
    m.time = yesterday
    m.save()
    return True

def build_daily_mipps():
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    built = 0
    for item in MarketItem.select().naive().iterator():
        q  = MIPPDaily.select().where((MIPPDaily.item == item) & (MIPPDaily.time == yesterday))
        if not q.count():
            if build_single_daily_mipp(item, yesterday, today):
                built += 1

    log.info("Built %s daily aggregate MIPP's" % built)

def index_market_search():
    log.info("Indexing %s Market Items in search" % MarketItem.select().count())

    start = time.time()

    for item in MarketItem.select().naive().iterator():
        doc = {
            "name": item.name,
            "wear": item.wear,
            "skin": item.skin,
            "item": item.item,
        }

        es.index(index="marketitems", doc_type='marketitem', id=item.id, body=doc)

    es.indices.refresh(index="marketitems")
    GraphMetric.mark("search_index_time", time.time() - start)

def fix_item_regressions():
    fixed = MarketItem.select().count()
    for item in MarketItem.select().naive().iterator():
        nameid = api.get_item_meta(item.name)["nameid"]
        if nameid and not item.nameid:
            log.warning("Item Data Regression for %s, is bulk item and has no nameid!" % item.id)
            item.nameid = nameid
            item.save()
        elif not nameid and item.nameid:
            log.warning("Item Data Regression for %s, is not bulk item but has a nameid!" % item.id)
            item.nameid = None
            item.save()
        else:
            fixed -= 1
    log.info("Fixed %s item regressions" % fixed)

def backfill_mipp_data():
    """
    This task was meant to assist in backfilling missing
    pricing data. It should ONLY be run in development
    enviroments, unless a specifc item is being fixed. It
    will fix exactly 30 days of missing data.
    """
    fill = 0
    last_30_days = rrule(DAILY, count=30,
        dtstart=datetime.utcnow() - relativedelta(days=30))
    last_30_days = map(lambda d: d.replace(hour=0, minute=0, second=0, microsecond=0), last_30_days)

    for item in MarketItem.select().naive().iterator():
        days = dict([(i, []) for i in last_30_days if not MIPPDaily.select().where(
            (MIPPDaily.item == item) &
            (MIPPDaily.time == i)).count()])

        try:
            hist = api.get_historical_price_data(item.name)
        except Exception:
            log.exception("Failed to get historical data for %s" % item.name)
            continue

        for entry in hist:
            when = datetime.strptime(entry[0].split(":", 1)[0], "%b %d %Y %H")
            when = when.replace(hour=0, minute=0, second=0, microsecond=0)
            if when in days:
                days[when].append(entry[1])

        for k, v in days.items():
            if not len(v): continue
            log.debug("Fixing day %s for item %s with %s results" % (k, item.name, len(v)))
            md = MIPPDaily()
            md.item = item
            md.volume = 0
            md.lowest = 0
            md.median = sum(v) / len(v)
            md.time = k
            md.save()
            fill += 1

    log.debug("Filled %s missing MIPPDaily's" % fill)

def track_inventories():
    LAST_HOUR = datetime.utcnow() - relativedelta(hours=1)

    q = (
        (Inventory.active == True) &
        ((Inventory.updated < LAST_HOUR) | (Inventory.updated == None))
    )

    updated = 0
    for inv in Inventory().select().where(q).iterator():
        ipp = InventoryPricePoint()
        ipp.inv = inv

        try:
            new_inv, t2 = with_timing(inv.get_latest, ())
            GraphMetric.mark("community_inventory_response_time", t2)
        except Exception:
            ipp.status = InventoryPricePoint.Status.ERROR
            ipp.save()
            log.warning("Failed to update inventory %s" % inv.id)
            continue

        # TEMP: backwards compat for assetid -> classid migration
        if len(inv.inventory) and not "c" in inv.inventory[0]:
            old_ids = set(map(int, map(lambda i: i["s"].split("_", 1)[0], inv.inventory)))
        else:
            old_ids = set(map(lambda i: i["c"], inv.inventory))
        new_ids = set(map(lambda i: i["c"], new_inv))

        # Sets are great
        ipp.removed = list(old_ids - new_ids)
        ipp.added = list(new_ids - old_ids)

        # Do a favor and update the actual inv!
        inv.inventory = new_inv

        ipp.size = len(new_inv)
        ipp.value = inv.calculate_value()
        inv.updated = datetime.utcnow()

        ipp.save()
        inv.save()
        updated += 1

    log.info("Updated %s inventories" % updated)
