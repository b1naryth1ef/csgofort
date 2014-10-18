"""
This file contains any migrations that need to be run from one develop
release to another. This will generally get cleared out weekly, and is
really only used for deployments.
"""

from database import *
from maz.mazdb import *
from playhouse.migrate import *
from util.migrations import *

migrator = PostgresqlFortMigrator(db)

def rmv_junk_mipp_data():
    c = MarketItemPricePoint.delete().where(
        (MarketItemPricePoint.volume == 0) &
        (MarketItemPricePoint.lowest == 0) &
        (MarketItemPricePoint.median == 0)
    ).execute()
    print "Deleted %s invalid mipps" % c

def add_currency_field():
    migrate(
        migrator.pre_add_enum(User.currency),
        migrator.add_column("user", "currency", User.currency),
        migrator.post_add_enum(User.currency)
    )

def add_music_kits():
    migrate(
        migrator.add_column("marketitem", "mkit", MarketItem.mkit)
    )

def add_user_indexes():
    migrate(
        migrator.add_index("user", ("steamid", ), True)
    )

def pre(): pass
def post(): pass

def run():
    rmv_junk_mipp_data()
