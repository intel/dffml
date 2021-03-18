"""
Validate that CI and source and docs are in sync
"""
import re
import os
import pathlib
import unittest
import platform
import itertools
from typing import List, Optional, Union, Callable

from dffml.plugins import PACKAGE_DIRECTORY_TO_NAME


class IgnoreFile:
    """
    Checks if files should be ignored by reading ignore files such as .gitignore
    and .dockerignore and parsing their rules.

    Examples
    --------

    >>> import pathlib
    >>> from dffml import IgnoreFile
    >>>
    >>> root = pathlib.Path(".")
    >>> root.joinpath(".gitignore").write_text("subdir/**")
    >>> root.joinpath("subdir", ".gitignore").mkdir()
    >>> root.joinpath("subdir", ".gitignore").write_text("!sub2/**")
    >>>
    >>> ignorefile = IgnoreFile()
    >>> print(ignorefile("subdir/sub2/feedface"))
    False
    >>> print(ignorefile("subdir/other"))
    True
    """

    def __init__(
        self, root: pathlib.Path, ignore_files: List[str] = [".gitignore"]
    ):
        self.root = root
        self.ignore_files = ignore_files
        self.compiled_regexes = {}

    @staticmethod
    def path_to_lines(path: pathlib.Path):
        return list(
            filter(bool, path.read_text().replace("\r\n", "\n").split("\n"))
        )

    @staticmethod
    def compile_regexes(
        contents: List[str],
    ) -> List[Callable[[str], Union[None, bool, re.Match]]]:
        for line in contents:
            # Handle the case where we do not want to ignore files matching this
            # pattern
            do_not_ignore = False
            if line.startswith("!"):
                line = line[1:]
                do_not_ignore = True
            # Substitute periods for literal periods
            line = line.replace(".", r"\.")
            # Substitute * for regex version of *, which is .*
            line = line.replace("*", r".*")
            # Compile the regex
            yield do_not_ignore, re.compile(line)

    def __call__(self, filename: str) -> bool:
        # Get the absolute file path
        filepath = pathlib.Path(filename).absolute()
        # Read any ignore files and compile their regexes from the file path up
        # to the root of the repo
        for ignore_filename in self.ignore_files:
            for directory in list(filepath.parents)[
                : filepath.parents.index(self.root) + 1
            ]:
                ignore_path = directory / ignore_filename
                if (
                    directory not in self.compiled_regexes
                    and ignore_path.is_file()
                ):
                    self.compiled_regexes[directory] = list(
                        self.compile_regexes(self.path_to_lines(ignore_path))
                    )
        # Get all applicable regexes by looking through dict of compiled regexes
        # and grabbing any that are in the files parents
        directories = []
        for directory in self.compiled_regexes.keys():
            if directory.resolve() in filepath.parents:
                directories.append(directory)
        # Check if any match
        ignore = False
        for directory in directories:
            for do_not_ignore, regex in self.compiled_regexes[directory]:
                if not do_not_ignore and regex.match(
                    str(filepath.relative_to(directory)).replace(os.sep, "/")
                ):
                    ignore = True
        # Check if any are supposed to not be ignored even though they match
        # other patterns
        for directory in directories:
            for do_not_ignore, regex in self.compiled_regexes[directory]:
                if (
                    do_not_ignore
                    and ignore
                    and regex.match(
                        str(filepath.relative_to(directory)).replace(
                            os.sep, "/"
                        )
                    )
                ):
                    ignore = False
        return ignore


class TestGitIgnore(unittest.TestCase):
    def test_ignore(self):
        ignorefile = IgnoreFile(root=pathlib.Path(__file__).parents[1])

        self.assertFalse(ignorefile("setup.py"))
        self.assertFalse(ignorefile("dffml/skel/common/setup.py"))
        self.assertTrue(ignorefile("dffml/skel/model/setup.py"))
        self.assertTrue(
            ignorefile(
                "examples/shouldi/tests/downloads/cri-resource-manager-download/.gopath/pkg/mod/github.com/apache/thrift@v0.12.0/contrib/fb303/py/setup.py"
            )
        )


REPO_ROOT = pathlib.Path(__file__).parents[1]


