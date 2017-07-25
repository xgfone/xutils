# encoding: utf-8
from __future__ import print_function, absolute_import, unicode_literals, division

import logging


def init_logging(logger=None, level="DEBUG", log_file="", init_handler=None,
                 max_count=30, propagate=False, file_config=None, dict_config=None):
    # Initialize the argument logger with the arguments, level and log_file.
    if logger:
        fmt = "%(asctime)s - %(process)d - %(pathname)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

        level = getattr(logging, level.upper())

        if log_file:
            if init_handler:
                handler = init_handler(log_file, max_count)
            else:
                from logging.handlers import TimedRotatingFileHandler
                handler = TimedRotatingFileHandler(log_file, when="midnight",
                                                   interval=1, backupCount=max_count)
        else:
            handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)

        loggers = logger if isinstance(logger, (list, tuple)) else [logger]
        for logger in loggers:
            logger.propagate = propagate
            logger.setLevel(level)
            logger.addHandler(handler)

    # Initialize logging by the configuration file, file_config.
    if file_config:
        logging.config.fileConfig(file_config, disable_existing_loggers=False)

    # Initialize logging by the dict configuration, dict_config.
    if dict_config and hasattr(logging.config, "dictConfig"):
        logging.config.dictConfig(dict_config)
