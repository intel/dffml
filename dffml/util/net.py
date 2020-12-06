import shutil
import hashlib
import pathlib
import functools
import urllib.request
from typing import List

from .os import chdir


class HashValidationError(Exception):
    """
    Raised when hash of file is not what was expected
    """

    def __init__(self, path, value, expected):
        super().__init__()
        self.path = path
        self.value = value
        self.expected = expected

    def __str__(self):
        return f"{self.path} hash was {self.value}, should be {self.expected}"


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


# Default list of URL protocols allowed
DEFAULT_PROTOCOL_ALLOWLIST: List[str] = ["https://"]


def sync_urlopen(url, protocol_allowlist=DEFAULT_PROTOCOL_ALLOWLIST):
    """
    Check that ``url`` has a protocol defined in ``protocol_allowlist``, then
    return the result of calling :py:func:`urllib.request.urlopen` passing it
    ``url``.
    """
    allowed_protocol = False
    for protocol in protocol_allowlist:
        if url.startswith(protocol):
            allowed_protocol = True
    if not allowed_protocol:
        raise ProtocolNotAllowedError(url, protocol_allowlist)

    return urllib.request.urlopen(url)


def cached_download(
    url,
    target_path,
    expected_hash,
    protocol_allowlist=DEFAULT_PROTOCOL_ALLOWLIST,
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
    >>> from dffml import cached_download
    >>>
    >>> @cached_download(
    ...     "https://github.com/intel/dffml/raw/152c2b92535fac6beec419236f8639b0d75d707d/MANIFEST.in",
    ...     "MANIFEST.in",
    ...     "f7aadf5cdcf39f161a779b4fa77ec56a49630cf7680e21fb3dc6c36ce2d8c6fae0d03d5d3094a6aec4fea1561393c14c",
    ... )
    ... async def first_line_in_manifest_152c2b(manifest):
    ...     return manifest.read_text().split()[:2]
    >>>
    >>> asyncio.run(first_line_in_manifest_152c2b())
    ['include', 'README.md']
    """
    target_path = pathlib.Path(target_path)

    def validate_hash(error: bool = True):
        filehash = hashlib.sha384(target_path.read_bytes()).hexdigest()
        if filehash != expected_hash:
            if error:
                raise HashValidationError(
                    str(target_path), filehash, expected_hash
                )
            return False
        return True

    def mkwrapper(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwds):
            args = list(args) + [target_path]
            if not target_path.is_file() or not validate_hash(error=False):
                # TODO(p5) Blocking request in coroutine
                with sync_urlopen(
                    url, protocol_allowlist=protocol_allowlist
                ) as resp:
                    target_path.write_bytes(resp.read())
            validate_hash()
            return await func(*args, **kwds)

        return wrapper

    return mkwrapper


def cached_download_unpack_archive(
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
    >>> @cached_download_unpack_archive(
    ...     "https://github.com/intel/dffml/archive/c4469abfe6007a50144858d485537324046ff229.tar.gz",
    ...     "dffml.tar.gz",
    ...     "dffml",
    ...     "bb9bb47c4e6e4c6b7147bb3c000bc4069d69c0c77a3e560b69f476a78e6b5084adf5467ee83cbbcc47ba5a4a0696fdfc",
    ... )
    ... async def files_in_dffml_commit_c4469a(dffml_dir):
    ...     return len(list(dffml_dir.rglob("**/*")))
    >>>
    >>> asyncio.run(files_in_dffml_commit_c4469a())
    124
    """
    directory_path = pathlib.Path(directory_path)

    async def extractor(download_path):
        download_path = download_path.absolute()
        with chdir(directory_path):
            shutil.unpack_archive(str(download_path), ".")

    extract = cached_download(
        url, file_path, expected_hash, protocol_allowlist=protocol_allowlist
    )(extractor)

    def mkwrapper(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwds):
            if not directory_path.is_dir():
                directory_path.mkdir(parents=True)
                await extract()
            return await func(*(list(args) + [directory_path]), **kwds)

        return wrapper

    return mkwrapper
