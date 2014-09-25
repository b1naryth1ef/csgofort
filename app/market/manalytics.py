from marketdb import *


# This query extracts the latest mipp for every known item while being O(1)
#  instead of being O(n) and hitting the database for every item. This is
#  basically an aggregate that uses the join conditions to order the results
#  and limit by time.
MARKET_VALUE_QUERY = """
SELECT t1.* FROM marketitempricepoint AS t1
  JOIN (SELECT item_id, MAX(time) as time FROM marketitempricepoint GROUP BY item_id) AS t2
    ON t1.item_id = t2.item_id AND t1.time = t2.time
    %s
"""

def get_market_value_total(start=None, end=None):
    """
    Returns the total market value given a timeframe. It will only use the
    most-recent MIPP inside that time-period, but will return a valuation
    based on average price and volume at that time.
    """
    latest_mipps = get_latest_mipps(start, end)
    return int(sum(map(lambda i: 
        (i.median * i.volume) if i.volume > 0 else 0, list(latest_mipps))))

def get_latest_mipps(start=None, end=None):
    q = MARKET_VALUE_QUERY

    if start and end:
        q = MarketItemPricePoint.raw(q % "WHERE t1.time >= %s AND t1.time <= %s", start, end)
    else:
        q = MarketItemPricePoint.raw(q % "")

    return q

def identify_trend(q, trend=.7):
    up, down, none = 0, 0, 0

    last = None
    for mipp in q:
        if not last:
            last = mipp
            continue

        if last.median == mipp.median:
            none += 1

        if last.median < mipp.median:
            up += 1

        if last.median > mipp.median:
            down += 1

        last = mipp

    trend_c = int(len(q) * trend)

    print trend_c, up, down, none

    if up >= trend_c:
        return "UP"

    if down >= trend_c:
        return "DOWN"

    return "NONE"
