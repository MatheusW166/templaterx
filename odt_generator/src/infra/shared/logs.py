import inspect
import logging
import sys
import os
from logging.handlers import RotatingFileHandler


DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
LOGS_DIR = "logs/"


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = DEFAULT_FORMAT

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


if not os.path.isdir(LOGS_DIR):
    os.mkdir(LOGS_DIR)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(CustomFormatter())

logging.basicConfig(
    level=logging.DEBUG,
    format=DEFAULT_FORMAT,
    handlers=[
        stream_handler,
        RotatingFileHandler(
            filename=LOGS_DIR+"app.log",
            mode="a",
            maxBytes=5*1024*1024,
            backupCount=2,
        )
    ]
)


class Logger:
    @classmethod
    def get_logger(cls, name=None):
        if name is None:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            name = module.__name__ if module else "__main__"

        return logging.getLogger(name)
