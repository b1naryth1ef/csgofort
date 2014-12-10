import datetime
from database import *
from fortdb import User
from util.steam import SteamMarketAPI
from util.web import usd_convert

from dateutil.relativedelta import relativedelta

import logging
log = logging.getLogger(__name__)

market_api = SteamMarketAPI(730)

MARKET_ITEM_INDEXES = (
    (("name", ), True),
    (("wear", ), False),
    (("skin", ), False),
    (("item", ), False),
)

class MarketItem(BModel):
    class Meta:
        indexes = MARKET_ITEM_INDEXES

    name = CharField()
    nameid = IntegerField(null=True)
    classid = IntegerField(null=True)
    image = TextField(null=True)

    # Parsed name attributes
    wear = CharField(null=True)
    skin = CharField(null=True)
    item = CharField(null=True)
    stat = BooleanField()
    holo = BooleanField()
    mkit = BooleanField(default=False)

    discovered = DateTimeField()
    last_crawl = DateTimeField()

    def store_price(self):
        """
        Attempts to query and store the steam market price/volume/etc of
        this item. Depending on if this is a bulk item or not, we need to
        call different api methods.
        """
        if self.nameid:
            low = 0
            volume, med = market_api.get_bulkitem_price(self.nameid)
        else:
            volume, low, med = market_api.get_item_price(self.name)

        # This is to debug some BULLLLSHIT ass stuff
        log.debug("Store Price [%s]: %s, %s, %s" % (self.id, volume, low, med))

        # (-1, 0, 0) implies that steam doesnt have data on the item currently
        if volume == -1 and low == 0 and med == 0:
            volume = 0
            last_mipp = self.get_latest_mipp()
            low = last_mipp.lowest
            med = last_mipp.median

        five_minutes_ago = datetime.datetime.utcnow() - relativedelta(minutes=5)

        # Find a MIPP in the latest five minutes
        q = MarketItemPricePoint.select().where(
            (MarketItemPricePoint.item == self) &
            (MarketItemPricePoint.time >= five_minutes_ago)
        )

        # If we have one, we just update that, otherwise create a fresh one
        if q.count():
            mipp = q.get()
        else:
            mipp = MarketItemPricePoint()

        mipp.item = self
        mipp.volume = volume if volume != -1 else 0
        mipp.lowest = low
        mipp.median = med
        mipp.save()

    def get_daily_mipp(self, day=None):
        if not day:
            day = (datetime.utcnow() - timedelta(days=1))
        day = day.replace(hour=0, minute=0, second=0, microsecond=0)

        return MIPPDaily.select().where((MIPPDaily.item == self) & (MIPPDaily.time == day)).get()

    def get_latest_mipp(self):
        """
        Returns the latest MIPP for this item
        """
        res = list(MarketItemPricePoint.select().where(
            MarketItemPricePoint.item == self
        ).order_by(MarketItemPricePoint.time.desc()).limit(1))

        if len(res):
            return res[0]

    def get_mipp_at(self, dt):
        # TODO: fix lel
        q = list(MarketItemPricePoint.select().where(
            (MarketItemPricePoint.item == self) &
            (MarketItemPricePoint.time >= (dt - relativedelta(days=2))),
            (MarketItemPricePoint.time <= (dt + relativedelta(days=2)))
        ))

        return sorted(q, key=lambda i: (i.time - dt).seconds)[0]

    def get_mipp_daily_at(self, dt):
        return MIPPDaily.get(
            (MIPPDaily.item == self) &
            (MIPPDaily.time == dt.replace(hour=0, minute=0, second=0, microsecond=0))
        )

    def toDict(self, cur="USD", tiny=False):
        latest = self.get_latest_mipp()

        data = {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "classid": self.classid,
            "price": {
                "volume": usd_convert(latest.volume, cur),
                "low": usd_convert(latest.lowest, cur),
                "med": usd_convert(latest.median, cur),
            }
        }

        if tiny: return data

        data["nameid"] = self.nameid
        data["info"] = {
                "wear": self.wear,
                "skin": self.skin,
                "item": self.item,
                "stat": self.stat,
                "holo": self.holo
            }
        data["discovered"] = self.discovered.isoformat()
        data["updated"] = self.last_crawl.isoformat()
        data["points"] = MarketItemPricePoint.select(MarketItemPricePoint.id).where(
            MarketItemPricePoint.item == self).count()

        return data

    def get_family_items(self):
        return MarketItem.select().where(
            (MarketItem.id != self.id) &
            (
                (MarketItem.skin == self.skin) &
                (MarketItem.item == self.item) &
                (MarketItem.stat == self.stat)
            )
        )


