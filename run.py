from app import app


# Setup logging
import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter

format = "[%(asctime)s] p%(process)s\n" \
         "[%(levelname)s] in %(name)s: %(filename)s:%(lineno)d\n" \
         "%(message)s\n"

logging.basicConfig(
    filename=app.config.get('LOG_FILENAME', 'logs/flask.log'),
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
    format = format
)

logging.info(
    "\n"
    "==============================================================\n"
    "Mega-fMRI stimulus Rating Tool Flask application started\n"
    "PET-keskus (2018) \n"
)

handler = RotatingFileHandler('logs/flask.log', maxBytes=10000, backupCount=5)
handler.setFormatter(
    Formatter(format)
)
app.logger.addHandler(handler)

# Logging for production (nginx + gunicorn)
import os
is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
if is_gunicorn:
    app.logger.info("Application run through gunicorn")
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.info("******************")
    '''
else:
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    '''

# EOF

