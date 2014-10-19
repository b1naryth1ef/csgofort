from datetime import datetime
from dateutil.relativedelta import relativedelta
from vacdb import VacID, VacList

import logging
log = logging.getLogger(__name__)

def crawl_tracked_vacs():
    LAST_2HOUR = datetime.utcnow() - relativedelta(hours=2)

    to_upd = VacID.select().where((
            (VacID.vac_banned == None) |
            (VacID.com_banned == None) |
            (VacID.eco_banned == None)) &
        (VacID.last_crawl < LAST_2HOUR)
    )
    count = to_upd.count()

    for vacid in to_upd.iterator():
        vacid.crawl()

    log.info("Updated %s VacID's" % count)

# This could be waaay more efficient
def prune_stale_vacids():
    count = 0
    for vid in VacID.select(VacID.id).iterator():
        if not VacList.select(VacList.id).where(VacList.tracked.contains(vid.id)).count():
            vid.delete_instance()
            count += 1
    log.info("Pruned %s stale VacID's" % count)
