import enum
import asyncio
from typing import List

from .asynchelper import concurrently


class Subprocess(enum.Enum):
    CREATED = "created"
    COMPLETED = "completed"
    STDOUT_READLINE = "stdout.readline"
    STDERR_READLINE = "stderr.readline"
    STDOUT = "stdout"
    STDERR = "stderr"


async def exec_subprocess(cmd, **kwargs):
    kwargs = {
        "stdout": asyncio.subprocess.PIPE,
        "stderr": asyncio.subprocess.PIPE,
        **kwargs,
    }
    proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)
    yield Subprocess.CREATED, proc
    work = {
        asyncio.create_task(proc.wait()): "wait",
    }
    for output in ["stdout", "stderr"]:
        if output in kwargs and kwargs[output] is asyncio.subprocess.PIPE:
            coro = getattr(proc, output).readline()
            task = asyncio.create_task(coro)
            work[task] = f"{output}.readline"
    async for event, result in concurrently(work):
        if event.endswith("readline"):
            if result == b"":
                continue
            # Yield line to caller
            yield Subprocess[event.replace(".", "_").upper()], result
            # Read another line if that's the event
            coro = getattr(proc, event.split(".")[0]).readline()
            task = asyncio.create_task(coro)
            work[task] = event
    # Yield when process exits
    yield Subprocess.COMPLETED, proc.returncode


async def run_command_events(
    cmd,
    *,
    logger=None,
    log_cmd_event: bool = True,
    events: List[Subprocess] = None,
    **kwargs,
):
    # Combination of stdout and stderr
    output = {
        Subprocess.STDOUT_READLINE: [],
        Subprocess.STDERR_READLINE: [],
        "combinded": [],
    }
    if logger is not None:
        logger.debug(f"Running {cmd}, {kwargs}")
    async for event, result in exec_subprocess(cmd, **kwargs):
        if event == Subprocess.CREATED:
            # Set proc when created
            proc = result
        elif event in [Subprocess.STDOUT_READLINE, Subprocess.STDERR_READLINE]:
            # Log line read
            if logger is not None:
                log_message = result.decode().rstrip()
                if log_cmd_event:
                    log_message = f"{cmd}: {event}: {log_message}"
                logger.debug(log_message)
            # Append to output in case of error
            output[event].append(result)
            output["combinded"].append(result)
        # Raise if anything goes wrong
        elif event == Subprocess.COMPLETED:
            if result != 0:
                raise RuntimeError(
                    repr(cmd) + ": " + b"".join(output["combinded"]).decode()
                )
            else:
                # If caller wants event
                if Subprocess.STDERR in events:
                    yield Subprocess.STDERR, b"".join(
                        output[Subprocess.STDERR_READLINE]
                    )
                if Subprocess.STDOUT in events:
                    yield Subprocess.STDOUT, b"".join(
                        output[Subprocess.STDOUT_READLINE]
                    )
                return
        # If caller wants event
        if events and event in events:
            yield event, result


async def run_command(
    cmd, *, logger=None, log_cmd_event: bool = True, **kwargs
):
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
    async for _, _ in run_command_events(
        cmd, logger=logger, log_cmd_event=log_cmd_event, **kwargs
    ):
        pass
