from datetime import datetime
from dateutil.relativedelta import relativedelta
from vacdb import VacID

def crawl_tracked_vacs():
    LAST_2HOUR = datetime.utcnow() - relativedelta(hours=2)

    to_upd = VacID.select().where(
        (
            (VacID.vac_banned == None) |
            (VacID.com_banned == None) |
            (VacID.eco_banned == None)
        ) & (VacID.last_crawl < LAST_2HOUR)
    )
    count = to_upd.count()

    for vacid in to_upd.iterator():
        vacid.crawl()

    print "Updated %s VacID's" % count
