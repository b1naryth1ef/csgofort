import requests, re, xmltodict, time
from pyquery import PyQuery
from config import STEAM_KEY

COUNT_ITEMS_QUERY = u"http://steamcommunity.com/market/search/render/?query={query}&appid={appid}"
LIST_ITEMS_QUERY = u"http://steamcommunity.com/market/search/render/?query={query}&start={start}&count={count}&search_descriptions=0&sort_column={sort}&sort_dir={order}&appid={appid}"
ITEM_PRICE_QUERY = u"http://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid={appid}&market_hash_name={name}"
ITEM_PAGE_QUERY = u"http://steamcommunity.com/market/listings/{appid}/{name}"
BULK_ITEM_PRICE_QUERY = u"http://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={nameid}"

steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

def if_len(a, b):
    if len(a):
        return a
    return b

class WorkshopEntity(object):
    def __init__(self, id, title, desc, game, user):
        self.id = id
        self.title = title
        self.desc = desc
        self.game = game
        self.user = user
        self.tags = []

class WorkshopFile(WorkshopEntity):
    def __init__(self, *args):
        super(WorkshopFile, self).__init__(*args)

        self.size = None
        self.posted = None
        self.updated = None
        self.thumb = None
        self.images = []

class WorkshopCollection(WorkshopEntity):
    def __init__(self, *args):
        super(WorkshopCollection, self).__init__(*args)

        self.files = []

class SteamAPI(object):
    def __init__(self, key):
        self.key = key

    @classmethod
    def new(cls):
        return cls(STEAM_KEY)

    def request(self, url, data, verb="GET"):
        url = "http://api.steampowered.com/%s" % url
        data['key'] = self.key
        function = getattr(requests, verb.lower())
        resp = function(url, params=data)
        resp.raise_for_status()
        return resp.json()

    def getGroupMembers(self, id):
        """
        Returns a list of steam 64bit ID's for every member in group `group`,
        a group public shortname or ID.
        """
        r = requests.get("http://steamcommunity.com/groups/%s/memberslistxml/?xml=1" % id)
        return xmltodict.parse(r.content)['memberList']['members'].values()

    def getUserInfo(self, id):
        return self.request("ISteamUser/GetPlayerSummaries/v0001", {
            "steamids": id
        })['response']['players']['player'][0]

    def getRecentGames(self, id):
        return self.request("IPlayerService/GetRecentlyPlayedGames/v0001", {"steamid": id})

    def getBanInfo(self, id):
        r = requests.get("http://steamcommunity.com/profiles/%s" % id)
        r.raise_for_status()
        q = PyQuery(r.content)
        bans = q(".profile_ban_status")
        if len(bans):
            return int(bans[0].text_content().split("day(s)", 1)[0].rsplit("\t", 1)[-1].strip())
        return None

    def getWorkshopFile(self, id):
        r = requests.get("http://steamcommunity.com/sharedfiles/filedetails/", params={"id": id})
        r.raise_for_status()
        q = PyQuery(r.content)

        print "Queryin on %s" % id

        breadcrumbs = [(i.text, i.get("href")) for i in q(".breadcrumbs")[0]]
        if not len(breadcrumbs):
            raise Exception("Invalid Workshop ID!")

        gameid = int(breadcrumbs[0][1].rsplit("/", 1)[-1])
        userid = re.findall("steamcommunity.com/(profiles|id)/(.*?)$",
            breadcrumbs[-1][1])[0][-1].split("/", 1)[0]
        title = q(".workshopItemTitle")[0].text

        desc = if_len(q(".workshopItemDescription"),
            q(".workshopItemDescriptionForCollection"))[0].text

        if len(breadcrumbs) == 3:
            size, posted, updated = [[x.text for x in i]
                for i in q(".detailsStatsContainerRight")][0]

            wf = WorkshopFile(id, title, desc, gameid, userid)
            wf.size = size
            wf.posted = posted
            wf.updated = updated
            wf.tags = [i[1].text.lower() for i in q(".workshopTags")]
            thumbs = q(".highlight_strip_screenshot")
            base = q(".workshopItemPreviewImageEnlargeable")
            if len(thumbs):
                wf.images = [i[0].get("src").rsplit("/", 1)[0]+"/" for i in thumbs]
            elif len(base):
                wf.images.append(base[0].get("src").rsplit("/", 1)[0]+"/")
            if len(q(".workshopItemPreviewImageMain")):
                wf.thumb = q(".workshopItemPreviewImageMain")[0].get("src")
            else:
                wf.thumb = wf.images[0]

            return wf
        elif len(breadcrumbs) == 4 and breadcrumbs[2][0] == "Collections":
            wc = WorkshopCollection(id, title, desc, gameid, userid)
            for item in q(".workshopItem"):
                id = item[0].get("href").rsplit("?id=", 1)[-1]
                wc.files.append(self.getWorkshopFile(id))
            return wc

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
        b_price = r["lowest_sell_order"] * .01

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

