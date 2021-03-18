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


# Default list of URL protocols allowed
DEFAULT_PROTOCOL_ALLOWLIST: List[str] = ["https://"]
download_logger = get_download_logger(LOGGER)


def progressbar(cur, total=100):
    """
    Simple progressbar to show download progress.
    """
    percent = cur / total
    progress = "#" * int(cur / 2)

    download_logger.debug(
        f"\rDownloading...: [{progress.ljust(50)}] {percent:.2%}\r"
    )


def progress_reporthook(blocknum, blocksize, totalsize):
    """
    Serve as a reporthook for monitoring download progress.
    """

    percent = (
        min(1.0, 0 if totalsize == 0 else (blocknum * blocksize / totalsize))
        * 100
    )
    progressbar(percent)


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
        sync_urlretrieve(
            url,
            filename=str(target_path),
            protocol_allowlist=protocol_allowlist,
            reporthook=progress_reporthook,
        )
    validate_file_hash(
        target_path, expected_sha384_hash=expected_sha384_hash,
    )


@dataclasses.dataclass
class CachedDownloadWrapper:
    url: Union[str, urllib.request.Request]
    target_path: Union[str, pathlib.Path]
    expected_hash: str
    protocol_allowlist: List[str] = dataclasses.field(
        default_factory=lambda: DEFAULT_PROTOCOL_ALLOWLIST
    )

    def __post_init__(self):
        self.target_path = pathlib.Path(self.target_path)

    def __call__(self, func):
        if inspect.isasyncgenfunction(func) and hasattr(func, "__aenter__"):

            @contextlib.asynccontextmanager
            async def wrapped(*args, **kwargs):
                async with func(
                    *self.add_target_to_args_and_validate(args), **kwargs,
                ) as result:
                    yield result

        elif inspect.isasyncgenfunction(func):

            async def wrapped(*args, **kwargs):
                async for result in func(
                    *self.add_target_to_args_and_validate(args), **kwargs,
                ):
                    yield result

        elif inspect.iscoroutinefunction(func):

            async def wrapped(*args, **kwargs):
                return await func(
                    *self.add_target_to_args_and_validate(args), **kwargs,
                )

        elif inspect.isgeneratorfunction(func) and hasattr(func, "__enter__"):

            @contextlib.contextmanager
            def wrapped(*args, **kwargs):
                with func(
                    *self.add_target_to_args_and_validate(args), **kwargs,
                ) as result:
                    yield result

        elif inspect.isgeneratorfunction(func):

            def wrapped(*args, **kwargs):
                yield from func(
                    *self.add_target_to_args_and_validate(args), **kwargs,
                )

        else:

            def wrapped(*args, **kwargs):
                return func(
                    *self.add_target_to_args_and_validate(args), **kwargs
                )

        # Wrap with functools
        wrapped = functools.wraps(func)(wrapped)

        return wrapped

    def __enter__(self):
        self.add_target_to_args_and_validate([])
        return self.target_path

    def __exit__(self, _exc_type, _exc_value, _traceback):
        pass

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        pass

    def add_target_to_args_and_validate(self, args):
        sync_urlretrieve_and_validate(
            self.url,
            self.target_path,
            expected_sha384_hash=self.expected_hash,
            protocol_allowlist=self.protocol_allowlist,
        )
        return list(args) + [self.target_path]


def cached_download(
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
    >>> import contextlib
    >>> from dffml import cached_download
    >>>
    >>> cached_manifest = cached_download(
    ...     "https://github.com/intel/dffml/raw/152c2b92535fac6beec419236f8639b0d75d707d/MANIFEST.in",
    ...     "MANIFEST.in",
    ...     "f7aadf5cdcf39f161a779b4fa77ec56a49630cf7680e21fb3dc6c36ce2d8c6fae0d03d5d3094a6aec4fea1561393c14c",
    ... )
    >>>
    >>> @cached_manifest
    ... async def first_line_in_manifest_152c2b(manifest):
    ...     return manifest.read_text().split()[:2]
    >>>
    >>> asyncio.run(first_line_in_manifest_152c2b())
    ['include', 'README.md']
    >>>
    >>> @cached_manifest
    ... def first_line_in_manifest_152c2b(manifest):
    ...     return manifest.read_text().split()[:2]
    >>>
    >>> first_line_in_manifest_152c2b()
    ['include', 'README.md']
    >>>
    >>> @cached_manifest
    ... def first_line_in_manifest_152c2b(manifest):
    ...     yield manifest.read_text().split()[:2]
    >>>
    >>> for contents in first_line_in_manifest_152c2b():
    ...     print(contents)
    ['include', 'README.md']
    >>>
    >>> @cached_manifest
    ... async def first_line_in_manifest_152c2b(manifest):
    ...     yield manifest.read_text().split()[:2]
    >>>
    >>> async def main():
    ...     async for contents in first_line_in_manifest_152c2b():
    ...         print(contents)
    >>>
    >>> asyncio.run(main())
    ['include', 'README.md']
    >>>
    >>> @cached_manifest
    ... @contextlib.contextmanager
    ... def first_line_in_manifest_152c2b(manifest):
    ...     yield manifest.read_text().split()[:2]
    >>>
    >>> with first_line_in_manifest_152c2b() as contents:
    ...     print(contents)
    ['include', 'README.md']
    >>>
    >>> @cached_manifest
    ... @contextlib.asynccontextmanager
    ... async def first_line_in_manifest_152c2b(manifest):
    ...     yield manifest.read_text().split()[:2]
    >>>
    >>> async def main():
    ...     async with first_line_in_manifest_152c2b() as contents:
    ...         print(contents)
    >>>
    >>> asyncio.run(main())
    ['include', 'README.md']
    >>>
    ... with cached_manifest as manifest_path:
    ...     print(manifest_path.read_text().split()[:2])
    ['include', 'README.md']
    >>>
    >>> async def main():
    ...     async with cached_manifest as manifest_path:
    ...         print(manifest_path.read_text().split()[:2])
    >>>
    >>> asyncio.run(main())
    ['include', 'README.md']
    """
    return CachedDownloadWrapper(
        url, target_path, expected_hash, protocol_allowlist=protocol_allowlist,
    )


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
        download_path = download_path.absolute()
        with chdir(directory_path):
            try:
                shutil.unpack_archive(str(download_path), ".")
            except Exception as error:
                shutil.rmtree(directory_path, onerror=on_error)
                raise DirectoryNotExtractedError(directory_path) from error

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
