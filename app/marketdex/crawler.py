from market import SteamMarketAPI
from marketdb import *
from datetime import datetime
import time

api = SteamMarketAPI(730)

def index_all_items():
    """
    Attempts to re-index all items in the database
    """

    start = datetime.utcnow()
    start_t = time.time()

    pages = int(api.get_item_count() / 100.0) + 2
    for page_n in range(pages):
        print "Reading page %s of %s" % (page_n, pages)
        items = api.list_items(sort="name", start=page_n * 100, count=100)
        for item_name in items:
            try:
                mi = MarketItem.get(MarketItem.name == item_name)
            except MarketItem.DoesNotExist:
                mi = MarketItem(name=item_name, discovered=datetime.utcnow())
                mi.item, mi.skin, mi.wear, mi.stat, mi.holo = api.parse_item_name(mi.name)
            
            mi.last_crawl = datetime.utcnow()
            mi.save()

    print "Index Rescanned in %s seconds!" % (time.time() - start_t)
    print "Size: %s" % MarketItem.select().count()
    print "New: %s" % MarketItem.select().where((MarketItem.discovered >= start)).count()

def index_all_prices():
    print "Re-pricing %s items!" % MarketItem.select().count()
    start = time.time()
    for item in MarketItem.select():
        item.store_price()
    print "Re-pricing finished in %s seconds!" % (time.time() - start)

while True:
    index_all_items()
    index_all_prices()
    time.sleep(600)