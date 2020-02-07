import hashlib
import pathlib
import functools
import urllib.request
from typing import List


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


DEFAULT_PROTOCOL_ALLOWLIST: List[str] = ["https://"]


def sync_urlopen(url, protocol_allowlist=DEFAULT_PROTOCOL_ALLOWLIST):
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
            args = list(args) + [str(target_path)]
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
