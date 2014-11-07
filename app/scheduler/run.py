from scheduler import Scheduler
from maz.crawler import (
    index_all_items, index_all_prices, index_all_images,
    check_community_status, build_daily_mipps, index_market_search,
    track_inventories)
from util.graph import truncate_graphs
from vactrak.crawler import crawl_tracked_vacs, prune_stale_vacids

sched = Scheduler()

# Index tasks
sched.add_task(index_all_items, minutes=15, start_now=True)
sched.add_task(index_all_prices, minutes=2, start_now=True)
sched.add_task(index_all_images, hours=6)
sched.add_task(index_market_search, start_now=True, minutes=5)

# Task to check steam server status
sched.add_task(check_community_status, start_now=True, minutes=1)

# Aggregate MIPPS into DailyMIPP's
sched.add_task(build_daily_mipps, hours=1, start_now=True)

# Updates tracked inventories
sched.add_task(track_inventories, start_now=True, minutes=5)

# Truncate graphs hourly
sched.add_task(truncate_graphs, start_now=True, hours=1)

# Track VacID objects
sched.add_task(crawl_tracked_vacs, start_now=True, minutes=30)

# Prune stale vacids
sched.add_task(prune_stale_vacids, start_now=True, minutes=30)
