"""
This file contains any migrations that need to be run from one develop
release to another. This will generally get cleared out weekly, and is
really only used for deployments.
"""

from database import *
from maz.mazdb import *
from playhouse.migrate import *
from util.migrations import *
from vactrak.vacdb import VacID

migrator = PostgresqlFortMigrator(db)

def inventory_classids_conversion():
    """
    Converts added/removed columns from charfield to integer
    """
    query = db.get_conn().cursor()
    query.execute("ALTER TABLE inventorypricepoint RENAME COLUMN added TO added_old;")
    query.execute("ALTER TABLE inventorypricepoint RENAME COLUMN removed TO removed_old;")

    migrate(
        migrator.add_column("inventorypricepoint", "added", InventoryPricePoint.added),
        migrator.add_column("inventorypricepoint", "removed", InventoryPricePoint.removed)
    )

    query = db.get_conn().cursor()
    query.execute("BEGIN")
    query.execute("SELECT id, added_old, removed_old FROM inventorypricepoint;")
    for entry in query.fetchall():
        InventoryPricePoint.update(
            added=map(int, entry[1]), removed=map(int, entry[2])
        ).where(InventoryPricePoint.id == entry[0]).execute()
    query.execute("COMMIT")

    migrate(
        migrator.drop_column("inventorypricepoint", "added_old"),
        migrator.drop_column("inventorypricepoint", "removed_old")
    )

def add_classid_field():
    migrate(
        migrator.add_column("marketitem", "classid", MarketItem.classid)
    )

def add_private_field():
    migrate(
        migrator.add_column("vacid", "private", VacID.private)
    )

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
    inventory_classids_conversion()
