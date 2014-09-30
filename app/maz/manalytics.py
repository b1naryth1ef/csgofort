from mazdb import *
from datetime import datetime, timedelta


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

normalize_date = lambda i: i.replace(hour=0, minute=0, second=0, microsecond=0)

def get_market_value_total_now():
    """
    This function returns the current estimated market value. This does
    NOT use MIPPDaily's to try and be as up-to-date as possible.

    TODO: motherfucking O(1) plz
    """
    latest = get_latest_mipps()
    return int(sum(map(lambda i: 
        (i.median * i.volume) if i.volume > 0 else 0, list(latest))))

def util_per_daily_mipp_range(start, end, selection):
    """
    Applys a selection to an aggergation over all daily mipps. Used for
    dashboard graphs. O(1) selection/aggergation performance for any range
    """
    return MIPPDaily.select(*selection).where(
        (MIPPDaily.time >= normalize_date(start)),
        (MIPPDaily.time <= normalize_date(end)),
        (MIPPDaily.volume > 0)
    ).group_by(MIPPDaily.time)

def get_daily_market_value_range(start, end):
    """
    This function returns a list of N market-value (aggergates) for N days
    (MIPPDailys) within the date range start - end.
    """
    q = util_per_daily_mipp_range(start, end, (
        MIPPDaily.time,
        fn.Sum(MIPPDaily.median * MIPPDaily.volume).alias("x"))
    )
    return dict(map(lambda i: (i.time.strftime("%s"), i.x), list(q)))

def get_daily_market_size_range(start, end):
    """
    This function returns a list of N market-sizes (aggergates) for N days
    (MIPPDailys) within the date range start - end.
    """
    q = util_per_daily_mipp_range(start, end, (
        MIPPDaily.time,
        fn.Sum(MIPPDaily.volume).alias("x"))
    )
    return dict(map(lambda i: (i.time.strftime("%s"), i.x), list(q)))

def get_latest_mipp_dailys(day=None):
    if not day:
        day = (datetime.utcnow() - timedelta(days=1))

    day = day.replace(hour=0, minute=0, second=0, microsecond=0)

    return MIPPDaily.select().where((MIPPDaily.time == day))

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
