from maz.mazdb import *

def pre():
    pass

def run():
    print "Deleting all invalid nameid MIPPs..."
    for mipp in MarketItemPricePoint.select().join(MarketItem).where(MarketItem.nameid != None):
        mipp.delete_instance()

def post():
    pass