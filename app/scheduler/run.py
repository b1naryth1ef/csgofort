from scheduler import Scheduler
from maz.crawler import index_all_items, index_all_prices, index_all_images

sched = Scheduler()

sched.add_task(index_all_items, minutes=15)
sched.add_task(index_all_prices, minutes=2)
sched.add_task(index_all_images, start_now=True, hours=6)