MARKET_ITEM_PRICE_POINT_INDEXES = (
    (("volume", "median", "lowest"), False),
    (("time"), False),
)

class MarketItemPricePoint(BModel):
    class Meta:
        indexes = MARKET_ITEM_PRICE_POINT_INDEXES

    item = ForeignKeyField(MarketItem)

    volume = IntegerField()
    lowest = FloatField()
    median = FloatField()

    time = DateTimeField(default=datetime.datetime.utcnow)

    def value(self):
        return self.volume * self.median

    def toDict(self):
        return {
            "item": self.item.id,
            "volume": self.volume,
            "price": {
                "low": self.lowest,
                "med": self.median
            },
            "time": self.time.isoformat()
        }

MIPP_DAILY_INDEXES = (
    (("volume", "median", "lowest"), False),
    (("time", ), False)
)

class MIPPDaily(BModel):
    """
    MIPPDailys are aggergated versions of MIPPs which allow for a more
    consistent and constant data source. They represent an average of all
    observed MIPPs for a single day period (24h exactly). A MIPPDaily will
    NOT exist for items that have no observed MIPP's in a day.
    """
    class Meta:
        indexes = MIPP_DAILY_INDEXES

    item = ForeignKeyField(MarketItem)

    volume = IntegerField()
    lowest = FloatField()
    median = FloatField()

    time = DateTimeField()

class Inventory(BModel):
    user = ForeignKeyField(User)

    active = BooleanField(default=True)

    inventory = JSONField(default=[])

    updated = DateTimeField(null=True)
    added = DateTimeField(default=datetime.datetime.utcnow)

    def calculate_value(self):
        total_value = 0

        for item in self.inventory:
            try:
                total_value += MarketItem.get(MarketItem.id == item['i']).get_latest_mipp().median
            except (MarketItem.DoesNotExist, AttributeError): pass

        return total_value

    def get_latest(self):
        return market_api.get_parsed_inventory(self.user.steamid)

    def toDict(self):
        return {}

class InventoryPricePoint(BModel):
    class Status:
        SUCCESS = 1
        ERROR = 2

    inv = ForeignKeyField(Inventory)
    status = IntegerField(default=Status.SUCCESS)

    # total inventory value
    value = FloatField(default=0)
    size = IntegerField(default=0)

    # Added/Removed items (by market ID)
    added = ArrayField(IntegerField, default=[])
    removed = ArrayField(IntegerField, default=[])

    time = DateTimeField(default=datetime.datetime.utcnow)

    def toDict(self, with_asset=False):
        data = {
            "id": self.id,
            "inv": self.inv.id,
            "status": self.status,
            "value": self.value,
            "size": self.size,
            "added": self.added,
            "removed": self.removed,
            "time": self.time
        }

        if with_asset:
            if len(self.added):
                data["added"] = map(lambda i: i.name,
                    list(MarketItem.select(MarketItem.name).where(MarketItem.classid << self.added)))
            if len(self.removed):
                data["removed"] = map(lambda i: i.name,
                    list(MarketItem.select(MarketItem.name).where(MarketItem.classid << self.removed)))
        return data

