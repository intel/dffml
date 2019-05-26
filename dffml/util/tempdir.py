# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Create and remove OS temporary directories.
"""
import queue
import shutil
import os.path
import tempfile
from typing import List

from .log import LOGGER

LOGGER = LOGGER.getChild("tempdir")


class TempDir(object):
    """
    Creates and deletes temporary directories. Removes any created directories
    when the program using this class terminates (see rmtempdirs for details).
    """

    SUFFIX: str = None
    PREFIX: str = "dffml_"

    def __init__(self):
        self.suffix = self.__class__.SUFFIX
        self.prefix = self.__class__.PREFIX
        self.dirs: List[str] = []

    def mktempdir(self):
        """
        Creates a temporary directory using TempDir's SUFFIX and PREFIX.
        Adds the directory to the to be deleted queue.
        """
        dirname = tempfile.mkdtemp(suffix=self.suffix, prefix=self.prefix)
        LOGGER.debug("Created directory %r", dirname)
        self.dirs.append(dirname)
        return dirname

    def rmtempdirs(self):
        """
        Removes all created temporary directories. Decorated with the
        atexit.register method to ensure all created directories will be removed
        on termination.
        """
        for rmdir in self.dirs:
            LOGGER.debug("Removing directory %r", rmdir)
            # OSError 39 sometimes if removal isn't attempted twice
            shutil.rmtree(rmdir, ignore_errors=True)
            shutil.rmtree(rmdir, ignore_errors=True)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.rmtempdirs()
