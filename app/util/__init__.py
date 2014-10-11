from flask import flash, redirect, request, jsonify, g
from app import csgofort

import json, time

def rounds(x, base=5):
    return int(base * round(float(x) / base))

def with_timing(f, args, kwargs={}):
    start = time.time()
    return (f(*args, **kwargs), time.time() - start)

def flashy(m, f="danger", u="/"):
    flash(m, f)
    return redirect(u)

def build_url(realm, path):
    if realm == "public":
        realm = None

    realm = ("%s." % realm) if realm else ""
    return "http://%s%s/%s" % (realm, csgofort.config["SERVER_NAME"], path)

@csgofort.context_processor
def util_ctx_proc():
    return {
        "build_url": build_url,
        "DOMAIN": csgofort.config["SERVER_NAME"],
        "REALM": request.blueprint
    }

@csgofort.template_filter("jsonify")
def jsonify_filter(x):
    return json.dumps(x, indent=4)

@csgofort.template_filter("convertu")
def convertu_filter(value, user):
    from util.web import usd_convert, get_sym
    if user:
        cur = user.currency
    else:
        cur = "USD"
    return u"{0}{1:.2f}".format(get_sym(cur), usd_convert(value, cur))

class APIError(Exception):
    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

    def toDict(self):
        resp = {
            "success": False,
            "error": self.message
        }

        if self.payload:
            resp.update(self.payload)

        return resp

@csgofort.errorhandler(APIError)
def handle_api_error(err):
    return jsonify(err.toDict())

@csgofort.before_request
def before_request():
    g.start = time.time()

@csgofort.teardown_request
def teardown_request(r):
    from fortdb import GraphMetric
    GraphMetric.mark("request_time", time.time() - g.start)
    GraphMetric.mark("request_count", 1)
