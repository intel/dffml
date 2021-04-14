# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""Logging"""
import time
import logging
import asyncio
import functools
from contextlib import contextmanager

LOGGER = logging.getLogger(__package__)


class DuplicateFilter(object):
    """
    Filter for logging only unique logs for download logger.
    """

    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv


def get_download_logger(root_logger):
    """
    Helper function to create a child logger for displaying download progress
    """
    logger = root_logger.getChild("download_logger")

    duplicate_filter = DuplicateFilter()
    progress_handler = logging.StreamHandler()
    formatter = logging.Formatter("\x1b[80D\x1b[K%(message)s")

    progress_handler.setFormatter(formatter)
    progress_handler.terminator = ""
    logger.addHandler(progress_handler)
    logger.addFilter(duplicate_filter)

    return logger


def log_time(func):
    """ 
    Decorator that can take either coroutine or normal function 
    
    Found on Stack Overflow from Mikhail Gerasimov, only modified 
    slightly to fit our needs.
    - https://stackoverflow.com/a/44176794/10108465
    - https://creativecommons.org/licenses/by-sa/3.0/
    """

    logger = LOGGER.getChild("duration_logger")

    @contextmanager
    def time_it():
        start_ts = time.time()
        yield
        dur = time.time() - start_ts
        logger.debug("{} took {:.2} seconds".format(func.__name__, dur))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with time_it():
                return func(*args, **kwargs)
        else:

            async def tmp():
                with time_it():
                    return await func(*args, **kwargs)

            return tmp()

    return wrapper
