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
from ..util.entrypoint import entrypoint
from ..source.source import BaseSource
from ..configloader.configloader import ConfigLoaders
from ..high_level import save


class FolderNotFoundError(Exception):
    """
    Folder doesn't exist.
    """


@config
class DirectorySourceConfig:
    foldername: str
    feature: str = field("Name of the feature the data will be referenced as")
    labels: List[str] = field(
        "Image labels", default_factory=lambda: ["unlabelled"]
    )
    save: BaseSource = None


@entrypoint("dir")
class DirectorySource(MemorySource):
    """
    Source to read files in a folder.
    """

    CONFIG = DirectorySourceConfig
    CONFIG_LOADER = ConfigLoaders()

    def __init__(self, config):
        super().__init__(config)
        if isinstance(getattr(self.config, "foldername", None), str):
            self.config.foldername = pathlib.Path(self.config.foldername)

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

        if (
            self.config.labels != ["unlabelled"]
            and len(self.config.labels) == 1
        ):
            if os.path.isfile(self.config.labels[0]):
                # Update labels with list read from the file
                self.config.labels = pathlib.Path.read_text(
                    pathlib.Path(self.config.labels[0])
                ).split(",")

        elif self.config.labels != ["unlabelled"]:
            label_folders = [
                labels
                for labels in os.listdir(self.config.foldername)
                if os.path.isdir(os.path.join(self.config.foldername, labels))
            ]
            # Check if all existing label folders are given to `labels` list
            if set(label_folders) > set(self.config.labels):
                self.logger.warning(
                    "All labels not specified. Folders present: %s \nLabels entered: %s",
                    label_folders,
                    self.config.labels,
                )

        await self.load_fd()

    async def _close(self):
        if self.config.save:
            await save(self.config.save, self.mem)

    async def load_fd(self):
        self.mem = {}

        # Iterate over the labels list
        for label in self.config.labels:
            if self.config.labels == ["unlabelled"]:
                folders = self.config.foldername
            else:
                folders = self.config.foldername.joinpath(label)

            # Go through all image files and read them using pngconfigloader
            for file_name in map(
                os.path.basename, glob.glob(str(folders) + "/*")
            ):
                image_filename = folders.joinpath(file_name)
                async with self.CONFIG_LOADER as cfgl:
                    _, feature_data = await cfgl.load_file(image_filename)

                if self.config.labels != ["unlabelled"]:
                    file_name = label + "/" + file_name

                self.mem[file_name] = Record(
                    file_name,
                    data={
                        "features": {
                            self.config.feature: feature_data,
                            "label": label,
                        }
                    },
                )

                if self.config.labels == ["unlabelled"]:
                    del self.mem[file_name].features()["label"]

        self.logger.debug("%r loaded %d records", self, len(self.mem))
