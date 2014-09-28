import datetime
from database import *
from fortdb import User
from util.steam import SteamMarketAPI

market_api = SteamMarketAPI(730)
class BModel(Model):
    class Meta:
        database = db

MARKET_ITEM_INDEXES = (
    # (("name", ), True),
    # (("wear", ), False),
    # (("skin", ), False),
    # (("item", ), False),
)

class MarketItem(BModel):
    class Meta:
        indexes = MARKET_ITEM_INDEXES

    name = CharField()
    nameid = IntegerField(null=True)
    image = TextField(null=True)

    # Parsed name attributes
    wear = CharField(null=True)
    skin = CharField(null=True)
    item = CharField(null=True)
    stat = BooleanField()
    holo = BooleanField()

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

        # TODO: find a MIPP in the last 5 minutes and update that instead

        mipp = MarketItemPricePoint()
        mipp.item = self
        mipp.volume = volume
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

    def toDict(self):
        latest = self.get_latest_mipp()
        return {
            "id": self.id,
            "name": self.name,
            "nameid": self.nameid,
            "image": self.image,
            "info": {
                "wear": self.wear,
                "skin": self.skin,
                "item": self.item,
                "stat": self.stat,
                "holo": self.holo
            },
            "discovered": self.discovered.isoformat(),
            "updated": self.last_crawl.isoformat(),
            "points": MarketItemPricePoint.select(MarketItemPricePoint.id).where(
                MarketItemPricePoint.item == self).count(),
            "price": {
                "volume": latest.volume,
                "low": latest.lowest,
                "med": latest.median
            }
        }

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
    # (("item", ), False),
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


class MIPPDaily(BModel):
    """
    MIPPDailys are aggergated versions of MIPPs which allow for a more
    consistent and constant data source. They represent an average of all
    observed MIPPs for a single day period (24h exactly). A MIPPDaily will
    NOT exist for items that have no observed MIPP's in a day.
    """
    item = ForeignKeyField(MarketItem)

    volume = IntegerField()
    lowest = FloatField()
    median = FloatField()

    samples = ArrayField(IntegerField)
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
            except MarketItem.DoesNotExist: pass

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
    added = ArrayField(CharField, default=[])
    removed = ArrayField(CharField, default=[])

    time = DateTimeField(default=datetime.datetime.utcnow)

    def toDict(self):
        return {
            "id": self.id,
            "inv": self.inv.id,
            "status": self.status,
            "value": self.value,
            "size": self.size,
            "added": self.added,
            "removed": self.removed,
            "time": self.time
        }
