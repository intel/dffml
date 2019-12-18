import unittest
from typing import List

from dffml.base import (
    BaseDataFlowFacilitatorObject,
    config,
    field,
    list_action,
)
from dffml.feature.feature import DefFeature, Feature, Features
from dffml.source.source import BaseSource
from dffml.source.csv import CSVSource
from dffml.source.json import JSONSource
from dffml.util.entrypoint import entry_point, base_entry_point
from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import parse_unknown


@config
class FakeTestingConfig:
    num: float
    files: List[str]
    features: Features
    name: str = field("Name of FakeTesting")
    label: str = "unlabeled"
    readonly: bool = False
    source: BaseSource = JSONSource


@base_entry_point("dffml.test", "test")
class BaseTesting(BaseDataFlowFacilitatorObject):
    pass  # pragma: no cov


@entry_point("fake")
class FakeTesting(BaseTesting):

    CONFIG = FakeTestingConfig


class TestAutoArgsConfig(unittest.TestCase):
    def test_00_args(self):
        self.maxDiff = 99999
        self.assertEqual(
            FakeTesting.args({}),
            {
                "test": {
                    "arg": None,
                    "config": {
                        "fake": {
                            "arg": None,
                            "config": {
                                "num": {"arg": Arg(type=float), "config": {},},
                                "files": {
                                    "arg": Arg(type=str, nargs="+"),
                                    "config": {},
                                },
                                "features": {
                                    "arg": Arg(
                                        type=Feature.load,
                                        nargs="+",
                                        action=list_action(Features),
                                    ),
                                    "config": {},
                                },
                                "name": {
                                    "arg": Arg(
                                        type=str, help="Name of FakeTesting"
                                    ),
                                    "config": {},
                                },
                                "readonly": {
                                    "arg": Arg(
                                        type=bool,
                                        action="store_true",
                                        default=False,
                                    ),
                                    "config": {},
                                },
                                "label": {
                                    "arg": Arg(type=str, default="unlabeled"),
                                    "config": {},
                                },
                                "source": {
                                    "arg": Arg(
                                        type=BaseSource.load,
                                        default=JSONSource,
                                    ),
                                    "config": {},
                                },
                            },
                        }
                    },
                }
            },
        )

    def test_config_defaults(self):
        config = FakeTesting.config(
            parse_unknown(
                "--test-fake-name",
                "feedface",
                "--test-num",
                "-4.2",
                "--test-files",
                "a",
                "b",
                "c",
                "--test-source-filename",
                "file.json",
                "--test-features",
                "def:Year:int:1",
                "def:Commits:int:10",
            )
        )
        self.assertEqual(config.num, -4.2)
        self.assertEqual(config.files, ["a", "b", "c"])
        self.assertEqual(config.name, "feedface")
        self.assertEqual(config.label, "unlabeled")
        self.assertFalse(config.readonly)
        self.assertTrue(isinstance(config.source, JSONSource))
        self.assertEqual(config.source.config.filename, "file.json")
        self.assertEqual(
            config.features,
            Features(
                DefFeature("Year", int, 1), DefFeature("Commits", int, 10)
            ),
        )

    def test_config_set(self):
        config = FakeTesting.config(
            parse_unknown(
                "--test-fake-name",
                "feedface",
                "--test-num",
                "-4.2",
                "--test-fake-label",
                "default-label",
                "--test-fake-readonly",
                "--test-files",
                "a",
                "b",
                "c",
                "--test-fake-source",
                "csv",
                "--test-source-filename",
                "file.csv",
                "--test-features",
                "def:Year:int:1",
                "def:Commits:int:10",
            )
        )
        self.assertEqual(config.num, -4.2)
        self.assertEqual(config.files, ["a", "b", "c"])
        self.assertEqual(config.name, "feedface")
        self.assertEqual(config.label, "default-label")
        self.assertTrue(config.readonly)
        self.assertTrue(isinstance(config.source, CSVSource))
        self.assertEqual(config.source.config.filename, "file.csv")
        self.assertEqual(
            config.features,
            Features(
                DefFeature("Year", int, 1), DefFeature("Commits", int, 10)
            ),
        )
