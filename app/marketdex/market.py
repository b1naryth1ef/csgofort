from pyquery import PyQuery
import requests, time

COUNT_ITEMS_QUERY = u"http://steamcommunity.com/market/search/render/?query={query}&appid={appid}"
LIST_ITEMS_QUERY = u"http://steamcommunity.com/market/search/render/?query={query}&start={start}&count={count}&search_descriptions=0&sort_column={sort}&sort_dir={order}&appid={appid}"
ITEM_PRICE_QUERY = u"http://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid={appid}&market_hash_name={name}"
ITEM_PAGE_QUERY = u"http://steamcommunity.com/market/listings/{appid}/{name}"
BULK_ITEM_PRICE_QUERY = u"http://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={nameid}"

# r.content.split("Market_LoadOrderSpread(", 1)[-1].split(");", 1)[0]

class SteamMarketAPI(object):
    def __init__(self, appid, retries=5):
        self.appid = appid
        self.retries = retries

    def parse_item_name(self, name):
        # Strip out unicode
        name = filter(lambda i: ord(i) <= 256, name)

        r_skin = ""
        r_wear = ""
        r_stat = False
        r_holo = False
        parsed = False

        if name.strip().startswith("Sticker"):
            r_item = "sticker"
            r_skin = name.split("|", 1)[-1]
            if "(holo)" in r_skin:
                r_skin = r_skin.replace("(holo)")
                r_holo = True
            if "|" in r_skin:
                r_skin, r_wear = r_skin.split("|", 1)
            parsed = True
        else:
            if '|' in name:
                start, end = name.split(" | ")
            else:
                start = name
                end = None

            if start.strip().startswith("StatTrak"):
                r_stat = True
                r_item = start.split(" ", 2)[-1]
            else:
                r_stat = False
                r_item = start.strip()

            if end:
                r_skin, ext = end.split("(")
                r_wear = ext.replace(")", "")
            parsed = True

        if not parsed:
            print "Failed to parse item name `%s`" % name

        return (
            r_item.lower().strip() or None,
            r_skin.lower().strip() or None,
            r_wear.lower().strip() or None,
            r_stat,
            r_holo
        )

    def get_item_count(self, query=""):
        url = COUNT_ITEMS_QUERY.format(query=query, appid=self.appid)
        r = requests.get(url).json()
        return r["total_count"]

    def list_items(self, query="", start=0, count=10, sort="quantity", order="desc"):
        url = LIST_ITEMS_QUERY.format(
            query=query,
            start=start,
            count=count,
            sort=sort,
            order=order,
            appid=self.appid)

        for _ in range(self.retries):
            try:
                r = requests.get(url)
                r.raise_for_status()
                r = r.json()
                if r:
                    break
            except Exception:
                print "Error listing items... retrying..."
                time.sleep(3)
        else:
            print "Failed after %s retries" % self.retries
            return None

        pq = PyQuery(r["results_html"])

        rows = pq(".market_listing_row .market_listing_item_name")
        return map(lambda i: i.text, rows)

    def get_item_nameid(self, item_name):
        url = ITEM_PAGE_QUERY.format(name=item_name, appid=self.appid)
        r = requests.get(url)

        if "Market_LoadOrderSpread(" in r.content:
            return int(r.content.split("Market_LoadOrderSpread(", 1)[-1].split(");", 1)[0].strip())
        else:
            return None

    def get_bulkitem_price(self, nameid):
        url = BULK_ITEM_PRICE_QUERY.format(nameid=nameid)
        r = requests.get(url).json()

        data = PyQuery(r["sell_order_summary"])("span")
        b_volume = int(data.text().split(" ", 1)[0])
        b_price = r["lowest_sell_order"]

        return b_volume, b_price

    def get_item_price(self, item_name):
        url = ITEM_PRICE_QUERY.format(
            name=item_name,
            appid=self.appid)

        for _ in range(self.retries):
            try:
                r = requests.get(url)
                r.raise_for_status()
                r = r.json()
                if r:
                    break
            except Exception:
                print "Error getting item price... retrying..."
                time.sleep(3)
        else:
            print "Failed to get item price for (%s) after %s retries" % (item_name, self.retries)
            return (0, 0.0, 0.0)

        return (
            int(r["volume"].replace(",", "")) if 'volume' in r else -1,
            float(r["lowest_price"].split(";")[-1]) if 'lowest_price' in r else 0.0,
            float(r["median_price"].split(";")[-1]) if 'median_price' in r else 0.0,
        )
