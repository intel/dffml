import io
import gzip
import urllib
import shutil
import hashlib
import pathlib
import tempfile
import functools

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


def cached_download(url, filename, expected_hash):
    target_path = pathlib.Path(__file__).parent / filename

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
            args = list(args) + [str(target_path)]
            if not target_path.is_file() or not validate_hash(error=False):
                # async with aiohttp.ClientSession(trust_env=True) as session:
                #     async with session.get(url) as response:
                async with urllib.request.urlopen(url) as response:
                    if unzip:
                        async with gzip.GzipFile(
                            fileobj=io.BytesIO(response.read())
                        ) as gzip_file:
                            target_path.write_bytes(await gzip_file.read())
                    else:
                        target_path.write_bytes(await response.read())
            validate_hash()
            return await func(*args, **kwds)

        return wrapper

    return mkwrapper