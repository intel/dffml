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
            self.config.foldername
        ):
            raise FolderNotFoundError(f"Folder path: {self.config.foldername}")

        # TODO doubt: Should we add a way where if user provides a file having all the label names we can read that file
        if len(self.config.labels) == 1 and self.config.labels is not None:
            if os.path.isfile(self.config.labels[0]):
                # Update labels with list rea from the file
                self.config.labels = pathlib.Path.read_text(
                    pathlib.Path(self.config.labels[0])
                ).split(",")

        label_folders = list(
            set(labels for labels in os.listdir(self.config.foldername))
        )
        # Check if all existing label folders are given to `labels` list
        if label_folders > self.config.labels:
            self.logger.warning(
                "All labels not specified. Folders present: %s \nLabels entered: %s",
                label_folders,
                self.config.labels,
            )

        await self.load_fd()

    async def _close(self):
        if self.config.save:
            # TODO doubt: Should we save preprocessed data to a new folder/file
            # So that user doesn't have to do preprocessing again and again later?
            await self.dump_fd()

    async def load_fd(self):
        self.mem = {}
        i = 0

        """
        Example cli:
        dffml list records -sources f=dir \
            -source-foldername dataset/train \
            -source-feature image \
            -source-labels airplane bird frog \
            -log debug

        | -- dataset
        | -- | -- train
        | -- | -- | -- label_1
        | -- | -- | -- | -- image_1.png
        | -- | -- | -- | -- image_2.png
        | -- | -- | -- | -- .....
        | -- | -- | -- label_2
        | -- | -- | -- | -- image_1.png
        | -- | -- | -- | -- image_2.png
        | -- | -- | -- | -- .....
        """

        # Iterate over the labels list
        for label in self.config.labels:
            label_folder = self.config.foldername.joinpath(label)
            # Go through all image files and read them using pngconfigloader
            for file_name in os.listdir(label_folder):
                image_filename = label_folder.joinpath(file_name)

                # I have added an example directory with images renamed with .mnistpng as the pngconfigloader isn't updated
                async with self.CONFIG_LOADER as cfgl:
                    _, feature_data = await cfgl.load_file(image_filename)

                self.mem[str(i)] = Record(
                    str(i),
                    data={
                        "features": {
                            self.config.feature: feature_data,
                            "label": label,
                        }
                    },
                )
                i += 1
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        raise NotImplementedError
