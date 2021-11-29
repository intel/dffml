"""
UNIX socket server which should only ever accept one connection.
"""
import sys
import struct
import asyncio
import pathlib
from typing import Union, Tuple, AsyncIterator

import dffml


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
        async for event, result in dffml.concurrently(work):
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
