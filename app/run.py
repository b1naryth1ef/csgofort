#!/usr/bin/env python
from app import csgofort
from util.log import setup_logging
import sys

# Import all the routes we need
from views.public import public
from views.auth import auth
from views.ui import ui
from views.admin import admin
from maz.maz import maz
from vactrak.vactrak import vactrak

# Register the routes with the flask app
csgofort.register_blueprint(public)
csgofort.register_blueprint(auth)
csgofort.register_blueprint(ui)
csgofort.register_blueprint(admin)
csgofort.register_blueprint(maz)
csgofort.register_blueprint(vactrak)

# Setup logging and mute some annoying loggers
setup_logging()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage: ./run.py <app|sched|once>"
        sys.exit(1)

    if sys.argv[1] == "app":
        csgofort.run(debug=True, port=6015, host="0.0.0.0")

    if sys.argv[1] == "sched":
        from scheduler.run import sched
        sched.run()

    if sys.argv[1] == "once":
        import scheduler.run

        if len(sys.argv) < 3:
            print "Usage: ./run.py once <task>"
            sys.exit(1)

        if sys.argv[2] in dir(scheduler.run):
            getattr(globals()["scheduler"].run, sys.argv[2])()
