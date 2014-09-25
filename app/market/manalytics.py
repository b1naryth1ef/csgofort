from marketdb import *

def get_market_value_total(start=None, end=None):
    q = MarketItemPricePoint.select().limit(1)

    if start and end:
        q = q.where(
            (MarketItemPricePoint.time >= start) &
            (MarketItemPricePoint.time <= dt)
        )

    return sum(map(lambda i: i.median * i.volume, q))

# WTF does this even mean tho?
# def get_market_value_avg(start=None, end=None):
#     q = MarketItemPricePoint.select(fn.Avg(MarketItemPricePoint.median).alias("avg"))
#     q = q.group_by(MarketItemPricePoint.item)
#     if start and end:
#         q = q.where(
#                 (MarketItemPricePoint.time >= start) &
#                 (MarketItemPricePoint.time <= dt)
#             )

#     results = map(lambda i: i.avg, q)

#     if not len(results):
#         return 0

#     return sum(results) / len(results)

