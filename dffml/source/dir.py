"""
Loads files from a directory
"""
import os
import glob
import pathlib
from typing import List

from ..record import Record
from ..base import config, field
from .memory import MemorySource
from .file import FileSource
from ..util.entrypoint import entrypoint
from dffml.source.source import BaseSource, BaseSourceContext
from ..configloader.configloader import ConfigLoaders


class FolderNotFoundError(Exception):
    """
    Folder doesn't exist.
    """


@config
class DirectorySourceConfig:
    foldername: pathlib.Path
    feature: str = field("Name of the feature the data will be referenced as")
    labels: List[str] = None
    loadfile: bool = False
    save: bool = False  # TODO It'll be a good idea to give the user option to save extracted features in some format


@entrypoint("dir")
class DirectorySource(MemorySource):
    """
    Source to read files in a folder.
    """

    CONFIG = DirectorySourceConfig
    CONFIG_LOADER = ConfigLoaders()

    def __init__(self, config):
        super().__init__(config)

    async def __aenter__(self) -> "BaseSourceContext":
        await self._open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._close()

    async def _open(self):
        if not os.path.exists(self.config.foldername) and not os.path.isdir(
            self.config.filename
        ):
            raise FolderNotFoundError(f"Folder path: {self.config.foldername}")

        # TODO if user provides a file having all the label names
        if len(self.config.labels) == 1 and self.config.labels is not None:
            if os.path.isfile(self.config.labels[0]):
                self.config.labels = pathlib.Path.read_text(
                    pathlib.Path(self.config.labels[0])
                ).split(",")

        if not set(
            [
                label_folders
                for label_folders in os.listdir(self.config.foldername)
            ]
        ) == set(self.config.labels):
            print(
                "\nWrite all labels not specified (give list of all label folders preset)\n"
            )
            # don't give exception if labels provided < label folder numbers
            # only give exception if a labelfolder doesn't exist (covers spelling errors)

        # folder = open(self.config.foldername, )
        await self.load_fd()

    async def _close(self):
        if self.config.save:
            # TODO Save preprocessed data to a new folder
            # So that user doesn't have to do preprocessing again and again
            await self.dump_fd()

    async def load_fd(self):
        self.mem = {}
        i = 0
        for label in self.config.labels:
            label_folder = self.config.foldername.joinpath(label)
            for file_name in os.listdir(label_folder):
                feature = label_folder.joinpath(file_name)

                if self.config.loadfile:
                    async with self.CONFIG_LOADER as cfgl:
                        _, feature = await cfgl.load_file(feature)
                self.mem[str(i)] = Record(
                    str(i),
                    data={
                        "features": {
                            self.config.feature: feature,
                            "label": label,
                        }
                    },
                )
                i += 1
                break
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        raise NotImplementedError
