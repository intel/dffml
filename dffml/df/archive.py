import uuid
import pathlib
import zipfile
import tarfile
import mimetypes

from typing import Dict, Tuple, Any
from .types import DataFlow, Input, InputFlow, Definition, Operation
from ..operation.archive import (
    make_tar_archive,
    make_zip_archive,
    extract_tar_archive,
    extract_zip_archive,
)
from ..operation.compression import (
    gz_compress,
    gz_decompress,
    bz2_compress,
    bz2_decompress,
    xz_compress,
    xz_decompress,
)


def get_key_substr(string: str, dict: dict) -> Any:
    """ 
    A function to find dictionary items whose key matches a substring.
    """
    return [value for key, value in dict.items() if string in key.lower()][0]


def get_archive_type(file_path: str) -> Tuple[str]:
    """
    A function to get archive type if the file exists.
    """
    archive_type, compression_type = None, None
    if zipfile.is_zipfile(file_path):
        archive_type = "zip"
    if tarfile.is_tarfile(file_path):
        archive_type = "tar"
        compression_type = mimetypes.guess_type(file_path)[1]
    return archive_type, compression_type


def get_archive_path_info(path: str) -> Tuple[str]:
    """
    A function to find type of archive from the given path
    if the file does not exists.
    """
    archive_type, compression_type = None, None
    file_type, compression_type = mimetypes.guess_type(path)
    file_subtype = file_type.split("/")[-1] if file_type is not None else None
    if file_subtype == "zip":
        archive_type = "zip"
    if file_subtype == "x-tar":
        archive_type = "tar"
    return archive_type, compression_type


def get_operations(
    archive_action: str, archive_type: str, compression_type: str
) -> Tuple[Operation]:
    """
    A function to fetch relevant operations based on type of archive
    and compression if any.
    """
    operations = {
        "archive_ops": {
            "zip": {
                "extract": extract_zip_archive,
                "archive": make_zip_archive,
            },
            "tar": {
                "extract": extract_tar_archive,
                "archive": make_tar_archive,
            },
        },
        "compression_ops": {
            "gzip": {"compress": gz_compress, "decompress": gz_decompress},
            "xz": {"compress": xz_compress, "decompress": xz_decompress},
            "bzip2": {"compress": bz2_compress, "decompress": bz2_decompress,},
        },
    }
    archive_op = operations["archive_ops"][archive_type][archive_action]
    compression_op = None
    if compression_type is not None:
        compression_action = (
            "compress" if archive_action == "archive" else "decompress"
        )
        compression_op = operations["compression_ops"][compression_type][
            compression_action
        ]
    return archive_op, compression_op


def deduce_archive_action(seed: Dict) -> Tuple[str]:
    """
    A function to deduce archive action as 'extract' or 'archive' 
    based on the seed and find type and compression of the archive.
    """
    input_path, output_path = seed["input_path"], seed["output_path"]
    input_exists, input_is_file, input_is_dir = (
        input_path.exists(),
        input_path.is_file(),
        input_path.is_dir(),
    )
    output_exists, output_is_file, output_is_dir = (
        output_path.exists(),
        output_path.is_file(),
        output_path.is_dir(),
    )
    if all([input_exists, output_exists, output_is_dir, input_is_file]):
        action = "extract"
        archive_type, compression_type = get_archive_type(input_path)
    elif all([input_exists, output_exists, input_is_dir, output_is_file]):
        action = "archive"
        archive_type, compression_type = get_archive_type(output_path)
    elif all([input_exists, not output_exists, input_is_dir]):
        # Triggered on first time use
        action = "archive"
        archive_type, compression_type = get_archive_path_info(output_path)
    return action, archive_type, compression_type


def create_chained_archive_dataflow(
    action, first_op, second_op, seed, temp_dir
) -> DataFlow:
    """
    A function to create chained dataflows for archive extraction/creation. 
    """
    second_op_output_typ = "directory" if action == "extract" else "file"
    dataflow = DataFlow(
        operations={first_op.op.name: first_op, second_op.op.name: second_op,},
        seed={
            Input(
                value=seed["input_path"],
                definition=get_key_substr("input", first_op.op.inputs),
            ),
            Input(
                value=temp_dir / f"{str(uuid.uuid4())}.tar",
                definition=get_key_substr("output", first_op.op.inputs),
            ),
            Input(
                value=seed["output_path"],
                definition=get_key_substr("output", second_op.op.inputs),
                origin="seed.final_output",
            ),
        },
    )
    dataflow.flow.update(
        {
            second_op.op.name: InputFlow(
                inputs={
                    "input_file_path": [
                        {first_op.op.name: f"output_file_path"}
                    ],
                    f"output_{second_op_output_typ}_path": [
                        "seed.final_output"
                    ],
                }
            )
        }
    )
    dataflow.update()
    return dataflow


def create_archive_dataflow(seed: set) -> DataFlow:
    """
    A function to create appropriate dataflow to extract/create an archive
    if it is supported.
    """
    seed = {input_.origin: pathlib.Path(input_.value) for input_ in seed}
    action, archive_type, compression_type = deduce_archive_action(seed)
    archive_op, compression_op = get_operations(
        action, archive_type, compression_type
    )
    if compression_op is None:
        dataflow = DataFlow(
            operations={archive_op.op.name: archive_op},
            seed={
                Input(
                    value=seed["input_path"],
                    definition=get_key_substr("input", archive_op.op.inputs),
                ),
                Input(
                    value=seed["output_path"],
                    definition=get_key_substr("output", archive_op.op.inputs),
                ),
            },
        )
    else:
        first_op = compression_op if action == "extract" else archive_op
        second_op = (
            compression_op if first_op is not compression_op else archive_op
        )
        dataflow = create_chained_archive_dataflow(
            action, first_op, second_op, seed, seed["input_path"].parent
        )
    return dataflow
