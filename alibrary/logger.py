"""Aerosint logger

Custom logger using the built-in logging package.
It allows to log the requests made to the server and custom execution messages.
It also has different flavors depending on if it is a debug mode or not.
"""

import logging
import os
import time
from logging import Formatter
from logging.config import dictConfig

from flask import Flask, Response, g, request

is_debug_active = bool(os.environ.get("FLASK_DEBUG"))


class ColoredFormatter(Formatter):
    """Custom logger formatter.

    It will colorize the logging output according to the logging level.
    """
    grey = "\x1b[37;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    blue = "\x1b[34;20m"
    magenta = "\x1b[35;20m"
    cyan = "\x1b[36;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_format = "[{asctime}] {levelname:>8}: {message}"

    FORMATS = {
        logging.DEBUG: blue + log_format + reset,
        logging.INFO: grey + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset
    }

    def format(self, record):
        """Format the specified record as text.

        It picks the color according to the log level and then uses the { style
        format string to generate the log text.

        Args:
            record: A LogRecord to format
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, style="{")
        return formatter.format(record)


def config_logger(debug: bool = False):
    """Configures the aerosint logger.

    The given debug flag defines the log level.
    """
    dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "console": {
                "()": ColoredFormatter,
            },
            "text_file": {
                "()": ColoredFormatter,
            },
        },
        "handlers": {
            "aerosint_console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "console",
                "stream": "ext://sys.stdout",
            },
            "aerosint": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "text_file",
                "filename": "aerosint.log",
                "maxBytes": 10485760,  # 10 Mb = 10 * 1024 * 1024
                "backupCount": 10,
            },
        },
        "loggers": {
            "aerosint": {
                "level": "INFO" if not debug else "DEBUG",
                "propagate": False,
                "handlers": ["aerosint"] if not debug else ["aerosint_console"]
            },
        }
    })


def start_handler_timer():
    """Stores the current time in a Flask session variable"""

    if "start" not in g:
        g.start = time.time()


def log_request(response: Response) -> Response:
    """Logs a request from its response.

    Args:
        response: The Response that is about to be return to the client.

    Returns:
        The Response object that it receive.
    """
    now = time.time()
    handling_duration = round(now - g.start, 3)

    logging.getLogger("aerosint").debug(
        "Request %-7s %-50s - %d (handled in %06.3fs)", request.method,
        request.path, response.status_code, handling_duration)

    return response


def init_logger(app: Flask):
    """Initializes the custom logger inside the Flask application."""
    app.before_request(start_handler_timer)
    app.after_request(log_request)

    log = logging.getLogger("werkzeug")
    log.disabled = True


config_logger(is_debug_active)
logger = logging.getLogger("aerosint")
