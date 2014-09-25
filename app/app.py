import socket

from flask import Flask
from flask.ext.openid import OpenID
from flask.ext.cors import cross_origin

class CustomFlask(Flask):
    @cross_origin()
    def send_static_file(self, filename):
        return Flask.send_static_file(self, filename)

LOCAL = (socket.gethostname() != "kato")

if LOCAL:
    csgofort = Flask("csgofort")
else:
    csgofort = CustomFlask("csgofort")

csgofort.secret_key = "1337"
openid = OpenID(csgofort)

# Setup domain based on host
if LOCAL:
    csgofort.config["SERVER_NAME"] = "dev.csgofort.com:6015"
else:
    csgofort.config["SERVER_NAME"] = "csgofort.com"

def register_views():
    from views.public import public
    from views.auth import auth
    from market.market import market
    from vacdex.vacdex import vacdex

    csgofort.register_blueprint(public)
    csgofort.register_blueprint(auth)
    csgofort.register_blueprint(market)
    csgofort.register_blueprint(vacdex)

