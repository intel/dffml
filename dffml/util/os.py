import os
import pathlib
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
def prepend_to_path(*args: str, env = None):
    """
    Prepend all given directories to the ``PATH`` environment variable.
    TODO Should we be modifying in place? Probably need to abstract out to the
    delta on the opimpctx.run() for input network context transfer as optional
    trigger only if not default?
    """
    if env is None:
        # TODO Deprecation warning for non explicit setting of env context.
        env = os.environ
    old_path = env.get("PATH", "")
    # TODO Will this work on Windows?
    env["PATH"] = ":".join(list(map(str, args)) + old_path.split(":"))
    try:
        yield
    finally:
        env["PATH"] = old_path


def which(binary):
    for dirname in os.environ.get("PATH", "").split(":"):
        check_path = pathlib.Path(dirname, binary)
        if check_path.exists():
            return check_path.resolve()
