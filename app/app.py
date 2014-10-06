import socket

from flask import Flask
from flask.ext.openid import OpenID
from flask.ext.cors import cross_origin
from config import SECRET_KEY

class CustomFlask(Flask):
    @cross_origin()
    def send_static_file(self, filename):
        return Flask.send_static_file(self, filename)

csgofort = CustomFlask("csgofort")
csgofort.secret_key = SECRET_KEY
openid = OpenID(csgofort)

# This allows exceptions to bubble to uwsgi
csgofort.config['PROPAGATE_EXCEPTIONS'] = True

# Setup domain based on host
LOCAL = (socket.gethostname() != "kato")
if LOCAL:
    csgofort.config["SERVER_NAME"] = "dev.csgofort.com:6015"
else:
    csgofort.config["SERVER_NAME"] = "csgofort.com"
