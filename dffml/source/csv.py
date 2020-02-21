# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loads repos from a csv file, using columns as features
"""
import csv
import ast
import itertools
import asyncio
from typing import Dict
from dataclasses import dataclass
from contextlib import asynccontextmanager

from ..repo import Repo
from .memory import MemorySource
from .file import FileSource, FileSourceConfig
from ..base import config
from ..util.entrypoint import entrypoint

csv.register_dialect("strip", skipinitialspace=True)


@dataclass
class OpenCSVFile:
    write_out: Dict
    active: int
    lock: asyncio.Lock
    write_back_key: bool = True
    write_back_tag: bool = False

    async def inc(self):
        async with self.lock:
            self.active += 1

    async def dec(self):
        async with self.lock:
            self.active -= 1
            return bool(self.active < 1)


CSV_SOURCE_CONFIG_DEFAULT_KEY = "key"
CSV_SOURCE_CONFIG_DEFAULT_tag = "untagged"
CSV_SOURCE_CONFIG_DEFAULT_tag_COLUMN = "tag"


@config
class CSVSourceConfig(FileSourceConfig):
    key: str = CSV_SOURCE_CONFIG_DEFAULT_KEY
    tag: str = CSV_SOURCE_CONFIG_DEFAULT_tag
    tagcol: str = CSV_SOURCE_CONFIG_DEFAULT_tag_COLUMN


# CSVSource is a bit of a mess
@entrypoint("csv")
class CSVSource(FileSource, MemorySource):
    """
    Uses a CSV file as the source of repo feature data
    """

    CONFIG = CSVSourceConfig

    # Headers we've added to track data other than feature data for a repo
    CSV_HEADERS = ["prediction", "confidence"]

    OPEN_CSV_FILES: Dict[str, OpenCSVFile] = {}
    OPEN_CSV_FILES_LOCK: asyncio.Lock = asyncio.Lock()

    @asynccontextmanager
    async def _open_csv(self, fd=None):
        async with self.OPEN_CSV_FILES_LOCK:
            if self.config.filename not in self.OPEN_CSV_FILES:
                self.logger.debug(f"{self.config.filename} first open")
                open_file = OpenCSVFile(
                    active=1, lock=asyncio.Lock(), write_out={}
                )
                self.OPEN_CSV_FILES[self.config.filename] = open_file
                if fd is not None:
                    await self.read_csv(fd, open_file)
            else:
                self.logger.debug(f"{self.config.filename} already open")
                await self.OPEN_CSV_FILES[self.config.filename].inc()
            yield self.OPEN_CSV_FILES[self.config.filename]

    async def _empty_file_init(self):
        async with self._open_csv():
            return {}

    async def read_csv(self, fd, open_file):
        dict_reader = csv.DictReader(fd, dialect="strip")
        # Record what headers are present when the file was opened
        if not self.config.key in dict_reader.fieldnames:
            open_file.write_back_key = False
        if self.config.tagcol in dict_reader.fieldnames:
            open_file.write_back_tag = True
        # Store all the repos by their tag in write_out
        open_file.write_out = {}
        # If there is no key track row index to be used as key by tag
        index = {}
        for row in dict_reader:
            # Grab tag from row
            tag = row.get(self.config.tagcol, self.config.tag)
            if self.config.tagcol in row:
                del row[self.config.tagcol]
            index.setdefault(tag, 0)
            # Grab key from row
            key = row.get(self.config.key, str(index[tag]))
            if self.config.key in row:
                del row[self.config.key]
            else:
                index[tag] += 1
            # Repo data we are going to parse from this row (must include
            # features).
            repo_data = {}
            # Parse headers we as the CSV source added
            csv_meta = {}
            row_keys = []
            # getting all keys starting with "prediction","confidence"
            for header in self.CSV_HEADERS:
                row_keys.extend(
                    list(
                        filter(
                            lambda x: x.startswith(header + "_"), row.keys()
                        )
                    )
                )
            # pop all prediction data from row and save in csv_meta
            for header in row_keys:
                value = row.get(header, None)
                if value is not None and value != "":
                    csv_meta[header] = row[header]
                    # Remove from feature data
                    del row[header]
            # Set the features
            features = {}
            for _key, _value in row.items():
                if _value != "":
                    try:
                        features[_key] = ast.literal_eval(_value)
                    except (SyntaxError, ValueError):
                        features[_key] = _value
            if features:
                repo_data["features"] = features

            # Getting all prediction target names
            target_keys = filter(
                lambda x: x.startswith("prediction_"), csv_meta.keys()
            )
            target_keys = map(
                lambda x: x.replace("prediction_", ""), target_keys
            )

            predictions = {
                target_name: {
                    "value": str(csv_meta["prediction_" + target_name]),
                    "confidence": float(csv_meta["confidence_" + target_name]),
                }
                for target_name in target_keys
            }
            repo_data.update({"prediction": predictions})
            # If there was no data in the row, skip it
            if not repo_data and key == str(index[tag] - 1):
                continue
            # Add the repo to our internal memory representation
            open_file.write_out.setdefault(tag, {})
            open_file.write_out[tag][key] = Repo(key, data=repo_data)

    async def load_fd(self, fd):
        """
        Parses a CSV stream into Repo instances
        """
        async with self._open_csv(fd) as open_file:
            self.mem = open_file.write_out.get(self.config.tag, {})
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        """
        Dumps data into a CSV stream
        """
        async with self.OPEN_CSV_FILES_LOCK:
            open_file = self.OPEN_CSV_FILES[self.config.filename]
            open_file.write_out.setdefault(self.config.tag, {})
            open_file.write_out[self.config.tag].update(self.mem)
            # Bail if not last open source for this file
            if not (await open_file.dec()):
                return
            # Add our headers
            fieldnames = (
                [] if not open_file.write_back_key else [self.config.key]
            )
            fieldnames.append(self.config.tagcol)
            # Get all the feature names
            feature_fieldnames = set()
            prediction_fieldnames = set()
            for tag, repos in open_file.write_out.items():
                for repo in repos.values():
                    feature_fieldnames |= set(repo.data.features.keys())
                    prediction_fieldnames |= set(repo.data.prediction.keys())
            fieldnames += list(feature_fieldnames)
            fieldnames += itertools.chain(
                *list(
                    map(
                        lambda key: ("prediction_" + key, "confidence_" + key),
                        list(prediction_fieldnames),
                    )
                )
            )
            self.logger.debug(f"fieldnames: {fieldnames}")
            # Write out the file
            writer = csv.DictWriter(fd, fieldnames=fieldnames)
            writer.writeheader()
            for tag, repos in open_file.write_out.items():
                for repo in repos.values():
                    repo_data = repo.dict()
                    row = {name: "" for name in fieldnames}
                    # Always write the tag
                    row[self.config.tagcol] = tag
                    # Write the key if it existed
                    if open_file.write_back_key:
                        row[self.config.key] = repo.key
                    # Write the features
                    for key, value in repo_data.get("features", {}).items():
                        row[key] = value
                    # Write the prediction
                    if "prediction" in repo_data:
                        for key, value in repo_data["prediction"].items():
                            row["prediction_" + key] = value["value"]
                            row["confidence_" + key] = value["confidence"]
                    writer.writerow(row)
            del self.OPEN_CSV_FILES[self.config.filename]
            self.logger.debug(f"{self.config.filename} written")
        self.logger.debug("%r saved %d records", self, len(self.mem))
