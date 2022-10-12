import tarfile
import zipfile
import pathlib


from ..df.base import op
from ..df.types import Definition


# definitions
DIRECTORY = Definition(name="directory", primitive="str")
ZIP_FILE = Definition(name="zip_file", primitive="str")
TAR_FILE = Definition(name="tar_file", primitive="str")
OUTPUT_ZIPFILE_PATH = Definition(name="output_zipfile_path", primitive="str")
OUTPUT_TARFILE_PATH = Definition(name="output_tarfile_path", primitive="str")
OUTPUT_DIRECTORY_PATH = Definition(
    name="output_directory_path", primitive="str"
)


def recursive_add_to_archive(archive_handle, path, archive_path):
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    if path.is_file():
        archive_handle(path, archive_path)
    elif path.is_dir():
        if archive_path:
            archive_handle(path, archive_path)
        path_names = [pth.name for pth in path.iterdir()]
        for name in sorted(path_names):
            name = pathlib.Path(name)
            recursive_add_to_archive(
                archive_handle, path / name, archive_path / name
            )


@op(
    inputs={"input_directory_path": DIRECTORY, "output_file_path": ZIP_FILE},
    outputs={"output_path": OUTPUT_ZIPFILE_PATH},
)
async def make_zip_archive(
    input_directory_path: str, output_file_path: str,
) -> dict:
    """
    Creates zip file of a directory.

    Parameters
    ----------
    input_directory_path : str
        Path to directory to be archived
    output_file_path : str
        Path where the output archive should be saved (should include file name)

    Returns
    -------
    dict
        Path to the output zip file
    """
    with zipfile.ZipFile(output_file_path, "w") as zip:
        recursive_add_to_archive(zip.write, input_directory_path, "")
    return {"output_path": output_file_path}


@op(
    inputs={"input_file_path": ZIP_FILE, "output_directory_path": DIRECTORY},
    outputs={"output_path": OUTPUT_DIRECTORY_PATH},
)
async def extract_zip_archive(
    input_file_path: str, output_directory_path: str,
) -> dict:
    """
    Extracts a given zip file.

    Parameters
    ----------
    input_file_path : str
        Path to the zip file
    output_directory_path : str
        Path where all the files should be extracted

    Returns
    -------
    dict
        Path to the directory where the archive has been extracted
    """
    with zipfile.ZipFile(input_file_path, "r") as zip:
        zip.extractall(output_directory_path)
    return {"output_path": output_directory_path}


@op(
    inputs={"input_directory_path": DIRECTORY, "output_file_path": TAR_FILE},
    outputs={"output_path": OUTPUT_TARFILE_PATH},
)
async def make_tar_archive(
    input_directory_path: str, output_file_path: str,
) -> dict:
    """
    Creates tar file of a directory.

    Parameters
    ----------
    input_directory_path : str
        Path to directory to be archived as a tarfile.
    output_file_path : str
        Path where the output archive should be saved (should include file name)

    Returns
    -------
    dict
        Path to the created tar file.
    """
    with tarfile.open(output_file_path, mode="x") as tar:
        recursive_add_to_archive(tar.add, input_directory_path, "")
    return {"output_path": output_file_path}


@op(
    inputs={"input_file_path": TAR_FILE, "output_directory_path": DIRECTORY},
    outputs={"output_path": OUTPUT_DIRECTORY_PATH},
)
async def extract_tar_archive(
    input_file_path: str, output_directory_path: str,
) -> dict:
    """
    Extracts a given tar file.

    Parameters
    ----------
    input_file_path : str
        Path to the tar file
    output_directory_path : str
        Path where all the files should be extracted

    Returns
    -------
    dict
        Path to the directory where the archive has been extracted
    """
    with tarfile.open(input_file_path, "r") as tar:
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, output_directory_path)
    return {"output_path": output_directory_path}
