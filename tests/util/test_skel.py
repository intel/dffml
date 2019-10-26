import itertools
from pathlib import Path

from dffml.util.skel import Skel
from dffml.util.asynctestcase import AsyncTestCase


# These are the files that we're expecting to be in skel/common, update this
# list anytime the files in skel/common change
COMMON_FILES = list(
    itertools.starmap(
        Path,
        [
            (".gitignore",),
            (".coveragerc",),
            ("setup_common.py",),
            ("MANIFEST.in",),
            ("REPLACE_IMPORT_PACKAGE_NAME", "version.py"),
            ("REPLACE_IMPORT_PACKAGE_NAME", "__init__.py"),
            ("tests/__init__.py",),
        ],
    )
)


class TestSkelUtil(AsyncTestCase):

    skel = Skel()

    def test_all_common_files_accounted_for(self):
        common_files = [
            path.relative_to(self.skel.common)
            for path in self.skel.common_files()
        ]
        for check in COMMON_FILES:
            self.assertIn(check, common_files)
