import sys
from loguru import logger


class Logger:
    @staticmethod
    def generate(level="DEBUG"):
        logger.configure(
            handlers=[
                dict(
                    sink=sys.stdout,
                    enqueue=True,
                    backtrace=True,
                    diagnose=True,
                    colorize=True,
                    level=level,
                )
            ],
        )
        return logger
