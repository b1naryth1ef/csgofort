"""
Tests all the functionality related to API wrappers around
Steam. This includes the actual steam API and our custom crawlers/parsers
"""
import unittest
from requests.exceptions import HTTPError

from util.steam import SteamAPI, SteamAPIError, SteamMarketAPI, WorkshopFile

class TestSteamAPI(unittest.TestCase):
    def setUp(self):
        self.api = SteamAPI.new()

    def test_vanity_to_steamid(self):
        self.assertEqual(self.api.getFromVanity("b1naryth1ef"), 76561198037632722)
        self.assertEqual(self.api.getFromVanity("juiceboxer"), 76561198041079607)
        self.assertEqual(self.api.getFromVanity("mothmonster"), 76561198057181896)

        self.assertEqual(self.api.getFromVanity("adsjlkjsdfl;fkja;sldfjasdf"), 0)
        self.assertEqual(self.api.getFromVanity("thisisatestpleasemakeitpass"), 0)

        self.assertRaises(SteamAPIError, self.api.getFromVanity, ("", ))

    def test_get_group_members(self):
        pancake = self.api.getGroupMembers("pancakeseat")

        self.assertIn(76561198037632722, pancake)
        self.assertIn(76561198057181896, pancake)

        self.assertRaises(SteamAPIError, self.api.getGroupMembers, ("kljfadsklfsdkjljklfdalkjf", ))

    def test_user_info(self):
        data = self.api.getUserInfo(76561198037632722)

        self.assertEqual(data["steamid"], unicode(76561198037632722))
        self.assertEqual(data["timecreated"], 1296579952)

        self.assertRaises(SteamAPIError, self.api.getUserInfo, (0, ))

    def test_recent_games(self):
        data = self.api.getRecentGames(76561198037632722)

        self.assertGreater(len(data), 1)
        self.assertRaises(SteamAPIError, self.api.getRecentGames, (0, ))

    def test_player_bans(self):
        data = self.api.getPlayerBans(76561198037632722)

        self.assertFalse(data["CommunityBanned"])
        self.assertEqual(data["EconomyBan"], "none")
        self.assertFalse(data["VACBanned"])
        self.assertEqual(data["DaysSinceLastBan"], 0)
        self.assertEqual(data["NumberOfVACBans"], 0)

        data = self.api.getPlayerBans(76561198043989211)
        self.assertTrue(data["VACBanned"])
        self.assertGreater(data["DaysSinceLastBan"], 1)
        self.assertGreaterEqual(data["NumberOfVACBans"], 1)

        self.assertRaises(SteamAPIError, self.api.getPlayerBans, (0, ))

    def test_workshop_file(self):
        data = self.api.getWorkshopFile(163589843)

        self.assertIsInstance(data, WorkshopFile)
        self.assertEqual(data.title, "Cache")
        self.assertEqual(data.desc, "A bomb defusal map set around Chernobyl.")
        self.assertEqual(data.game, 730)
        self.assertEqual(data.user, "FMPONE")
        self.assertIn("classic", data.tags)
        self.assertGreater(len(data.images), 1)
        self.assertEqual(data.posted, "Jul 25, 2013 @ 5:23am")

        self.assertRaises(SteamAPIError, self.api.getWorkshopFile, (0, ))

class TestSteamMarketAPI(unittest.TestCase):
    def setUp(self):
        self.api = SteamMarketAPI(730)

    def test_inventory(self):
        data = self.api.get_inventory(76561198037632722)

        self.assertGreater(len(data["rgInventory"]), 1)
        self.assertIn("150402846", data["rgInventory"].keys())

        obj = data["rgInventory"]["150402846"]
        self.assertEqual(obj["classid"], "320337751")
        self.assertEqual(obj["instanceid"], "188530139")
        self.assertEqual(obj["amount"], "1")

        # TODO: more

    def test_asset_class_info(self):
        data = self.api.get_asset_class_info(469432309)

        self.assertTrue(data["success"])

        obj = data["469432309"]
        self.assertEqual(obj["classid"], "469432309")
        self.assertEqual(obj["type"], "Base Grade Container")

        # TODO: more

