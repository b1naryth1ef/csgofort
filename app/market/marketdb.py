import datetime
from peewee import *
from playhouse.postgres_ext import *
from util.steam import SteamMarketAPI

market_api = SteamMarketAPI(730)
db = PostgresqlExtDatabase('fort', user="b1n", password="b1n", threadlocals=True, port=5433)

class BModel(Model):
    class Meta:
        database = db

class MarketItem(BModel):
    name = CharField()
    nameid = IntegerField(null=True)

    # Parsed name attributes
    wear = CharField(null=True)
    skin = CharField(null=True)
    item = CharField(null=True)
    stat = BooleanField()
    holo = BooleanField()

    discovered = DateTimeField()
    last_crawl = DateTimeField()

    def store_price(self):
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

    def get_latest_mipp(self):
        res = list(MarketItemPricePoint.select().where(
            MarketItemPricePoint.item == self
        ).order_by(MarketItemPricePoint.time.desc()).limit(1))

        if len(res):
            return res[0]

    def toDict(self):
        return {
            "id": self.id,
            "name": self.name,
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
        }

class MarketItemPricePoint(BModel):
    item = ForeignKeyField(MarketItem)

    volume = IntegerField()
    lowest = FloatField()
    median = FloatField()

    time = DateTimeField(default=datetime.datetime.utcnow)

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

