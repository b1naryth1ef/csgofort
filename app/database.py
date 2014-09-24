#!/usr/bin/env python
import sys, os
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

def migrate(module):
    print "Running migration for %s" % module.__name__
    
    module.pre()
    module.run()
    module.post()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage: ./database.py [build/reset/migrate]"
        sys.exit(1)

    if sys.argv[1] == "build":
        print "Building new tables..."
        map(lambda i: i.create_table(True), TABLES)

    if sys.argv[1] == "reset":
        print "Resetting DB..."
        for table in TABLES:
            table.drop_table(True, cascade=True)
            table.create_table(True)

    if sys.argv[1] == "migrate":
        m = "migrations.%s" % sys.argv[2]
        __import__(m)
        migrate(sys.modules[m])

