import socket

from flask import Flask
from flask.ext.openid import OpenID
from flask.ext.cors import cross_origin

class CustomFlask(Flask):
    @cross_origin()
    def send_static_file(self, filename):
        return Flask.send_static_file(self, filename)

csgofort = CustomFlask("csgofort")
csgofort.secret_key = "1337"
openid = OpenID(csgofort)

# Setup domain based on host
LOCAL = (socket.gethostname() != "kato")
if LOCAL:
    csgofort.config["SERVER_NAME"] = "dev.csgofort.com:6015"
else:
    csgofort.config["SERVER_NAME"] = "csgofort.com"

def register_views():
    from views.public import public
    from views.auth import auth
    from views.ui import ui
    from maz.maz import maz
    from vacdex.vacdex import vacdex

    csgofort.register_blueprint(public)
    csgofort.register_blueprint(auth)
    csgofort.register_blueprint(ui)
    csgofort.register_blueprint(maz)
    csgofort.register_blueprint(vacdex)

