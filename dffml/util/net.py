import os
import stat
import shutil
import pathlib
import inspect
import functools
import contextlib
import dataclasses
import urllib.request
from typing import List, Union
from .os import chdir
from .file import validate_file_hash
from .log import LOGGER, get_download_logger


class ProtocolNotAllowedError(Exception):
    """
    Raised when a URL's protocol is not in allowed list of protocols.
    """

    def __init__(self, url, allowlist):
        super().__init__()
        self.url = url
        self.allowlist = allowlist

    def __str__(self):
        return f"Protocol of URL {self.url!r} is not in allowlist: {self.allowlist!r}"


class DirectoryNotExtractedError(Exception):
    """
    Raised when extraction of directory failed!
    """

    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path

    def __str__(self):
        return f"Failed to extract - {self.directory_path!r}"


def progressbar(percent):
    """
    Simple progressbar to show download progress.
    """
    progress = "#" * int(percent / 4)
    download_logger.debug(
        f"Downloading: [{progress.ljust(25)}] {int(percent)}%"
    )


def progressbar_no_totalsize(blocknum):
    """
    Progress bar that bounces back and forth since we don't know total size.
    """
    blank = " " * 25
    progress = blank[: blocknum % 25] + "#" + blank[(blocknum % 25) + 1 :]
    download_logger.debug(f"Downloading: [{progress}] ?%")


def progress_reporthook(blocknum, blocksize, totalsize):
    """
    Serve as a reporthook for monitoring download progress.
    """
    if totalsize < 0:
        progressbar_no_totalsize(blocknum + 6)
    else:
        percent = (
            min(
                1.0,
                0 if totalsize == 0 else (blocknum * blocksize / totalsize),
            )
            * 100
        )
        progressbar(percent)


# Default list of URL protocols allowed
DEFAULT_PROTOCOL_ALLOWLIST: List[str] = ["https://"]
download_logger = get_download_logger(LOGGER)


def validate_protocol(
    url: Union[str, urllib.request.Request],
    protocol_allowlist=DEFAULT_PROTOCOL_ALLOWLIST,
) -> str:
    """
    Check that ``url`` has a protocol defined in ``protocol_allowlist``.
    Raise
    :py:class:`ProtocolNotAllowedError <dffml.util.net.ProtocolNotAllowedError>`

    Examples
    --------

    >>> from dffml.util.net import validate_protocol, DEFAULT_PROTOCOL_ALLOWLIST
    >>>
    >>> validate_protocol("http://example.com")
    Traceback (most recent call last):
        ...
    dffml.util.net.ProtocolNotAllowedError: Protocol of URL 'http://example.com' is not in allowlist: ['https://']
    >>>
    >>> validate_protocol("https://example.com")
    'https://example.com'
    >>>
    >>> validate_protocol("sshfs://example.com", ["sshfs://"] + DEFAULT_PROTOCOL_ALLOWLIST)
    'sshfs://example.com'
    """
    allowed_protocol = False
    for protocol in protocol_allowlist:
        check_url = url
        if isinstance(check_url, urllib.request.Request):
            check_url = check_url.full_url
        if check_url.startswith(protocol):
            allowed_protocol = True
    if not allowed_protocol:
        raise ProtocolNotAllowedError(url, protocol_allowlist)
    return url


def sync_urlopen(
    url: Union[str, urllib.request.Request],
    protocol_allowlist: List[str] = DEFAULT_PROTOCOL_ALLOWLIST,
    **kwargs,
):
    """
    Check that ``url`` has a protocol defined in ``protocol_allowlist``, then
    return the result of calling :py:func:`urllib.request.urlopen` passing it
    ``url`` and any keyword arguments.
    """
    validate_protocol(url, protocol_allowlist=protocol_allowlist)
    return urllib.request.urlopen(url, **kwargs)


def sync_urlretrieve(
    url: Union[str, urllib.request.Request],
    protocol_allowlist: List[str] = DEFAULT_PROTOCOL_ALLOWLIST,
    **kwargs,
):
    """
    Check that ``url`` has a protocol defined in ``protocol_allowlist``, then
    return the result of calling :py:func:`urllib.request.urlretrieve` passing
    it ``url`` and any keyword arguments.
    """
    validate_protocol(url, protocol_allowlist=protocol_allowlist)
    return urllib.request.urlretrieve(url, **kwargs)


def sync_urlretrieve_and_validate(
    url: Union[str, urllib.request.Request],
    target_path: Union[str, pathlib.Path],
    *,
    expected_sha384_hash=None,
    protocol_allowlist: List[str] = DEFAULT_PROTOCOL_ALLOWLIST,
):
    target_path = pathlib.Path(target_path)
    if not target_path.is_file() or not validate_file_hash(
        target_path, expected_sha384_hash=expected_sha384_hash, error=False,
    ):
        if not target_path.parent.is_dir():
            target_path.parent.mkdir(parents=True)
        path, _ = sync_urlretrieve(
            url,
            filename=str(target_path),
            protocol_allowlist=protocol_allowlist,
            reporthook=progress_reporthook,
        )
        return path
    validate_file_hash(
        target_path, expected_sha384_hash=expected_sha384_hash,
    )
    return target_path.absolute()


