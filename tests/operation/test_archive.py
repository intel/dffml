from unittest.mock import patch, mock_open

from dffml import run
from dffml.df.types import DataFlow, Input
from dffml.util.asynctestcase import AsyncTestCase
from dffml.operation.archive import (
    make_zip_archive,
    extract_zip_archive,
    make_tar_archive,
    extract_tar_archive,
)


def create_dataflow(operation, seed):
    dataflow = DataFlow(
        operations={operation.op.name: operation},
        seed={
            Input(value=val, definition=operation.op.inputs[input_name])
            for input_name, val in seed.items()
        },
        implementations={operation.op.name: operation.imp},
    )
    return dataflow


class TestZipOperations(AsyncTestCase):
    test_file_pth = "test/path/to/zip_file.zip"
    test_dir_pth = "test/path/to/directory"

    async def test_make_zip_op(self):
        dataflow = create_dataflow(
            make_zip_archive,
            {
                "input_directory_path": self.test_dir_pth,
                "output_file_path": self.test_file_pth,
            },
        )
        m_open = mock_open()
        with patch("io.open", m_open), patch(
            "zipfile.ZipFile._write_end_record"
        ):
            async for _, _ in run(dataflow):
                m_open.assert_called_once_with(self.test_file_pth, "w+b")

    async def test_extract_zip_op(self):
        dataflow = create_dataflow(
            extract_zip_archive,
            {
                "input_file_path": self.test_file_pth,
                "output_directory_path": self.test_dir_pth,
            },
        )
        m_open = mock_open()
        with patch("io.open", m_open), patch("zipfile._EndRecData"), patch(
            "zipfile.ZipFile._RealGetContents"
        ):
            async for _, _ in run(dataflow):
                m_open.assert_called_once_with(self.test_file_pth, "rb")


class TestTarOperations(AsyncTestCase):
    test_file_pth = "test/path/to/tar_file.tar"
    test_dir_pth = "test/path/to/directory"

    async def test_make_tar_archive_op(self):
        dataflow = create_dataflow(
            make_tar_archive,
            {
                "input_directory_path": self.test_dir_pth,
                "output_file_path": self.test_file_pth,
            },
        )
        m_open = mock_open()
        with patch("tarfile.bltn_open", m_open), patch(
            "tarfile.TarFile.close"
        ):
            async for _, _ in run(dataflow):
                m_open.assert_called_once_with(self.test_file_pth, "xb")

    async def test_extract_tar_op(self):
        dataflow = create_dataflow(
            extract_tar_archive,
            {
                "input_file_path": self.test_file_pth,
                "output_directory_path": self.test_dir_pth,
            },
        )
        m_open = mock_open()
        with patch("builtins.open", m_open), patch(
            "tarfile.TarFile.extractall"
        ), patch("tarfile.TarInfo.fromtarfile", m_open):
            async for _, _ in run(dataflow):
                m_open.assert_any_call("test/path/to/tar_file.tar", "rb")
