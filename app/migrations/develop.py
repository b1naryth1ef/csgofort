from database import *
from maz.mazdb import *
from playhouse.migrate import *

migrator = PostgresqlMigrator(db)

def add_indexes():
    migrate(
        migrator.add_index("marketitempricepoint", ("volume", ), False),
        migrator.add_index("marketitempricepoint", ("median", ), False),
        migrator.add_index("marketitempricepoint", ("time", ), False),
        migrator.add_index("marketitem", ("name", ), True),
        migrator.add_index("marketitem", ("wear", ), False),
        migrator.add_index("marketitem", ("skin", ), False),
        migrator.add_index("marketitem", ("item", ), False),
        migrator.add_index("mippdaily", ("volume", ), False),
        migrator.add_index("mippdaily", ("median", ), False),
        migrator.add_index("mippdaily", ("time", ), False)
    )

def fix_negative_volumes():
    MarketItemPricePoint.update(volume=0).where(MarketItemPricePoint.volume == -1).execute()

def add_user_level():
    migrate(
        migrator.add_column("user", "level", User.level)
    )

def rmv_mipp_daily_samples():
    migrate(
        migrator.drop_column('mippdaily', 'samples')
    )

def add_inventory_size_field():
    migrate(
        migrator.add_column('inventorypricepoint', 'size', InventoryPricePoint.size)
    )

def add_item_image_field():
    migrate(
        migrator.add_column('marketitem', 'image', MarketItem.image),
    )

def add_item_indexes():
    migrate(
        *[
            migrator.add_index('marketitem', *x) for x in MARKET_ITEM_INDEXES
        ]
    )
    migrate(
        *[
            migrator.add_index('markeitempricepoint', *x) for x in MARKET_ITEM_PRICE_POINT_INDEXES
        ]
    )

def remove_invalid_nameid_mipps():
    print "Deleting all invalid nameid MIPPs..."
    for mipp in MarketItemPricePoint.select().join(MarketItem).where(MarketItem.nameid is not None):
        mipp.delete_instance()


def pre(): pass
def post(): pass

def run():
    fix_negative_volumes()
    add_indexes()
