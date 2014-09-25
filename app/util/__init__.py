from flask import flash, redirect, request
from app import csgofort

import json

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