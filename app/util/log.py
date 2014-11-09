import logging

LEVELS = {
    "elasticsearch": logging.WARN,
    "urllib3": logging.WARN,
    "requests": logging.WARN,
    "peewee": logging.INFO,
}

FORMAT = "[%(levelname)s] %(asctime)s - %(name)s:%(lineno)d - %(message)s"

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    set_logging_levels()

    file_handler = logging.FileHandler('/tmp/csgofort.log')
    file_handler.setFormatter(logging.Formatter(FORMAT))

    root = logging.getLogger()
    root.addHandler(file_handler)

def set_logging_levels():
    for log, lvl in LEVELS.items():
        logging.getLogger(log).setLevel(lvl)
