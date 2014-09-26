from database import *
from maz.mazdb import *
from playhouse.migrate import *

migrator = PostgresqlMigrator(db)

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
    for mipp in MarketItemPricePoint.select().join(MarketItem).where(MarketItem.nameid != None):
        mipp.delete_instance()


def pre(): pass
def post(): pass

def run():
    add_item_image_field()
