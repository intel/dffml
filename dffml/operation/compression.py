import sys
import bz2
import gzip
import lzma
import shutil

from ..df.base import op
from ..df.types import Definition


def make_compress(extension, compression_cls):
    async def compress(
        input_file_path: str, output_file_path: str,
    ):
        f"""
        A simple function to compress a {extension} file.

        Parameters
        ----------
        input_file_path : str
            Path of the file to be compressed.
        output_file_path : str
            Path where the output should be saved (should include file name).
        """
        with open(input_file_path, "rb") as f_in:
            with compression_cls.open(output_file_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return {"output_path": output_file_path}

    return compress


def make_decompress(extension, compression_cls):
    async def decompress(input_file_path: str, output_file_path: str):
        f"""
        A simple function to decompress a {extension} file.

        Parameters
        ----------
        input_file_path : str
            Path of the file to be decompressed.
        output_file_path : str
            Path where the output should be saved (should include file name).
        """
        with compression_cls.open(input_file_path, "rb") as f_in:
            with open(output_file_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return {"output_path": output_file_path}

    return decompress


SUPPORTED_COMPRESSION_FORMATS = {"gz": gzip, "bz2": bz2, "xz": lzma}

for extension, compression_cls in SUPPORTED_COMPRESSION_FORMATS.items():
    # Create definitions for compressed/decompressed file path for this format
    compressed_file_path = Definition(
        name=f"compressed_{extension}_file_path", primitive="str"
    )
    decompressed_file_path = Definition(
        name=f"decompressed_{extension}_file_path", primitive="str"
    )
    compressed_output_file_path = Definition(
        name=f"compressed_output_{extension}_file_path", primitive="str"
    )
    decompressed_output_file_path = Definition(
        name=f"decompressed_output_{extension}_file_path", primitive="str"
    )

    compress = op(
        inputs={
            "input_file_path": decompressed_file_path,
            "output_file_path": compressed_file_path,
        },
        outputs={"output_path": compressed_output_file_path},
    )(make_compress(extension, compression_cls))
    decompress = op(
        inputs={
            "input_file_path": compressed_file_path,
            "output_file_path": decompressed_file_path,
        },
        outputs={"output_path": decompressed_output_file_path},
    )(make_decompress(extension, compression_cls))

    setattr(sys.modules[__name__], f"{extension}_compress", compress)
    setattr(sys.modules[__name__], f"{extension}_decompress", decompress)
