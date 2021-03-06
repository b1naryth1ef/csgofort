from database import *
from util.steam import SteamAPI
from util.web import get_currencies, get_sym
from util import build_url
from datetime import datetime

steam = SteamAPI.new()

USER_INDEXES = (
    (("steamid", ), True)
)

class SteamIDEntity(object):
    @classmethod
    def cache_nickname(cls, steamid):
        """
        Caches a users steam nickname in redis. Nicknames are kept for 2
        hours (120 minutes), and then expired. This function will also
        return the latest steamid after caching, to allow for getandset
        functionality
        """
        data = steam.getUserInfo(steamid)
        red.setex("nick:%s" % steamid, data["personaname"], 60 * 120)
        return data['personaname']

    def get_nickname(self):
        """
        Returns the nickname. This will read from the cache if it exists,
        or will set the cache if it does not.

        NB: might be worth asyncing this out to a job if the steamapi is
        down or slow!
        """
        if not hasattr(self, "nickname"):
            self.nickname = red.get("nick:%s" % self.steamid) or self.cache_nickname(self.steamid)
            if not isinstance(self.nickname, unicode):
                self.nickname = self.nickname.decode('utf-8')
        return self.nickname

    def get_avatar(self):
        """
        Returns a URL to the users avatar. (Comes from the auth server)
        """
        return build_url("auth", "avatar/%s" % self.steamid)

class User(BModel, SteamIDEntity):
    class Meta:
        indexes = USER_INDEXES

    class Level:
        BASIC = 0
        ADMIN = 100

    steamid = CharField()
    email = CharField(null=True)

    active = BooleanField(default=True)
    level = IntegerField(default=0)

    # The selected currency, default is USD
    currency = EnumField(choices=get_currencies(), default='USD')

    def get_currency_sym(self):
        return get_sym(self.currency)

    def toDict(self, admin=False):
        data = {
            "id": self.id,
            "steamid": self.steamid,
            "nickname": self.get_nickname(),
            "avatar": self.get_avatar(),
            "level": self.level,
            "active": self.active,
            "cur": self.currency
        }

        return data

GRAPH_METRIC_INDEXES = (
    (("metric", ), False),
)

class GraphMetric(BModel):
    """
    GraphMetrics are a simple way to track and graph statistics. If you
    create a new metric (e.g. calling GraphMetric.mark) you MUST add an
    aggregation rule in util/graph.py!!!!
    """
    class Meta:
        indexes = GRAPH_METRIC_INDEXES

    metric = CharField()
    value = FloatField()
    time = DateTimeField()

    @classmethod
    def mark(self, name, value):
        GraphMetric.create(metric=name, time=datetime.utcnow(), value=value)

    @classmethod
    def graph(self, name, start):
        q = GraphMetric.select().where(
            (GraphMetric.metric == name) &
            (GraphMetric.time >= start)
        )

        return {i.time.strftime("%s"): i.value for i in q}
