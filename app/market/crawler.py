"""
This tool constantly crawls and aggregates data from the steam community
market, and dumps it into our database. It's meant to constantly run and
paces itself (while remaining error-safe) to avoid getting blocked by steam
"""

from market import SteamMarketAPI
from marketdb import *
from datetime import datetime
import time

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
    start_t = time.time()

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
            
            mi.last_crawl = datetime.utcnow()
            mi.save()

    print "Index Rescanned in %s seconds!" % (time.time() - start_t)
    print "Size: %s" % MarketItem.select().count()
    print "New: %s" % MarketItem.select().where((MarketItem.discovered >= start)).count()

def index_all_prices():
    """
    Creates new MIPP's for every market item in the database.
    """
    print "Re-pricing %s items!" % MarketItem.select().count()
    start = time.time()
    for item in MarketItem.select():
        item.store_price()
    print "Re-pricing finished in %s seconds!" % (time.time() - start)

def run():
    while True:
        index_all_items()
        index_all_prices()
        time.sleep(600)