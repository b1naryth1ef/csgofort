from flask import flash, redirect, request, jsonify
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
