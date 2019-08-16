"""
Asynchronous subprocess interaction.
"""
import os
import asyncio.subprocess

from .log import LOGGER


def inpath(binary):
    return any(
        list(
            map(
                lambda dirname: os.path.isfile(os.path.join(dirname, binary)),
                os.environ.get("PATH", "").split(":"),
            )
        )
    )


async def stop(proc):
    """
    Stops a subprocess
    """
    exit_code = await proc.wait()
    if exit_code != 0:
        raise RuntimeError(
            "'%s' exited with code %d: '%s'"
            % (
                getattr(proc, "name", "subprocess"),
                exit_code,
                getattr(proc, "data", "").rstrip(),
            )
        )
    return exit_code, proc


async def create(*args, **kwargs):
    """
    Runs a subprocess using asyncio.create_subprocess_exec and returns the
    process.
    """
    LOGGER.debug("proc.create: %r", args)
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
        **kwargs,
    )
    proc.name = args[0]
    proc.args = args[1:]
    return proc


async def get_output(proc):
    """
    Combines stdout and stderr
    """
    stderr = (await proc.stderr.read()).decode(errors="ignore")
    stdout = (await proc.stdout.read()).decode(errors="ignore")
    proc.data = stdout + stderr
    return stdout, stderr


async def check_output(*args, **kwargs):
    """
    Runs a subprocess using asyncio.create_subprocess_exec and returns either
    its standard error or output.
    """
    proc = await create(*args, **kwargs)
    stdout, stderr = await get_output(proc)
    await stop(proc)
    return stdout or stderr
