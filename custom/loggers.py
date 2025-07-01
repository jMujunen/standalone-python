import logging
from logging import Logger

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    "WARNING": YELLOW,
    "INFO": GREEN,
    "DEBUG": BLUE,
    "CRITICAL": "\033[1;91m",
    "ERROR": RED,
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        color = COLOR_SEQ % (30 + COLORS.get(levelname, 0))
        record.levelname = f"{color}[{levelname}]{RESET_SEQ}"
        return super().format(record)


class ColoredLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name, logging.DEBUG)
        color_handler = logging.StreamHandler()
        color_handler.setFormatter(
            ColoredFormatter(
                fmt="\033[1m%(asctime)s\33[0m %(levelname)s - %(funcName)s() - %(message)s",
                datefmt="%-I:%M %-Ss",
            )
        )
        self.addHandler(color_handler)


logging.setLoggerClass(ColoredLogger)
logger: Logger = logging.getLogger(__name__)
