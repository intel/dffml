# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""Logging"""
import logging

LOGGER = logging.getLogger(__package__)


def get_download_logger(root_logger):
    """
    Helper function to create a child logger for displaying download progress
    """
    logger = root_logger.getChild("download_logger")

    progress_handler = logging.StreamHandler()
    formatter = logging.Formatter("\x1b[80D\x1b[K%(message)s")

    progress_handler.setFormatter(formatter)
    progress_handler.terminator = ""
    logger.addHandler(progress_handler)

    return logger
