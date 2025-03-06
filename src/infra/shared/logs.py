import inspect
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

LOGS_DIR = "logs/"

if not os.path.isdir(LOGS_DIR):
    os.mkdir(LOGS_DIR)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
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