@unittest.skipUnless(platform.system() == "Linux", "Only runs on Linux")
class TestCI(unittest.TestCase):
    maxDiff = None
    SKIP_SETUP_PY_FILES = [
        REPO_ROOT / "setup.py",
        REPO_ROOT / "dffml" / "skel" / "common" / "setup.py",
        REPO_ROOT / "build" / "lib" / "dffml" / "skel" / "common" / "setup.py",
        REPO_ROOT / "examples" / "source" / "setup.py",
        REPO_ROOT
        / "examples"
        / "tutorials"
        / "sources"
        / "file"
        / "dffml-source-ini"
        / "setup.py",
    ]

    def test_all_plugins_appear_in_dffml_plugins(self):
        """
        Make sure that any setup.py files associated with a plugin appear in
        dffml/plugins.py
        """
        ignorefile = IgnoreFile(REPO_ROOT)
        # A list of directory tupples, relative to the root of the repo, which
        # contain setup.py files. Directories who have setup.py files listed in
        # SKIP_SETUP_PY_FILES will not be in this list
        setup_py_directories = sorted(
            map(
                lambda path: path.parent.relative_to(REPO_ROOT).parts,
                filter(
                    lambda path: path not in self.SKIP_SETUP_PY_FILES,
                    itertools.filterfalse(
                        ignorefile, REPO_ROOT.rglob("setup.py")
                    ),
                ),
            )
        )
        self.assertListEqual(
            setup_py_directories, sorted(PACKAGE_DIRECTORY_TO_NAME.keys())
        )

    def test_all_plugins_being_tested(self):
        """
        Make sure that plugins are included in the test matrix and therefore
        being tested by the CI.
        """
        # We compare against PACKAGE_DIRECTORY_TO_NAME as the truth because the
        # test_all_plugins_appear_in_dffml_plugins() validates that every
        # directory that has a setup.py appears in PACKAGE_DIRECTORY_TO_NAME.
        should_be = sorted(
            list(
                map(
                    lambda directories: "/".join(directories),
                    PACKAGE_DIRECTORY_TO_NAME.keys(),
                )
            )
            + ["."]
        )
        # Load the ci testing workflow avoid requiring the yaml module as that
        # has C dependencies.
        # We read the file, split it by lines., filter by lines mentioning PyPi
        lines = (
            pathlib.Path(REPO_ROOT, ".github", "workflows", "testing.yml",)
            .read_text()
            .split("\n")
        )
        # filter by lines mentioning PyPi
        # tokens, and make a list of tuples which contain the left hand side of
        # the lines '=', split on the '/' character.
        # We skip the line which the default TWINE_PASSWORD environment
        # variable, since that's for the main package (not any of the plugins).
        plugins_tested_by_ci = []
        # Once we see plugins: we start adding the subsequent list of plugins to
        # our list of plugins tested by CI.
        start_adding_plugins = 0
        # Go over each line in the YAML file
        for line in lines:
            if line.strip() == "plugin:":
                # Start adding when we see the list of plugins
                start_adding_plugins += 1
            elif start_adding_plugins and ":" in line:
                # If we've reached the next YAML object key we're done adding to
                # the list of plugins
                break
            elif start_adding_plugins:
                # Add plugins to list of plugins being tested
                # Line is in the format of: "- plugin/path"
                plugins_tested_by_ci.append(line.strip().split()[-1])
        # Make sure there was only one list
        self.assertTrue(plugins_tested_by_ci, "No plugins found!")
        self.assertEqual(
            start_adding_plugins, 1, "More than one list of plugins found!"
        )
        # Sort them
        plugins_tested_by_ci = sorted(plugins_tested_by_ci)
        # Compare to truth
        self.assertListEqual(should_be, plugins_tested_by_ci)

    def test_all_plugins_have_pypi_tokens(self):
        """
        Make sure every plugin is listed with a PyPi API token to enable
        automatic releases.
        """
        # Load the ci testing workflow avoid requiring the yaml module as that
        # has C dependencies.
        # We read the file, split it by lines, filter by lines mentioning PyPi
        # tokens, and make a list of tuples which contain the left hand side of
        # the lines '=', split on the '/' character.
        # We skip the line which the default TWINE_PASSWORD environment
        # variable, since that's for the main package (not any of the plugins).
        # Example:
        #   model/vowpalWabbit=${{ secrets.PYPI_MODEL_VOWPALWABBIT }}
        # This line results in a list entry of: ('model', 'vowpalWabbit')
        plugins_with_pypi_tokens = sorted(
            map(
                lambda i: tuple(i.strip().split("=")[0].split("/")),
                filter(
                    lambda line: "secrets.PYPI_" in line
                    and not "TWINE_PASSWORD" in line,
                    pathlib.Path(
                        REPO_ROOT, ".github", "workflows", "testing.yml"
                    )
                    .read_text()
                    .split("\n"),
                ),
            )
        )
        # We compare list list to the list of packages dffml.plugins knows
        # about, to make sure that every package has a secret so it can be
        # auto-deployed to PyPi.
        self.assertListEqual(
            plugins_with_pypi_tokens, sorted(PACKAGE_DIRECTORY_TO_NAME.keys())
        )
