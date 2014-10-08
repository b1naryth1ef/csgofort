import socket

from flask import Flask
from flask.ext.openid import OpenID
from flask.ext.cors import cross_origin
from config import SECRET_KEY

LOCAL = (socket.gethostname() != "kato")

class CustomFlask(Flask):
    @cross_origin()
    def send_static_file(self, filename):
        return Flask.send_static_file(self, filename)

# If we're local, we need to enable CORS. Remote uses nginx for this.
if LOCAL:
    csgofort = CustomFlask("csgofort")
else:
    csgofort = Flask("csgofort")

csgofort.secret_key = SECRET_KEY
openid = OpenID(csgofort)

# This allows exceptions to bubble to uwsgi
csgofort.config['PROPAGATE_EXCEPTIONS'] = True

# Setup domain based on host

if LOCAL:
    csgofort.config["SERVER_NAME"] = "dev.csgofort.com:6015"
else:
    csgofort.config["SERVER_NAME"] = "csgofort.com"
