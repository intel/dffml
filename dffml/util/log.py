# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""Logging"""
import logging

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
