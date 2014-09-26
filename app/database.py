#!/usr/bin/env python
import sys, os
from peewee import *
from playhouse.postgres_ext import *
import redis

db = PostgresqlExtDatabase('fort', user="b1n", password="b1n", threadlocals=True, port=5433)
red = redis.Redis()

from maz.mazdb import MarketItem, MarketItemPricePoint
from vacdex.vacdb import *

from util import build_url
from util.steam import SteamAPI

steam = SteamAPI.new()

class BModel(Model):
    class Meta:
        database = db

class User(BModel):
    steamid = CharField()
    email = CharField(null=True)

    active = BooleanField(default=True)

    def get_avatar(self):
        """
        Returns a URL to the users avatar. (Comes from the auth server)
        """
        return build_url("auth", "avatar/%s" % self.id)

    def get_nickname(self):
        """
        Returns the nickname. This will read from the cache if it exists,
        or will set the cache if it does not.

        NB: might be worth asyncing this out to a job if the steamapi is
        down or slow!
        """
        if not hasattr(self, "nickname"):
            self.nickname = (red.get("nick:%s" % self.steamid) or self.cache_nickname(self.steamid)).decode('utf-8')
        return self.nickname

    @classmethod
    def cache_nickname(cls, steamid):
        """
        Caches a users steam nickname in redis. Nicknames are kept for 2
        hours (120 minutes), and then expired. This function will also
        return the latest steamid after caching, to allow for getandset
        functionality
        """
        data = steam.getUserInfo(steamid)
        red.setex("nick:%s" % steamid, data["personaname"], 60 * 120)
        return data['personaname']


TABLES = [
    MarketItem,
    MarketItemPricePoint,
    User
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

