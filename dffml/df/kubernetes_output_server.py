"""
UNIX socket server which should only ever accept one connection.
"""
import sys
import struct
import asyncio
import pathlib
import logging
from typing import (
    Dict,
    Any,
    AsyncIterator,
    Tuple,
    Union,
    Type,
    AsyncContextManager,
    Optional,
    Set,
)


LOGGER = logging.getLogger(pathlib.Path(__file__).stem)

# TODO Use importlib.resources instead of reading via pathlib
PYTHON_CODE: str = pathlib.Path(__file__).parent.joinpath(
    "kubernetes_execute_pickled_dataflow_with_inputs.py"
).read_text()
OUTPUT_SERVER: str = pathlib.Path(__file__).read_text()


async def concurrently(
    work: Dict[asyncio.Task, Any],
    *,
    errors: str = "strict",
    nocancel: Optional[Set[asyncio.Task]] = None,
) -> AsyncIterator[Tuple[Any, Any]]:
    # Set up logger
    logger = LOGGER.getChild("concurrently")
    # Track if first run
    first = True
    # Set of tasks we are waiting on
    tasks = set(work.keys())
    # Return when outstanding operations reaches zero
    try:
        while first or tasks:
            first = False
            # Wait for incoming events
            done, _pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                # Remove the task from the set of tasks we are waiting for
                tasks.remove(task)
                # Get the tasks exception if any
                exception = task.exception()
                if errors == "strict" and exception is not None:
                    raise exception
                if exception is None:
                    # Remove the compeleted task from work
                    complete = work[task]
                    del work[task]
                    yield complete, task.result()
                    # Update tasks in case work has been updated by called
                    tasks = set(work.keys())
                else:
                    logger.debug(
                        "[%s] Ignoring exception: %s", task, exception
                    )
    finally:
        for task in tasks:
            if not task.done() and (nocancel is None or task not in nocancel):
                task.cancel()
            else:
                # For tasks which are done but have exceptions which we didn't
                # raise, collect their exceptions
                task.exception()


async def server_socket_unix_stream(
    socket_path: Union[str, pathlib.Path], stop: asyncio.Event,
) -> AsyncIterator[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
    queue = asyncio.Queue()

    async def handler(reader, writer):
        nonlocal queue
        await queue.put((reader, writer))

    work = {
        asyncio.create_task(stop.wait()): "stop.wait",
        asyncio.create_task(queue.get()): "queue.get",
    }
    server = await asyncio.start_unix_server(handler, path=socket_path)
    async with server:
        await server.start_serving()
        async for event, result in concurrently(work):
            if event == "queue.get":
                yield result
                work[asyncio.create_task(queue.get())] = event
            else:
                break
        server.close()
        await server.wait_closed()


BASIC_BINARY_PROTOCOL_FORMAT: str = "!Q"
BASIC_BINARY_PROTOCOL_SIZE: int = struct.calcsize(BASIC_BINARY_PROTOCOL_FORMAT)


async def read_messages(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
) -> AsyncIterator[bytes]:
    size = struct.unpack(
        BASIC_BINARY_PROTOCOL_FORMAT,
        await reader.readexactly(BASIC_BINARY_PROTOCOL_SIZE),
    )[0]
    # Only read one message per connection for now
    yield await reader.readexactly(size)
    writer.close()


async def main():
    stop = asyncio.Event()
    async for reader, writer in server_socket_unix_stream(sys.argv[-1], stop):
        async for message in read_messages(reader, writer):
            sys.stdout.buffer.write(message)
            # Read one message for now
            stop.set()


if __name__ == "__main__":
    asyncio.run(main())
