"""
This file contains styles tests for checking at the end of source files.
"""
import os
import pathlib

from dffml.util.asynctestcase import IntegrationCLITestCase

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]

SKIP_FILES_FORMATS = [
    ".zip",
    ".rst",
    ".png",
    ".gz",
    ".log",
    ".pyc",
    ".coverage",
    ".eggs",
    ".swp",
    ".mnistpng",
    "docs/changelog.md",
    "docs/shouldi.md",
    "docs/swportal.rst",
    "docs/contributing/consoletest.md",
    ".pyc",
    ".git",
    ".egg-info",
    ".sh",
    ".Dockerfile",
    ".html",
    ".md",
    ".gif",
    ".in",
    ".cfg",
    ".yaml",
    ".venv",
    ".pylintrc",
    ".yml",
]

SKIP_DIRECTORIES = [
    ".cache/",
    ".idea/",
    ".vscode/",
    ".egg-info/",
    "build/",
    "dist/",
    "docs/build/",
    "venv/",
    "wheelhouse/",
    ".mypy_cache/",
    "htmlcov/",
    ".venv/",
    "html/",
    "pages/",
    "pip-wheel-metadata/",
    "doctest/",
    "docs/api/",
    "/consoletest/",
    "tests/service/logs/",
    "__pycache__",
    "git/",
    "images/",
    "dffml.egg-info",
    ".ci",
    "examples",
]


class TestML(IntegrationCLITestCase):
    def test_styles(self):
        for path in ROOT_DIR.rglob("*.*"):
            if not any(
                dirs in str(path) for dirs in SKIP_DIRECTORIES
            ) and not any(
                extension in str(path) for extension in SKIP_FILES_FORMATS
            ):
                content = pathlib.Path(path).read_text()
                if len(content):
                    self.assertEqual(content[-1], "\n", path)
