#!/usr/bin/env python
import sys, os

from elasticsearch import Elasticsearch
from peewee import *
from playhouse.postgres_ext import *
from redis import Redis

from util.fields import EnumField
from util.elasticindexes import ES_INDEXES, ES_MAPPINGS

from app import csgofort

# Setup Postgresql Database Connection
db = PostgresqlExtDatabase('fort',
    user="b1n",
    password="b1n",
    threadlocals=True,
    port=csgofort.config.get("POSTGRES_PORT", 5433))

red = Redis(db=csgofort.config.get("REDIS_DB", 1))
es = Elasticsearch(host=csgofort.config.get("ELASTIC_HOST", "127.0.0.1"))

db.register_fields({
    "enum": EnumField
})

class BModel(Model):
    class Meta:
        database = db

    @classmethod
    def create_table(cls, safe):
        for field in cls._meta.get_fields():
            if hasattr(field, "pre_field_create"):
                field.pre_field_create(safe)

        cls._meta.database.create_table(cls, safe)

        for field in cls._meta.get_fields():
            if hasattr(field, "post_field_create"):
                field.post_field_create()

def tables():
    from maz.mazdb import (MarketItem, MarketItemPricePoint, MIPPDaily,
        Inventory, InventoryPricePoint
    )

    from fortdb import User, GraphMetric
    from vactrak.vacdb import VacList, VacID

    return [
        User,
        GraphMetric,
        MarketItem,
        MarketItemPricePoint,
        MIPPDaily,
        Inventory,
        InventoryPricePoint,
        VacList,
        VacID
    ]

def migrate(module):
    print "Running migration for %s" % module.__name__

    module.pre()
    module.run()
    module.post()

def setup_es():
    for k, v in ES_INDEXES.items():
        try:
            es.indices.delete(index="marketitems")
        except: pass

        es.indices.create(
            index=k,
            body=v,
            ignore=400
        )

        for dtype, mp in ES_MAPPINGS.get(k, {}).items():
            es.indices.put_mapping(
                index=k,
                doc_type=dtype,
                body=mp
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
