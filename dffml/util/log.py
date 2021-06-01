# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""Logging"""
import time
import logging
import inspect
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
    logger.addFilter(duplicate_filter)
    return logger


def log_time(func):
    """ 
    Decorator that can take either coroutine or normal function
    and log its runtime.
    """

    logger = LOGGER.getChild("duration_logger")

    @contextmanager
    def time_it():
        start_ts = time.monotonic()
        yield
        dur = time.monotonic() - start_ts
        logger.debug("{} took {:.2} seconds".format(func.__name__, dur))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if inspect.iscoroutinefunction(func):

            async def tmp():
                with time_it():
                    return await func(*args, **kwargs)

            return tmp()

        else:
            with time_it():
                return func(*args, **kwargs)

    return wrapper
