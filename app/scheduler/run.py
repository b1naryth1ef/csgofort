from scheduler import Scheduler
from maz.crawler import (
    index_all_items, index_all_prices, index_all_images,
    check_community_status, build_daily_mipps)

sched = Scheduler()

sched.add_task(index_all_items, minutes=15)
sched.add_task(index_all_prices, minutes=2)
sched.add_task(index_all_images, start_now=True, hours=6)
sched.add_task(check_community_status, minutes=1)
sched.add_task(build_daily_mipps, hours=1)
