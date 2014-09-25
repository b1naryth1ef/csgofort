from marketdb import *


MARKET_VALUE_QUERY = """
SELECT t1.* FROM marketitempricepoint t1
  JOIN (SELECT item_id, MAX(time) as time FROM marketitempricepoint GROUP BY item_id) t2
    ON t1.item_id = t2.item_id AND t1.time = t2.time ORDER BY item_id
"""

def get_market_value_total(start=None, end=None):
    q = MARKET_VALUE_QUERY

    if start and end:
        q = q + "WHERE t1.time >= ? AND t1.time <= ?"
        q = MarketItemPricePoint.raw(q, start, end)
    else:
        q = MarketItemPricePoint(q)

    return int(sum(map(lambda i: i.median * i.volume, list(q))))
