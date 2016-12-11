import sys
import logging


def setup_logging(app, settings):
    # Setup logging
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    fmt = logging.Formatter(settings.get('logging.format', '%(asctime)s <%(levelname)s> %(message)s'))
    ch.setFormatter(fmt)
    app.logger.addHandler(ch)
