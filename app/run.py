#!/usr/bin/env python
from app import csgofort, register_views
import sys

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print "Usage: ./run.py <app|crawler|sched>"
        sys.exit(1)

    if sys.argv[1] == "app":
        register_views()
        csgofort.run(debug=True, port=6015, host="0.0.0.0")

    if sys.argv[1] == "crawler":
        from maz.crawler import run
        run()

    if sys.argv[1] == "sched":
        from scheduler.run import sched
        sched.run()