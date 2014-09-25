from marketdb import *

def market_value(start=None, end=None):
    q = MarketItemPricePoint.select(fn.Avg(MarketItemPricePoint.median).alias("avg"))
    q = q.group_by(MarketItemPricePoint.item)
    if start and end:
        q = q.where(
                (MarketItemPricePoint.time >= start) &
                (MarketItemPricePoint.time <= dt)
            )

    return map(lambda i: i.avg, q)

def get_market_value_total(start=None, end=None):
    return sum(market_value(start, end))

def get_market_value_avg(start=None, end=None):
    results = market_value(start, end)

    if not len(results):
        return 0

    return sum(results) / len(results)

