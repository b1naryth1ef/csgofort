from dateutil.relativedelta import relativedelta
from datetime import datetime
import time, thread, logging, signal, sys, os, inspect

log = logging.getLogger(__name__)

class Task(object):
    def __init__(self, f, now, delta):
        self.f = f
        self.delta = delta
        self.last = (datetime.utcnow() - relativedelta(years=5)) if now else datetime.utcnow()
        self.active = True
        self.running = False

    def should_run(self):
        return (self.active and not self.running and (datetime.utcnow() > (self.last + self.delta)))

    def run(self):
        log.info("Running task %s..." % self.f.__name__)
        start = time.time()
        self.last = datetime.utcnow()
        self.running = True

        # Attempt to run the job
        try:
            self.f()
        except Exception:
            log.exception("Task %s failed in %ss" % (self.f.__name__, time.time() - start))
            self.running = False
            return

        self.running = False
        log.info("Task %s completed in %ss" % (self.f.__name__, time.time() - start))

class Scheduler(object):
    def __init__(self):
        # Write PID to a file
        try:
            with open("/var/run/csgofortsched.pid", "w") as f:
                f.write(str(os.getpid()))
        except:
            log.exception("Failed to create PID file: ")

        self.schedules = []
        self.paused = False

        log.info("Binding signal handlers")
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGHUP, self.handle_signal)

    def wait_for_jobs(self, timeout=3600):
        for _ in xrange(timeout):
            if not any(map(lambda i: i.running, self.schedules)):
                break
            time.sleep(1)
        else:
            raise Exception("Timeout Reached, %s jobs still running (%s)" % (len(self.schedules), self.schedules))

    def safe_stop(self):
        self.paused = True
        sys.exit(1)

    def restart(self):
        log.info("Restarting scheduler...")
        self.paused = True

        for job in self.schedules:
            log.info("Reloading %s" % job.f.__name__)
            job.f = getattr(reload(inspect.getmodule(job.f)), job.f.__name__)
        self.paused = False

    def handle_signal(self, signum, handler):
        log.info("Handling signal %s" % signum)
        if signum == signal.SIGINT:
            self.safe_stop()
        elif signum == signal.SIGTERM:
            sys.exit(1)
        elif signum == signal.SIGHUP:
            self.restart()

    def add_task(self, f, start_now=False, **kwargs):
        self.schedules.append(Task(f, start_now, relativedelta(**kwargs)))

    def schedule(self, start_now=False, **kwargs):
        def deco(f):
            self.add_task(f, start_now, **kwargs)
            return f
        return deco

    def run(self):
        log.info("Starting Scheduler...")
        while True:
            time.sleep(.3)
            if self.paused: continue

            for task in self.schedules:
                if task.should_run():
                    thread.start_new_thread(task.run, ())

