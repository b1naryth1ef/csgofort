"""
This tool constantly crawls and aggregates data from the steam community
market, and dumps it into our database. It's meant to constantly run and
paces itself (while remaining error-safe) to avoid getting blocked by steam
"""

from util.steam import SteamMarketAPI
from mazdb import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, requests

api = SteamMarketAPI(730)

def index_all_items():
    """
    Iterates over every item in the steam community market listing, and
    adds it to the db. If its a new item, it will also query the nameid
    to check if its a bulk or normal item.

    NB: Because of the way the steam listing works, this function expects
    to not always get ALL items back. Sometimes items disappear (because
        they lack volume) from the market for months at a time.
    """

    start = datetime.utcnow()

    pages = int(api.get_item_count() / 100.0) + 2
    for page_n in range(pages):
        print "Reading page %s of %s" % (page_n, pages)

        # Get a listing of items
        items = api.list_items(sort="name", start=page_n * 100, count=100)

        # Iterate over the listing and parse all items into the database
        #  if they no longer exist, otherwise just update the last_crawl
        #  time.
        for item_name in items:
            try:
                mi = MarketItem.get(MarketItem.name == item_name)
            except MarketItem.DoesNotExist:
                mi = MarketItem(name=item_name, discovered=datetime.utcnow())
                mi.item, mi.skin, mi.wear, mi.stat, mi.holo = api.parse_item_name(mi.name)
                mi.nameid = api.get_item_nameid(mi.name)
                mi.image = api.get_item_image(mi.name)
            
            mi.last_crawl = datetime.utcnow()
            mi.save()

    print "Index Rescanned in!"
    print "Size: %s" % MarketItem.select().count()
    print "New: %s" % MarketItem.select().where((MarketItem.discovered >= start)).count()

def index_all_prices():
    """
    Creates new MIPP's for every market item in the database.
    """
    print "Re-pricing %s items!" % MarketItem.select().count()
    for item in MarketItem.select().naive().iterator():
        item.store_price()

def index_all_images():
    print "Re-indexing all %s item images!" % MarketItem.select().count()
    for item in MarketItem.select().naive().iterator():
        item.image = api.get_item_image(item.name)
        if item.image:
            item.save()
    print "Finished re-indexing all item images!"

def check_community_status():
    print "Checking Steam Community status..."
    for _ in range(5):
        try:
            r = requests.get("http://steamcommunity.com/market/")
            r.raise_for_status()
            red.incr("maz:community_status", -1)
        except:
            time.sleep(5)
    else:
        if red.get("maz:community_status") < 5:
            red.incr("maz:community_status", 1)
    print "Done checking Steam Community Status."


def build_single_daily_mipp(item, yesterday, today):
    q = MarketItemPricePoint.select().where(
        (MarketItemPricePoint.item == item) &
        (MarketItemPricePoint.time >= yesterday) &
        (MarketItemPricePoint.time <= today)
    )

    if not q.count():
        print "No MIPP's for daily aggregation (%s)!" % item.id
        return False
    q = list(q)

    m = MIPPDaily()
    m.item = item
    m.volume = sum(map(lambda i: i.volume, q)) / len(q)
    m.lowest = sum(map(lambda i: i.lowest, q)) / len(q)
    m.median = sum(map(lambda i: i.median, q)) / len(q)
    m.samples = map(lambda i: i.id, q)
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

    print "Built %s daily aggregate MIPP's" % built

def index_market_search():
    print "Indexing %s Market Items in search" % MarketItem.select().count()

    for item in MarketItem.select().naive().iterator():
        doc = {
            "name": item.name,
            "wear": item.wear,
            "skin": item.skin,
            "item": item.item,
        }

        es.index(index="marketitems", doc_type='marketitem', id=item.id, body=doc)

    es.indices.refresh(index="marketitems")

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
            new_inv = inv.get_latest()
        except:
            ipp.status = InventoryPricePoint.Status.ERROR
            ipp.save()
            print "Failed to update inventory %s" % inv.id
            continue

        inv_ids_old = map(lambda i: i["s"].split("_", 1)[0], inv.inventory)
        inv_ids_new = map(lambda i: i["s"].split("_", 1)[0], new_inv)

        for iid in inv_ids_old:
            if iid not in inv_ids_new:
                ipp.removed.append(iid)
            else:
                inv_ids_new.remove(iid)

        # Do a favor and update the actual inv!
        inv.inventory = new_inv

        ipp.size = len(new_inv)
        ipp.added = inv_ids_new
        ipp.value = inv.calculate_value()
        ipp.save()

        inv.updated = datetime.utcnow()
        inv.save()
        updated += 1

    print "Updated %s inventories" % updated