async def cached_download(
    url: Union[str, urllib.request.Request],
    target_path: Union[str, pathlib.Path],
    expected_hash: str,
    protocol_allowlist: List[str] = DEFAULT_PROTOCOL_ALLOWLIST,
):
    """
    Download a file and verify the hash of the downloaded file. If the file
    already exists and the hash matches, do not re-download the file.

    The path to the downloaded file is prepended to the argument list of the
    wrapped function.

    You can use tools like ``curl`` to download the file, and then ``sha384sum``
    to calculate the hash value used for the ``expected_hash`` argument.

    .. code-block:: console

        $ curl -sSL 'https://github.com/intel/dffml/raw/152c2b92535fac6beec419236f8639b0d75d707d/MANIFEST.in' | sha384sum
        f7aadf5cdcf39f161a779b4fa77ec56a49630cf7680e21fb3dc6c36ce2d8c6fae0d03d5d3094a6aec4fea1561393c14c  -

    Parameters
    ----------
    url : str
        The URL to download
    target_path : str, pathlib.Path
        Path on disk to store download
    expected_hash : str
        SHA384 hash of the contents
    protocol_allowlist : list, optional
        List of strings, one of which the URL must start with. If you want to be
        able to download ``http://`` (rather than ``https://``) links, you'll
        need to override this.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> cached_manifest = asyncio.run(
    ...     cached_download(
    ...         "https://github.com/intel/dffml/raw/152c2b92535fac6beec419236f8639b0d75d707d/MANIFEST.in",
    ...         "MANIFEST.in",
    ...         "f7aadf5cdcf39f161a779b4fa77ec56a49630cf7680e21fb3dc6c36ce2d8c6fae0d03d5d3094a6aec4fea1561393c14c",
    ...     )
    ... )
    >>>
    >>> with open(cached_manifest) as manifest:
    ...     print(manifest.read().split()[:2])
    ['include', 'README.md']
    """
    return sync_urlretrieve_and_validate(
        url,
        target_path,
        expected_sha384_hash=expected_hash,
        protocol_allowlist=protocol_allowlist,
    )


async def cached_download_unpack_archive(
    url,
    file_path,
    directory_path,
    expected_hash,
    protocol_allowlist=DEFAULT_PROTOCOL_ALLOWLIST,
):
    """
    Download an archive and extract it to a directory on disk.

    Verify the hash of the downloaded file. If the hash matches the file is not
    re-downloaded.

    The path to the extracted directory is prepended to the argument list of the
    wrapped function.

    See :py:func:`cached_download <dffml.util.net.cached_download>` for
    instructions on how to calculate ``expected_hash``.

    .. warning::

        This function does not verify the integrity of the unpacked archive on
        disk. Only the downloaded file.

    Parameters
    ----------
    url : str
        The URL to download
    file_path : str, pathlib.Path
        Path on disk to store download
    directory_path : str, pathlib.Path
        Path on disk to store extracted contents of downloaded archive
    expected_hash : str
        SHA384 hash of the contents
    protocol_allowlist : list, optional
        List of strings, one of which the URL must start with. If you want to be
        able to download ``http://`` (rather than ``https://``) links, you'll
        need to override this.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import cached_download_unpack_archive
    >>>
    >>> dffml_dir = asyncio.run(
    ...     cached_download_unpack_archive(
    ...         "https://github.com/intel/dffml/archive/c4469abfe6007a50144858d485537324046ff229.tar.gz",
    ...         "dffml.tar.gz",
    ...         "dffml",
    ...         "bb9bb47c4e6e4c6b7147bb3c000bc4069d69c0c77a3e560b69f476a78e6b5084adf5467ee83cbbcc47ba5a4a0696fdfc",
    ...     )
    ... )
    >>> print(len(list(dffml_dir.rglob("**/*"))))
    495
    """

    def on_error(func, path, exc_info):
        """
        Error handler for shutil.rmtree
        """
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            pass

    directory_path = pathlib.Path(directory_path)

    async def extractor(download_path):
        try:
            shutil.unpack_archive(str(download_path), str(directory_path))
        except Exception as error:
            shutil.rmtree(directory_path, onerror=on_error)
            raise DirectoryNotExtractedError(directory_path) from error

    if not directory_path.is_dir():
        directory_path.mkdir(parents=True)
        await extractor(
            await cached_download(
                url,
                file_path,
                expected_hash,
                protocol_allowlist=protocol_allowlist,
            )
        )
    return directory_path.absolute()
