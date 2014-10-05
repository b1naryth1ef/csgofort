#!/usr/bin/env python
import sys

from elasticsearch import Elasticsearch
from peewee import *
from playhouse.postgres_ext import *
import redis, os

db = PostgresqlExtDatabase('fort', user="b1n", password="b1n", threadlocals=True, port=os.getenv("PGPORT", 5433))
red = redis.Redis()
es = Elasticsearch()

class BModel(Model):
    class Meta:
        database = db

def tables():
    from maz.mazdb import (MarketItem, MarketItemPricePoint, MIPPDaily,
        Inventory, InventoryPricePoint
    )   

    # from vacdex.vacdb import *
    from fortdb import User

    return [
        User,
        MarketItem,
        MarketItemPricePoint,
        MIPPDaily,
        Inventory,
        InventoryPricePoint,
    ]

def migrate(module):
    print "Running migration for %s" % module.__name__

    module.pre()
    module.run()
    module.post()

def setup_es():
    try:
        es.indices.delete(index="marketitems")
    except: pass
    es.indices.create(
        index="marketitems",
        body={
            "settings": {
                "number_of_shards": 1,
                "analysis": {
                    "filter": {
                        "autocomplete_filter": {
                            "type":     "edge_ngram",
                            "min_gram": 3,
                            "max_gram": 25
                        }
                    },
                    "analyzer": {
                        "autocomplete": {
                            "type":      "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "autocomplete_filter"
                            ]
                        }
                    }
                }
            }
        },
        ignore=400
    )
    es.indices.put_mapping(
        index="marketitems",
        doc_type="marketitem",
        body={
            "marketitem": {
                "properties": {
                    "name": {
                        "type":     "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    )

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage: ./database.py [build/reset/migrate]"
        sys.exit(1)

    if sys.argv[1] == "build":
        print "Building new tables..."
        map(lambda i: i.create_table(True), tables())

        setup_es()

    if sys.argv[1] == "reset":
        print "Resetting DB..."
        for table in tables():
            table.drop_table(True, cascade=True)
            table.create_table(True)

    if sys.argv[1] == "re":

        for table in tables():
            if table.__name__.lower() == sys.argv[2].lower():
                print "Recreating table %s" % sys.argv[2]
                table.drop_table(True, cascade=True)
                table.create_table(True)
                break
        else:
            print "No table %s" % sys.argv[2]

    if sys.argv[1] == "migrate":
        m = "migrations.%s" % sys.argv[2]
        __import__(m)
        migrate(sys.modules[m])
