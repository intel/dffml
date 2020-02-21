# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
from unittest.mock import patch, mock_open
from contextlib import contextmanager
from typing import AsyncIterator

from dffml.repo import Repo
from dffml.source.source import BaseSourceContext
from dffml.source.file import FileSource, FileSourceConfig
from dffml.util.cli.arg import Arg, parse_unknown
from dffml.util.asynctestcase import AsyncTestCase


class FakeFileSourceContext(BaseSourceContext):
    async def update(self, repo: Repo):
        pass  # pragma: no cover

    async def repos(self) -> AsyncIterator[Repo]:
        yield Repo("")  # pragma: no cover

    async def repo(self, key: str):
        pass  # pragma: no cover


class FakeFileSource(FileSource):

    CONTEXT = FakeFileSourceContext

    async def load_fd(self, fd):
        self.loaded_fd = fd

    async def dump_fd(self, fd):
        self.dumped_fd = fd


@contextmanager
def yield_42():
    yield 42


class TestFileSource(AsyncTestCase):
    def test_args(self):
        self.assertEqual(
            FileSource.args({}),
            {
                "source": {
                    "arg": None,
                    "config": {
                        "file": {
                            "arg": None,
                            "config": {
                                "filename": {
                                    "arg": Arg(type=str),
                                    "config": {},
                                },
                                "readwrite": {
                                    "arg": Arg(
                                        type=bool,
                                        action="store_true",
                                        default=False,
                                    ),
                                    "config": {},
                                },
                                "allowempty": {
                                    "arg": Arg(
                                        type=bool,
                                        action="store_true",
                                        default=False,
                                    ),
                                    "config": {},
                                },
                                "tag": {
                                    "arg": Arg(type=str, default="untagged"),
                                    "config": {},
                                },
                            },
                        }
                    },
                }
            },
        )

    def test_config_readonly_default(self):
        config = FileSource.config(
            parse_unknown("--source-file-filename", "feedface")
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.tag, "untagged")
        self.assertFalse(config.readwrite)
        self.assertFalse(config.allowempty)

    def test_config_readonly_set(self):
        config = FileSource.config(
            parse_unknown(
                "--source-file-filename",
                "feedface",
                "--source-file-tag",
                "default-tag",
                "--source-file-readwrite",
                "--source-file-allowempty",
            )
        )
        self.assertEqual(config.filename, "feedface")
        self.assertEqual(config.tag, "default-tag")
        self.assertTrue(config.readwrite)
        self.assertTrue(config.allowempty)

    def config(
        self, filename, tag="untagged", readwrite=True, allowempty=True
    ):
        return FileSourceConfig(
            filename=filename,
            readwrite=readwrite,
            tag=tag,
            allowempty=allowempty,
        )

    async def test_open(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", m_open
        ):
            async with FakeFileSource(
                self.config("testfile", readwrite=False)
            ):
                m_open.assert_called_once_with("testfile", "r")

    async def test_open_gz(self):
        source = FakeFileSource("testfile.gz")
        m_open = mock_open()
        with patch("os.path.exists", return_value=True), patch(
            "gzip.open", m_open
        ):
            async with FakeFileSource(
                self.config("testfile.gz", readwrite=False)
            ):
                m_open.assert_called_once_with("testfile.gz", "rt")

    async def test_open_bz2(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=True), patch(
            "bz2.open", m_open
        ):
            async with FakeFileSource(
                self.config("testfile.bz2", readwrite=False)
            ):
                m_open.assert_called_once_with("testfile.bz2", "rt")

    async def test_open_lzma(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=True), patch(
            "lzma.open", m_open
        ):
            async with FakeFileSource(
                self.config("testfile.lzma", readwrite=False)
            ):
                m_open.assert_called_once_with("testfile.lzma", "rt")

    async def test_open_xz(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=True), patch(
            "lzma.open", m_open
        ):
            async with FakeFileSource(
                self.config("testfile.xz", readwrite=False)
            ):
                m_open.assert_called_once_with("testfile.xz", "rt")

    async def test_open_zip(self):
        source = FakeFileSource(self.config("testfile.zip", readwrite=False))
        with patch("os.path.exists", return_value=True), patch.object(
            source, "zip_opener_helper", yield_42
        ):
            async with source:
                self.assertEqual(source.loaded_fd, 42)

    async def test_open_no_file(self):
        with patch("os.path.exists", return_value=False), patch(
            "os.path.isfile", return_value=False
        ):
            async with FakeFileSource(
                self.config("testfile", readwrite=False)
            ) as source:
                self.assertTrue(isinstance(source.mem, dict))

    async def test_close(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", m_open
        ):
            async with FakeFileSource(self.config("testfile")):
                pass
            m_open.assert_called_once_with("testfile", "w+")

    async def test_close_gz(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=False), patch(
            "gzip.open", m_open
        ):
            async with FakeFileSource(self.config("testfile.gz")):
                pass
            m_open.assert_called_once_with("testfile.gz", "wt")

    async def test_close_bz2(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=False), patch(
            "bz2.open", m_open
        ):
            async with FakeFileSource(self.config("testfile.bz2")):
                pass
            m_open.assert_called_once_with("testfile.bz2", "wt")

    async def test_close_lzma(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=False), patch(
            "lzma.open", m_open
        ):
            async with FakeFileSource(self.config("testfile.lzma")):
                pass
            m_open.assert_called_once_with("testfile.lzma", "wt")

    async def test_close_xz(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=False), patch(
            "lzma.open", m_open
        ):
            async with FakeFileSource(self.config("testfile.xz")):
                pass
            m_open.assert_called_once_with("testfile.xz", "wt")

    async def test_close_zip(self):
        source = FakeFileSource(self.config("testfile.zip"))
        with patch("os.path.exists", return_value=False), patch.object(
            source, "zip_closer_helper", yield_42
        ):
            async with source:
                pass
            self.assertEqual(source.dumped_fd, 42)

    async def test_close_readonly(self):
        m_open = mock_open()
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", m_open
        ):
            async with FakeFileSource(
                self.config("testfile", readwrite=False)
            ):
                pass
            m_open.assert_not_called()
