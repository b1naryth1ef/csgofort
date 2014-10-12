from database import *
from fortdb import User

from datetime import datetime
from util.steam import SteamAPI

steam = SteamAPI.new()

class VacList(BModel):
    user = ForeignKeyField(User)

    tracked = ArrayField(BigIntegerField, default=[])

    active = BooleanField(default=True)

    def validate(self):
        if len(self.tracked) > 4096:
            raise Exception("Too many tracked accounts! Maximum is 4096.")

    def toDict(self, tiny=False):
        result = {}

        result['user'] = self.user.id
        result['active'] = self.active
        if tiny: return result

        result['tracked'] = []

        for tid in self.tracked:
            result['tracked'].append(VacID.get(VacID.id == tid).toDict())

        return result

class VacID(BModel):
    steamid = BigIntegerField()

    vac_banned = DateTimeField(null=True)
    com_banned = DateTimeField(null=True)
    eco_banned = DateTimeField(null=True)

    vac_days = IntegerField(default=0)
    vac_count = IntegerField(default=0)

    last_crawl = DateTimeField()
    crawl_count = IntegerField(default=0)

    def toDict(self):
        data = {
            "id": self.id,
            "steamid": self.steamid,
            "updated":  self.last_crawl.strftime("%s"),
            "hits": self.crawl_count,
            "trackers": VacList.select().where(VacList.tracked.contains(self.id)).count(),
            "bans": {
                "vac": self.vac_banned.strftime("%s") if self.vac_banned else 0,
                "community": self.com_banned.strftime("%s") if self.com_banned else 0,
                "trade": self.eco_banned.strftime("%s") if self.eco_banned else 0,
            },
            "vac": {
                "last": self.vac_days,
                "count": self.vac_count
            }
        }

        return data

    def crawl(self):
        result = steam.getPlayerBans(self.steamid)

        self.crawl_count += 1
        self.last_crawl = datetime.utcnow()

        self.vac_days = result['DaysSinceLastBan']
        self.vac_count = result['NumberOfVACBans']

        if result["CommunityBanned"] and not self.com_banned:
            self.com_banned = datetime.utcnow()

        if result["VACBanned"] and not self.vac_banned:
            self.vac_banned = datetime.utcnow()

        if result["EconomyBan"] != "none" and not self.eco_banned:
            self.eco_banned = datetime.utcnow()

        self.save()
