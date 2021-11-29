import os
import json
import time
import pickle
import struct
import asyncio
import pathlib
import logging

import dffml


async def main():
    # Turn on logging
    logging.basicConfig(level=logging.DEBUG)
    # Connect to output socket if present
    output_socket_path = os.environ.get("OUTPUT", "")
    if output_socket_path:
        output_socket_path = pathlib.Path(output_socket_path)
        # TODO Use fanotify or inotify
        while not output_socket_path.is_socket():
            logging.debug(f"Waiting for socket file {output_socket_path!r}")
            time.sleep(0.01)
        _, output_writer = await asyncio.open_unix_connection(
            output_socket_path
        )
    # Assume one context is being run and we want the output of that context
    # [(ctx_as_str, {'product': 36})]
    # So use [0] for first context returned and then [1] to select results
    output = json.dumps(
        dffml.export(
            list(
                [
                    result
                    async for result in dffml.run(
                        dffml.DataFlow._fromdict(
                            **json.loads(
                                pathlib.Path(
                                    os.environ["DATAFLOW"]
                                ).read_text()
                            )
                        ),
                        (
                            [
                                dffml.Input._fromdict(**item)
                                for item in json.loads(
                                    pathlib.Path(
                                        os.environ["INPUTS"]
                                    ).read_bytes()
                                )
                            ]
                            if os.environ.get("INPUTS", "")
                            else []
                        ),
                    )
                ]
            )[0][1]
        )
    )
    if output_socket_path:
        output_writer.write(
            struct.pack("!Q", int(len(output))) + output.encode(),
        )
        await output_writer.drain()
        output_writer.close()
        await output_writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
