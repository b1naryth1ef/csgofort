from scheduler import Scheduler
from maz.crawler import (
    index_all_items, index_all_prices, index_all_images,
    check_community_status, build_daily_mipps, index_market_search,
    track_inventories)

sched = Scheduler()

# Index tasks
sched.add_task(index_all_items, minutes=15)
sched.add_task(index_all_prices, minutes=2)
sched.add_task(index_all_images, hours=6)
sched.add_task(index_market_search, start_now=True, minutes=5)

# Task to check steam server status
sched.add_task(check_community_status, minutes=1)

# Aggregate MIPPS into DailyMIPP's
sched.add_task(build_daily_mipps, hours=1, start_now=True)

# Updates tracked inventories
sched.add_task(track_inventories, start_now=True, minutes=5)
