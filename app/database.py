from peewee import *
from playhouse.postgres_ext import *
import redis

db = PostgresqlExtDatabase('fort', user="b1n", password="b1n", threadlocals=True, port=5433)
red = redis.Redis()

from marketdex.marketdb import MarketItem, MarketItemPricePoint
from vacdex.vacdb import *

class BModel(Model):
    class Meta:
        database = db

TABLES = [
    MarketItem,
    MarketItemPricePoint
]

if __name__ == "__main__":
    for table in TABLES:
        table.drop_table(True, cascade=True)
        table.create_table(True)