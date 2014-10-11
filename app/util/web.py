# -*- coding: utf-8 -*-
import requests, json
from database import red

TWO_HOURS = 60 * 60 * 2

CURRENCY_SYM = {
    "CNY": u"¥",
    "EUR": u"€",
    "GBP": u"£",
    "ILS": u"₪",
    "JPY": u"¥",
    "KRW": u"₩",
    "THB": u"฿",
    "VND": u"₫",
    "ZAR": u"R",
}
def get_sym(cur):
    return CURRENCY_SYM.get(cur, "$")

def get_currencies(cache=True):
    if red.exists("curlist") and cache:
        return json.loads(red.get("curlist"))
    li = requests.get("http://www.freecurrencyconverterapi.com/api/v2/currencies")
    result = sorted(map(lambda i: i, li.json()["results"].keys()))
    red.set("curlist", json.dumps(result))
    return result

def get_exchange_rate(from_c, to_c):
    key = "%s_%s" % (from_c, to_c)
    if red.exists(key):
        return float(red.get(key))

    r = requests.get("http://www.freecurrencyconverterapi.com/api/v2/convert", params={
        "q": key,
        "compact": "y"
    })
    data = r.json()[key]["val"]

    red.setex(key, data, TWO_HOURS)
    return data

def usd_convert(value, to_c):
    if to_c == "USD": return value

    return get_exchange_rate("USD", to_c) * float(value)
