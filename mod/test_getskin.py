import requests, pprint

TEST = "http://steamcommunity.com/profiles/{}/inventory/json/{}/{}/"

url = TEST.format(76561198037632722, 730, 2)

x = requests.get(url).json()