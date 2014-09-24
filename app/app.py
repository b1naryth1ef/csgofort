import socket
from flask import Flask

csgofort = Flask("csgofort")

# Setup domain based on host
if socket.gethostname() == "kato":
    csgofort.config["SERVER_NAME"] = "csgofort.com"
else:
    csgofort.config["SERVER_NAME"] = "dev.csgofort.com:6015"

def register_views():
    from views.public import public
    from marketdex.marketdex import marketdex
    from vacdex.vacdex import vacdex

    csgofort.register_blueprint(public)
    csgofort.register_blueprint(marketdex)
    csgofort.register_blueprint(vacdex)

