import logging
from logging import LogRecord
from typing import Any, cast

SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")


class CustomLogger(logging.Logger):
    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, message, args, **kwargs)


logging.setLoggerClass(CustomLogger)


class CustomFormatter(logging.Formatter):
    green = "\x1b[32;1m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    BASE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + BASE_FORMAT + reset,
        logging.INFO: grey + BASE_FORMAT + reset,
        logging.WARNING: yellow + BASE_FORMAT + reset,
        logging.ERROR: red + BASE_FORMAT + reset,
        logging.CRITICAL: bold_red + BASE_FORMAT + reset,
        SUCCESS: green + BASE_FORMAT + reset,
    }

    def format(self, record: LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.BASE_FORMAT)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


_logger = cast(CustomLogger, logging.getLogger(__name__))
_logger.setLevel(logging.DEBUG)

_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(CustomFormatter())

_logger.addHandler(_ch)
