# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import io
import atexit
import shutil
import random
import inspect
import asyncio
import logging
import tempfile
import unittest
import collections
from unittest.mock import patch, mock_open, Mock
from functools import wraps
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, AsyncIterator

from dffml.repo import Repo
from dffml.source import Sources, FileSource
from dffml.util.asynctestcase import AsyncTestCase

class FakeFileSource(FileSource):

    async def update(self, repo: Repo):
        pass # pragma: no cover

    async def repos(self) -> AsyncIterator[Repo]:
        yield Repo('') # pragma: no cover

    async def repo(self, src_url: str):
        pass # pragma: no cover

    async def load_fd(self, fd):
        pass # pragma: no cover

    async def dump_fd(self, fd):
        pass # pragma: no cover

class MockZipFile:
    def __init__(self, name):
        self.name = name
        self.files = [Mock(filename='foo.csv'), Mock(filename='bar.csv')]

    def __iter__(self):
        return iter(self.files)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def infolist(self):
        return self.files

class TestFileSource(AsyncTestCase):

    def test_readonly(self) -> bool:
        self.assertTrue(FakeFileSource('testfile:ro').readonly)
        self.assertFalse(FakeFileSource('testfile').readonly)

    def test_filename(self) -> bool:
        self.assertEqual(FakeFileSource('testfile').filename,
                         'testfile')

    def test_filename_readonly(self) -> bool:
        self.assertEqual(FakeFileSource('testfile:ro').filename,
                         'testfile')

    def test_repr(self):
        self.assertEqual(repr(FakeFileSource('testfile')),
                         'FakeFileSource(\'testfile\')')

    async def test_open(self):
        source = FakeFileSource('testfile')
        m_open = mock_open()
        with patch('os.path.exists', return_value=True), \
                patch('builtins.open', m_open):
            await source.open()
            m_open.assert_called_once_with('testfile', 'r')

    async def test_open_gz(self):
        source = FakeFileSource('testfile.gz')
        m_open = mock_open()
        with patch('os.path.exists', return_value=True), \
                patch('gzip.open', m_open):
            await source.open()
            m_open.assert_called_once_with('testfile.gz', 'rt')

    async def test_open_bz2(self):
        source = FakeFileSource('testfile.bz2')
        m_open = mock_open()
        with patch('os.path.exists', return_value=True), \
                patch('bz2.open', m_open):
            await source.open()
            m_open.assert_called_once_with('testfile.bz2', 'rt')

    async def test_open_lzma(self):
        source = FakeFileSource('testfile.lzma')
        m_open = mock_open()
        with patch('os.path.exists', return_value=True), \
                patch('lzma.open', m_open):
            await source.open()
            m_open.assert_called_once_with('testfile.lzma', 'rt')

    async def test_open_xz(self):
        source = FakeFileSource('testfile.xz')
        m_open = mock_open()
        with patch('os.path.exists', return_value=True), \
                patch('lzma.open', m_open):
            await source.open()
            m_open.assert_called_once_with('testfile.xz', 'rt')

    async def test_open_zip(self):
        source = MockZipFile('testfile.zip')
        m_open = mock_open()
        source.open = m_open
        with patch('os.path.exists', return_value=True), \
                patch('zipfile.ZipFile',m_open):
            source.open()

    async def test_open_no_file(self):
        source = FakeFileSource('testfile')
        with patch('os.path.isfile', return_value=False):
            await source.open()
            self.assertTrue(isinstance(source.mem, dict))

    async def test_close(self):
        source = FakeFileSource('testfile')
        m_open = mock_open()
        with patch('builtins.open', m_open):
            await source.close()
            m_open.assert_called_once_with('testfile', 'w')

    async def test_close_gz(self):
        source = FakeFileSource('testfile.gz')
        m_open = mock_open()
        with patch('gzip.open', m_open):
            await source.close()
            m_open.assert_called_once_with('testfile.gz', 'wt')

    async def test_close_bz2(self):
        source = FakeFileSource('testfile.bz2')
        m_open = mock_open()
        with patch('bz2.open', m_open):
            await source.close()
            m_open.assert_called_once_with('testfile.bz2', 'wt')

    async def test_close_lzma(self):
        source = FakeFileSource('testfile.lzma')
        m_open = mock_open()
        with patch('lzma.open', m_open):
            await source.close()
            m_open.assert_called_once_with('testfile.lzma', 'wt')

    async def test_close_xz(self):
        source = FakeFileSource('testfile.xz')
        m_open = mock_open()
        with patch('lzma.open', m_open):
            await source.close()
            m_open.assert_called_once_with('testfile.xz', 'wt')

    async def test_close_zip(self):
        source = MockZipFile('testfile.zip')
        m_open = mock_open()
        source.close = m_open
        with patch('os.path.exists', return_value=True), \
                patch('zipfile.ZipFile',m_open):
            source.close()
    
    async def test_close_readonly(self):
        source = FakeFileSource('testfile:ro')
        m_open = mock_open()
        with patch('builtins.open', m_open):
            await source.close()
            m_open.assert_not_called()
