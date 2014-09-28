from database import *
from util.steam import SteamAPI
from util import build_url

steam = SteamAPI.new()

class User(BModel):
    steamid = CharField()
    email = CharField(null=True)

    active = BooleanField(default=True)

    def get_avatar(self):
        """
        Returns a URL to the users avatar. (Comes from the auth server)
        """
        return build_url("auth", "avatar/%s" % self.id)

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

