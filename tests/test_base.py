import unittest
from typing import List, Tuple
import pathlib

from dffml.base import (
    BaseDataFlowFacilitatorObject,
    config,
    field,
    list_action,
    BaseDataFlowFacilitatorObjectContext,
)
from dffml.feature.feature import Feature, Features
from dffml.source.source import BaseSource
from dffml.source.csv import CSVSource
from dffml.source.json import JSONSource
from dffml.util.entrypoint import entrypoint, base_entry_point
from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import parse_unknown
from dffml.util.asynctestcase import IntegrationCLITestCase


@config
class FakeTestingConfig:
    num: float
    files: List[str]
    features: Features
    nums: Tuple[int]
    name: str = field("Name of FakeTesting")
    label: str = "unlabeled"
    readonly: bool = False
    source: BaseSource = JSONSource


@base_entry_point("dffml.test", "test")
class BaseTesting(BaseDataFlowFacilitatorObject):
    pass  # pragma: no cov


@entrypoint("fake")
class FakeTesting(BaseTesting):

    CONFIG = FakeTestingConfig


class TestAutoArgsConfig(IntegrationCLITestCase):
    def test_00_args(self):
        self.maxDiff = 99999
        self.assertEqual(
            FakeTesting.args({}),
            {
                "test": {
                    "plugin": None,
                    "config": {
                        "fake": {
                            "plugin": None,
                            "config": {
                                "num": {
                                    "plugin": Arg(type=float),
                                    "config": {},
                                },
                                "files": {
                                    "plugin": Arg(type=str, nargs="+"),
                                    "config": {},
                                },
                                "features": {
                                    "plugin": Arg(
                                        type=Feature,
                                        nargs="+",
                                        action=list_action(Features),
                                    ),
                                    "config": {},
                                },
                                "nums": {
                                    "plugin": Arg(type=int, nargs="+"),
                                    "config": {},
                                },
                                "name": {
                                    "plugin": Arg(
                                        type=str, help="Name of FakeTesting"
                                    ),
                                    "config": {},
                                },
                                "readonly": {
                                    "plugin": Arg(
                                        action="store_true", default=False,
                                    ),
                                    "config": {},
                                },
                                "label": {
                                    "plugin": Arg(
                                        type=str, default="unlabeled"
                                    ),
                                    "config": {},
                                },
                                "source": {
                                    "plugin": Arg(
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

    async def test_config_defaults(self):
        config = FakeTesting.config(
            await parse_unknown(
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
                "Year:int:1",
                "Commits:int:10",
                "--test-fake-nums",
                "100",
            )
        )
        self.assertEqual(config.num, -4.2)
        self.assertEqual(config.files, ["a", "b", "c"])
        self.assertEqual(config.name, "feedface")
        self.assertEqual(config.label, "unlabeled")
        self.assertFalse(config.readonly)
        self.assertTrue(isinstance(config.source, JSONSource))
        self.assertEqual(
            config.source.config.filename, pathlib.Path("file.json")
        )
        self.assertEqual(
            config.features,
            Features(Feature("Year", int, 1), Feature("Commits", int, 10)),
        )
        self.assertEqual(config.nums, (100,))

    async def test_config_set(self):
        config = FakeTesting.config(
            await parse_unknown(
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
                "Year:int:1",
                "Commits:int:10",
                "--test-fake-nums",
                "100",
                "42",
            )
        )
        self.assertEqual(config.num, -4.2)
        self.assertEqual(config.files, ["a", "b", "c"])
        self.assertEqual(config.name, "feedface")
        self.assertEqual(config.label, "default-label")
        self.assertTrue(config.readonly)
        self.assertTrue(isinstance(config.source, CSVSource))
        self.assertEqual(
            config.source.config.filename, pathlib.Path("file.csv")
        )
        self.assertEqual(
            config.features,
            Features(Feature("Year", int, 1), Feature("Commits", int, 10)),
        )
        self.assertEqual(config.nums, (100, 42))


class FakeTestingContext(BaseDataFlowFacilitatorObjectContext):
    """
    Fake Testing Context
    """


@config
class FakeTestingConfig2:
    name: str = field("Name of FakeTesting2")
    num: float
    features: Features = Features(
        Feature("default", int, 1), Feature("features", int, 10)
    )
    label: str = "unlabeled"


@entrypoint("fake2")
class FakeTesting2(BaseTesting):
    CONTEXT = FakeTestingContext
    CONFIG = FakeTestingConfig2


@config
class FakeTestingConfig3:
    label: str = "unlabeled"


@entrypoint("fake3")
class FakeTesting3(BaseTesting):
    CONTEXT = FakeTestingContext
    CONFIG = FakeTestingConfig3


class TestCONFIG(unittest.TestCase):
    def test_CONFIG(self):
        with self.assertRaises(TypeError):
            config = FakeTesting2()
        config = FakeTesting3()
