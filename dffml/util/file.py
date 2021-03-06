import hashlib
import pathlib
from typing import Union


class NoHashToUseForValidationSuppliedError(Exception):
    """
    A hash to validate file contents against was not supplied.
    """


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


def validate_file_hash(
    filepath: Union[str, pathlib.Path],
    *,
    expected_sha384_hash: str = None,
    error: bool = True,
    chunk_size: int = 8192,
):
    r"""
    Read the contents of a file, hash the contents, and compare that hash to the
    one given.

    Examples
    --------

    Write out ``file.txt`` with the contents of b"Hello World\n". Then check it
    to see if the SHA 384 hash of the contents matches the SHA 384 hash for
    b"Hello FeedFace\n".

    >>> import pathlib
    >>> import hashlib
    >>> from dffml import validate_file_hash
    >>>
    >>> correct_contents = b"Hello FeedFace\n"
    >>> expected_sha384_hash = hashlib.sha384(correct_contents).hexdigest()
    >>>
    >>> original_path = pathlib.Path("file.txt")
    >>> original_path.write_text("Hello World\n")
    12
    >>>
    >>> validate_file_hash(
    ...     original_path,
    ...     expected_sha384_hash=expected_sha384_hash,
    ... )
    Traceback (most recent call last):
        ...
    dffml.util.file.HashValidationError: file.txt hash was acbfd470c22c0d95a1d10a087dc31988b9f7bfeb13be70b876a73558be664e5858d11f9459923e6e5fd838cb5708b969, should be 00d7bdbf0b24d37463bd9d2107926c3fa870537c009cd64dde72c3578160d9e04f63bf487631a2e2e7610f9654cf0f78
    >>>
    >>> validate_file_hash(
    ...     original_path,
    ...     expected_sha384_hash=expected_sha384_hash,
    ...     error=False,
    ... )
    False
    >>>
    >>> # Write the correct contents to the file so validation passes
    >>> original_path.write_bytes(correct_contents)
    15
    >>> validate_file_hash(
    ...     original_path,
    ...     expected_sha384_hash=expected_sha384_hash,
    ... )
    True
    """
    filepath = pathlib.Path(filepath)
    if expected_sha384_hash is None:
        raise NoHashToUseForValidationSuppliedError(filepath)
    filehash = hashlib.sha384()
    with open(filepath, "rb") as fileobj:
        bytes_read = fileobj.read(chunk_size)
        filehash.update(bytes_read)
        while len(bytes_read) == chunk_size:
            bytes_read = fileobj.read(chunk_size)
            filehash.update(bytes_read)
    filehash = filehash.hexdigest()
    if filehash != expected_sha384_hash:
        if error:
            raise HashValidationError(
                str(filepath), filehash, expected_sha384_hash
            )
        return False
    return True
