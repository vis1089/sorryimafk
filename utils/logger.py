import logging
import os
import sys


class ColorFormatter(logging.Formatter):
    """
    The ColorFormatter class provides methods for formatting log messages with color (ansi escape codes)
    """

    # Colors
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"  # reset back to normal formatting
    format = "[%(asctime)s - %(name)s - %(levelname)s] - %(message)s (%(filename)s:%(lineno)d)"  # log message format
    datefmt = '%Y-%m-%d %H:%M:%S'

    FORMATS = {  # set the log format for each level
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):  # override the format method
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Formatter(logging.Formatter):
    """
    The Formatter class provides methods for formatting log messages without color
    """

    format = "[%(asctime)s - %(name)s - %(levelname)s] - %(message)s (%(filename)s:%(lineno)d)"  # log message format
    datefmt = '%Y-%m-%d %H:%M:%S'

    FORMATS = {  # set the log format for each level
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):  # override the format method
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger(logging.Logger):
    """
    A custom logger with handlers for logging to a file and standard (console) output.
    """

    def __init__(self):
        super().__init__('afkbot')

    afkbot_logger = logging.getLogger('afkbot')
    afkbot_logger.setLevel(logging.DEBUG)  # Set the afkbot_logger level to debug for testing

    if not afkbot_logger.handlers:  # prevent duplicate messages
        file_handler = logging.FileHandler(filename=os.path.join(os.path.dirname(__file__), '..', 'afkbot.log'),
                                           encoding='utf-8', mode='w')
        file_handler.setFormatter(Formatter())
        afkbot_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)  # Use sys.stdout for standard output
        console_handler.setFormatter(ColorFormatter())
        afkbot_logger.addHandler(console_handler)
