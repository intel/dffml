import asyncio

from .asynchelper import concurrently


async def run_command(cmd, logger=None, **kwargs):
    r"""
    Run a command using :py:func:`asyncio.create_subprocess_exec`.

    If ``logger`` is supplied, write stdout and stderr to logger debug.

    ``kwargs`` are passed to :py:func:`asyncio.create_subprocess_exec`, except
    for stdout and stderr which are pipes used for logging.

    Examples
    --------

    >>> import sys
    >>> import asyncio
    >>> import logging
    >>>
    >>> import dffml
    >>>
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> logger = logging.getLogger("mylogger")
    >>>
    >>> asyncio.run(dffml.run_command([
    ...     sys.executable, "-c", "print('Hello World')"
    ... ], logger=logger))

    You should see "Hello World" in the logging output

    .. code-block::

	DEBUG:asyncio:Using selector: EpollSelector
	DEBUG:mylogger:Running ['/usr/bin/python3.7', '-c', "print('Hello World')"], {'stdout': -1, 'stderr': -1}
	DEBUG:mylogger:['/usr/bin/python3.7', '-c', "print('Hello World')"]: stdout.readline: Hello World
	DEBUG:mylogger:['/usr/bin/python3.7', '-c', "print('Hello World')"]: stderr.readline:
    """
    kwargs = {
        "stdout": asyncio.subprocess.PIPE,
        "stderr": asyncio.subprocess.PIPE,
        **kwargs,
    }
    if logger is not None:
        logger.debug(f"Running {cmd}, {kwargs}")
    proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)
    work = {
        asyncio.create_task(proc.wait()): "wait",
    }
    for output in ["stdout", "stderr"]:
        if output in kwargs and kwargs[output] is asyncio.subprocess.PIPE:
            coro = getattr(proc, output).readline()
            task = asyncio.create_task(coro)
            work[task] = f"{output}.readline"
    output = []
    async for event, result in concurrently(work):
        if event.endswith("readline"):
            # Log line read
            if logger is not None:
                logger.debug(f"{cmd}: {event}: {result.decode().rstrip()}")
            # Append to output in case of error
            output.append(result)
            # Read another line if that's the event
            coro = getattr(proc, event.split(".")[0]).readline()
            task = asyncio.create_task(coro)
            work[task] = event
        else:
            # When wait() returns process has exited
            break

    if proc.returncode != 0:
        raise RuntimeError(repr(cmd) + ": " + b"\n".join(output).decode())
