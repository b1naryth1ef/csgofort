from fortdb import GraphMetric
from dateutil.relativedelta import relativedelta
from datetime import datetime
from collections import defaultdict
from util import rounds
import logging

log = logging.getLogger(__name__)

# Datetime attribute fields in order of magnitude
DATETIME_FIELDS = ["microsecond", "second", "minute", "hour", "day", "month", "year"]

def get_next(i):
    for dex, item in enumerate(DATETIME_FIELDS):
        if item == i:
            return DATETIME_FIELDS[dex+1]

def truncate_too(dt, place):
    """
    This function truncates a datetime up until a date-attribute 'place'
    """
    etc = None
    if ':' in place:
        place, etc = place.split(":", 1)
        etc = int(etc)

    for item in DATETIME_FIELDS:
        if item == place:
            if etc:
                val = int(rounds(getattr(dt, item), etc))

                try:
                    dt = dt.replace(**{item: val})
                except:
                    dt = dt + relativedelta(**{place: 1})
            return dt

        dt = dt.replace(**{item: 0})
    return dt

# An averager
AVG = lambda i: sum(i) / len(i)

RULES = {
    "community_response_time": [(
        (relativedelta(seconds=1), "minute:5"),
        (relativedelta(days=7), "hour"),
        (relativedelta(days=30), "day"),
        (relativedelta(months=32), "drop")
    ), AVG],

    "community_inventory_response_time": [(
        (relativedelta(seconds=1), "minute:5"),
        (relativedelta(days=7), "hour"),
        (relativedelta(days=30), "day"),
        (relativedelta(months=18), "drop")
    ), AVG],

    "search_index_time": [(
        (relativedelta(seconds=1), "minute:10"),
        (relativedelta(days=7), "hour"),
        (relativedelta(days=30), "day"),
        (relativedelta(months=2), "drop")
    ), AVG],

    "index_items_time": [(
        (relativedelta(seconds=1), "minute:30"),
        (relativedelta(days=7), "hour"),
        (relativedelta(days=30), "day"),
        (relativedelta(months=2), "drop")
    ), AVG],

    "request_time": [(
        (relativedelta(seconds=1), "second"),
        (relativedelta(minutes=30), "minute:5"),
        (relativedelta(days=7), "hour"),
        (relativedelta(days=30), "day"),
        (relativedelta(months=32), "drop")
    ), AVG],

    "request_count": [(
        (relativedelta(seconds=1), "minute"),
        (relativedelta(hours=1), "minute:5"),
        (relativedelta(days=1), "hour"),
        (relativedelta(months=3), "hour:3"),
        (relativedelta(months=12), "drop"),
    ), sum],

    "community_rcode_%": [(
        (relativedelta(seconds=1), "minute"),
        (relativedelta(days=1), "hour"),
        (relativedelta(days=31), "drop"),
    ), sum]
}

def get_real_rules():
    """
    Rules can use fuzzy-finding wildcards, and thus we need to actually
    extract all the valid rules from the database here.
    """
    real = {}

    for name, rule in RULES.items():
        q = GraphMetric.select(GraphMetric.metric).where(
            GraphMetric.metric % name).group_by(GraphMetric.metric)

        for i in q:
            real[i.metric] = rule
    return real

def truncate_graphs():
    """
    This function helps with the aggergation and compaction of graph metrics.
    Based on rules defined above, this will compact a large set of metrics
    into a single aggergated metric to save space, and allow for more efficient
    querying.
    """
    for (name, rules) in get_real_rules().items():
        rules, action = rules
        log.info("Truncating metric %s", name)

        for (inc, step) in enumerate(rules):
            delta, place = step

            q = GraphMetric.select().where(GraphMetric.metric == name)
            q = q.where(GraphMetric.time <= (datetime.utcnow() - delta))

            # There is another rule
            if (inc + 1) < len(rules):
                q = q.where(GraphMetric.time >= (datetime.utcnow() - rules[inc+1][0]))

            # If we can get the drop rule just remove this shit
            if place == "drop" and q.count():
                log.debug("Dropping %i metrics from rule", q.count())
                map(lambda i: i.delete_instance(), list(q))
                break

            gmres = defaultdict(list)
            map(lambda i: gmres[truncate_too(i.time, place)].append(i), list(q))

            if ':' in place:
                place, _ = place.split(":", 1)

            for time, gms in gmres.items():
                if len(gms) <= 1:
                    continue

                # If this metric may change, don't aggregate
                if getattr(time, place) == getattr(datetime.utcnow(), place):
                    continue

                newgm = GraphMetric(time=time, metric=name)
                newgm.value = action(map(lambda i: i.value, gms))
                log.debug("Aggergated %s metrics into single: %s", len(gms), newgm.save())

                map(lambda i: i.delete_instance(), gms)

    # Find any metrics that we track, but do not have aggergation rules for.
    # These are very bad things and will blow up the GraphMetric table.
    names = map(lambda i: i.metric,
        list(GraphMetric.select(GraphMetric.metric).group_by(GraphMetric.metric)))

    noagg = set(names) - set(get_real_rules().keys())
    if len(noagg):
        log.warning("The following metrics do not have aggregation rules: %s", ', '.join(noagg))
