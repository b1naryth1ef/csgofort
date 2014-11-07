import socket, os

from flask import Flask
from flask.ext.openid import OpenID
from flask.ext.cors import cross_origin
import config

# Load config data from local config, bit hackey but it works
compiled_cfg = {}
for attr in dir(config):
    compiled_cfg[attr] = config.__dict__[attr]

# This is a custom class for local development, which handles CORS
class CustomFlask(Flask):
    @cross_origin()
    def send_static_file(self, filename):
        return Flask.send_static_file(self, filename)

# If we're local, we need to enable CORS. Remote uses nginx for this.
if compiled_cfg["ENV"] == "local":
    csgofort = CustomFlask("csgofort")
else:
    csgofort = Flask("csgofort")

csgofort.config.update(compiled_cfg)
csgofort.secret_key = csgofort.config["SECRET_KEY"]
openid = OpenID(csgofort)

# This allows exceptions to bubble to uwsgi
csgofort.config['PROPAGATE_EXCEPTIONS'] = True

# Setup domain based on host, dev.csgofort.com is aliased to 127.0.0.1
#  for ease of development.
if csgofort.config["ENV"] == "local":
    # TODO: fix this up a bit
    if socket.gethostname() == "eos":
        csgofort.config["SERVER_NAME"] = "eos.csgofort.com:6015"
    else:
        csgofort.config["SERVER_NAME"] = "dev.csgofort.com:6015"

    from werkzeug.contrib.profiler import ProfilerMiddleware
    csgofort.config['PROFILE'] = True
    f = open('/tmp/profiler.log', 'w')
    csgofort.wsgi_app = ProfilerMiddleware(csgofort.wsgi_app, f, restrictions=[30])
else:
    csgofort.config["SERVER_NAME"] = "csgofort.com"

def build_js_templates():
    TEMPLATES = "var T = {};"

    for (curdir, dirs, files) in os.walk("templates/"):
        for fname in files:
            if "js" in curdir and fname.endswith(".html"):
                p = open(os.path.join(curdir, fname))
                TEMPLATES += 'T["%s"] = _.template("%s");' % (
                    fname.rsplit(".", 1)[0],
                    p.read().replace("\n", "").replace('"', "'")
                )
                p.close()

    with open("static/js/templates.js", "w") as f:
        f.write(TEMPLATES)

build_js_templates()

if __name__ == "__main__":
    print "Run the web app with: ./run.py app"
