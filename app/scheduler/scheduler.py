from dateutil.relativedelta import relativedelta
from datetime import datetime
import time, thread, logging

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
        self.schedules = []

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

            for task in self.schedules:
                if task.should_run():
                    thread.start_new_thread(task.run, ())
