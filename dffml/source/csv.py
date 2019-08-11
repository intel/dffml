# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
"""
Loads repos from a csv file, using columns as features
"""
import csv
import ast
import asyncio
from typing import NamedTuple, Dict, List
from dataclasses import dataclass
from contextlib import asynccontextmanager

from ..repo import Repo
from .memory import MemorySource
from .file import FileSource, FileSourceConfig
from ..util.cli.arg import Arg
from ..util.entrypoint import entry_point

csv.register_dialect("strip", skipinitialspace=True)


@dataclass
class OpenCSVFile:
    write_out: Dict
    active: int
    lock: asyncio.Lock
    write_back_key: bool = True
    write_back_label: bool = False

    async def inc(self):
        async with self.lock:
            self.active += 1

    async def dec(self):
        async with self.lock:
            self.active -= 1
            return bool(self.active < 1)


CSV_SOURCE_CONFIG_DEFAULT_KEY = "src_url"
CSV_SOURCE_CONFIG_DEFAULT_LABEL = "unlabeled"
CSV_SOURCE_CONFIG_DEFAULT_LABEL_COLUMN = "label"


class CSVSourceConfig(FileSourceConfig, NamedTuple):
    filename: str
    readonly: bool = False
    key: str = CSV_SOURCE_CONFIG_DEFAULT_KEY
    label: str = CSV_SOURCE_CONFIG_DEFAULT_LABEL
    label_column: str = CSV_SOURCE_CONFIG_DEFAULT_LABEL_COLUMN


# CSVSource is a bit of a mess
@entry_point("csv")
class CSVSource(FileSource, MemorySource):
    """
    Uses a CSV file as the source of repo feature data
    """

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

    @classmethod
    def args(cls, args, *above) -> Dict[str, Arg]:
        cls.config_set(args, above, "filename", Arg())
        cls.config_set(
            args,
            above,
            "readonly",
            Arg(type=bool, action="store_true", default=False),
        )
        cls.config_set(
            args,
            above,
            "label",
            Arg(type=str, default=CSV_SOURCE_CONFIG_DEFAULT_LABEL),
        )
        cls.config_set(
            args,
            above,
            "labelcol",
            Arg(type=str, default=CSV_SOURCE_CONFIG_DEFAULT_LABEL_COLUMN),
        )
        cls.config_set(args, above, "key", Arg(type=str, default="src_url"))
        return args

    @classmethod
    def config(cls, config, *above):
        return CSVSourceConfig(
            filename=cls.config_get(config, above, "filename"),
            readonly=cls.config_get(config, above, "readonly"),
            label=cls.config_get(config, above, "label"),
            key=cls.config_get(config, above, "key"),
            label_column=cls.config_get(config, above, "labelcol"),
        )

    async def read_csv(self, fd, open_file):
        dict_reader = csv.DictReader(fd, dialect="strip")
        # Record what headers are present when the file was opened
        if not self.config.key in dict_reader.fieldnames:
            open_file.write_back_key = False
        if self.config.label_column in dict_reader.fieldnames:
            open_file.write_back_label = True
        # Store all the repos by their label in write_out
        open_file.write_out = {}
        # If there is no key track row index to be used as src_url by label
        index = {}
        for row in dict_reader:
            # Grab label from row
            label = row.get(self.config.label_column, self.config.label)
            if self.config.label_column in row:
                del row[self.config.label_column]
            index.setdefault(label, 0)
            # Grab src_url from row
            src_url = row.get(self.config.key, index[label])
            if self.config.key in row:
                del row[self.config.key]
            else:
                index[label] += 1
            # Repo data we are going to parse from this row (must include
            # features).
            repo_data = {}
            # Parse headers we as the CSV source added
            csv_meta = {}
            for header in self.CSV_HEADERS:
                value = row.get(header, None)
                if value is not None and value != "":
                    csv_meta[header] = row[header]
                    # Remove from feature data
                    del row[header]
            # Set the features
            features = {}
            for key, value in row.items():
                if value != "":
                    try:
                        features[key] = ast.literal_eval(value)
                    except (SyntaxError, ValueError):
                        features[key] = value
            if features:
                repo_data["features"] = features
            if "prediction" in csv_meta and "confidence" in csv_meta:
                repo_data.update(
                    {
                        "prediction": {
                            "value": str(csv_meta["prediction"]),
                            "confidence": float(csv_meta["confidence"]),
                        }
                    }
                )
            # If there was no data in the row, skip it
            if not repo_data and src_url == str(index[label] - 1):
                continue
            # Add the repo to our internal memory representation
            open_file.write_out.setdefault(label, {})
            open_file.write_out[label][src_url] = Repo(src_url, data=repo_data)

    async def load_fd(self, fd):
        """
        Parses a CSV stream into Repo instances
        """
        async with self._open_csv(fd) as open_file:
            self.mem = open_file.write_out.get(self.config.label, {})
        self.logger.debug("%r loaded %d records", self, len(self.mem))

    async def dump_fd(self, fd):
        """
        Dumps data into a CSV stream
        """
        async with self.OPEN_CSV_FILES_LOCK:
            open_file = self.OPEN_CSV_FILES[self.config.filename]
            open_file.write_out.setdefault(self.config.label, {})
            open_file.write_out[self.config.label].update(self.mem)
            # Bail if not last open source for this file
            if not (await open_file.dec()):
                return
            # Add our headers
            fieldnames = (
                [] if not open_file.write_back_key else [self.config.key]
            )
            fieldnames.append(self.config.label_column)
            # Get all the feature names
            feature_fieldnames = set()
            for label, repos in open_file.write_out.items():
                for repo in repos.values():
                    feature_fieldnames |= set(repo.data.features.keys())
            fieldnames += list(feature_fieldnames)
            fieldnames += self.CSV_HEADERS
            self.logger.debug(f"fieldnames: {fieldnames}")
            # Write out the file
            writer = csv.DictWriter(fd, fieldnames=fieldnames)
            writer.writeheader()
            for label, repos in open_file.write_out.items():
                for repo in repos.values():
                    repo_data = repo.dict()
                    row = {name: "" for name in fieldnames}
                    # Always write the label
                    row[self.config.label_column] = label
                    # Write the key if it existed
                    if open_file.write_back_key:
                        row[self.config.key] = repo.src_url
                    # Write the features
                    for key, value in repo_data.get("features", {}).items():
                        row[key] = value
                    # Write the prediction
                    if "prediction" in repo_data:
                        row["prediction"] = repo_data["prediction"]["value"]
                        row["confidence"] = repo_data["prediction"][
                            "confidence"
                        ]
                    writer.writerow(row)
            del self.OPEN_CSV_FILES[self.config.filename]
            self.logger.debug(f"{self.config.filename} written")
        self.logger.debug("%r saved %d records", self, len(self.mem))
