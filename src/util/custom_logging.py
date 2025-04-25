"""Custom Logging"""
# https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output

import os
import logging
from enum import StrEnum
from typing import Literal

# import typer
from util.colors import COLOR

# log message format
# https://docs.python.org/3/library/logging.html#logrecord-attributes
LOGGING_TIMESTAMP = "%d.%m.%y %H:%M:%S"  # Datetime format
# MSG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-20s %(module)s [%(name)s.%(funcName)s(%(lineno)d)] %(message)s"
# colored format
MSG_FORMAT = f"{COLOR.CYAN0.value}%(asctime)s.%(msecs)03d %(levelname)-20s {COLOR.PURPLE0.value}%(module)-18s {COLOR.BLUE0.value}%(name)s.%(funcName)-25s(%(lineno)d) %(message)s"

RESET = COLOR.RESET.value
BOLD = COLOR.BOLD.value
ENV_MY_LOGLEVEL = "MY_LOGLEVEL"
ENV_MY_LOGLEVEL_INT = "MY_LOGLEVEL_INT"


class LOGGING_COLORS(StrEnum):
    """Colors used for logging"""

    DEBUG = COLOR.GREEN0.value
    INFO = COLOR.SKY_BLUE.value
    WARNING = COLOR.ORANGE.value
    ERROR = COLOR.RED1.value
    CRITICAL = COLOR.RED_BG1.value


class LOGGING_EMOJIS(StrEnum):
    """Emojis used for logging"""

    DEBUG = "💻"
    INFO = "🟦"
    WARNING = "🟨"
    ERROR = "🟥"
    CRITICAL = "🔥"


COL_LOGLEVELS = [c.name for c in LOGGING_COLORS]


class ColoredFormatter(logging.Formatter):
    """Log Message Formatter"""

    def __init__(self, msg, use_color=True):
        """constructor"""
        logging.Formatter.__init__(self, msg, LOGGING_TIMESTAMP)
        self.use_color = use_color

    @staticmethod
    def msg_formatter(msg_formatted, use_color=True):
        """formatting the message"""
        if use_color:
            msg_formatted = msg_formatted.replace("$RESET", RESET).replace("$BOLD", BOLD)
        else:
            msg_formatted = msg_formatted.replace("$RESET", "").replace("$BOLD", "")
        return msg_formatted

    def format(self, record):
        """formatting the log message"""
        levelname = record.levelname.upper()
        if self.use_color and levelname.upper() in COL_LOGLEVELS:
            # levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            _loglevel_color = LOGGING_COLORS[levelname].value
            _loglevel_emoji = LOGGING_EMOJIS[levelname].value
            # somehow the formatting is not working
            _indent = (11 - len(levelname)) * " "
            levelname_color = _loglevel_color + levelname + _indent + RESET
            record.levelname = levelname_color
            record.msg = f"{_loglevel_emoji} {_loglevel_color}{record.getMessage()}{RESET}"
        return logging.Formatter.format(self, record)


class ColoredLogger(logging.Logger):
    """logger supporting colors and emojis"""

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        _color_formatter = ColoredFormatter(ColoredFormatter.msg_formatter(MSG_FORMAT, use_color=True))

        _console = logging.StreamHandler()
        _console.setFormatter(_color_formatter)
        self.addHandler(_console)
        return


def get_log_level(level: Literal["debug", "info", "warning", "error", "critical"] | None = "info") -> int:
    """retrieving loglevel either via param or via an env variable MY_LOGLEVEL using literal instead of int value"""
    out: int = None
    _log_level_dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    _loglevel_env: str = os.environ.get(ENV_MY_LOGLEVEL)

    if _loglevel_env:
        out = _log_level_dict[_loglevel_env.lower()]
    else:
        out = _log_level_dict[level.lower()]
    logger.debug(f"Setting Loglevel, env MY_LOGLEVEL [{_loglevel_env}], input [{level}], out [{out}]")
    # setting it as env variable
    os.environ[ENV_MY_LOGLEVEL_INT] = str(out)
    return out


# logging class needs to be set before anything else
logging.setLoggerClass(ColoredLogger)
logger = logging.getLogger(__name__)


def main():
    """test the logger"""
    logger.debug("DEBUG MESSAGE")
    logger.info("INFO MESSAGE")
    logger.warning("WARNING MESSAGE")
    logger.error("ERROR MESSAGE")
    logger.critical("CRITICAL MESSAGE")


if __name__ == "__main__":
    loglevel = get_log_level(level="debug")
    main()
