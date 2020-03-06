import os
import contextlib


# When creating files or directories we should always default to only allowing
# the user to access or edit the files or directories.
MODE_BITS_SECURE = 0o700


@contextlib.contextmanager
def chdir(new_path):
    """
    Context manager to change directroy
    """
    old_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(old_path)


@contextlib.contextmanager
def prepend_to_path(*args: str):
    """
    Prepend all given directories to the ``PATH`` environment variable.
    """
    old_path = os.environ.get("PATH", "")
    # TODO Will this work on Windows?
    os.environ["PATH"] = ":".join(list(map(str, args)) + old_path.split(":"))
    try:
        yield
    finally:
        os.environ["PATH"] = old_path
