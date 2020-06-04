import asyncio

from . import high_level


def train(*args, **kwargs):
    return asyncio.run(high_level.train(*args, **kwargs))


train.__doc__ = (
    high_level.train.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def accuracy(*args, **kwargs):
    return asyncio.run(high_level.accuracy(*args, **kwargs))


accuracy.__doc__ = (
    high_level.accuracy.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def predict(*args, **kwargs):
    async_gen = high_level.predict(*args, **kwargs).__aiter__()

    loop = asyncio.new_event_loop()

    def cleanup():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            cleanup()
            return
        except:
            cleanup()
            raise


predict.__doc__ = (
    high_level.predict.__doc__.replace("await ", "")
    .replace("asynciterator", "iterator")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def save(*args, **kwargs):
    return asyncio.run(high_level.save(*args, **kwargs))


save.__doc__ = (
    high_level.save.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def load(*args, **kwargs):
    async_gen = high_level.load(*args, **kwargs).__aiter__()

    loop = asyncio.new_event_loop()

    def cleanup():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            cleanup()
            return
        except:
            cleanup()
            raise


load.__doc__ = (
    high_level.load.__doc__.replace("await ", "")
    .replace("async ", "")
    .replace("asyncio.run(main())", "main()")
    .replace("    >>> import asyncio\n", "")
    .replace(
        "    >>> from dffml import *\n",
        "    >>> from dffml import *\n    >>> from dffml.noasync import *\n",
    )
)


def run(*args, **kwargs):
    """
    >>> # Socket server derived from
    >>> # https://docs.python.org/3/library/socketserver.html#asynchronous-mixins
    >>> import socket
    >>> import threading
    >>> import socketserver
    >>>
    >>> from dffml.noasync import run
    >>> from dffml import DataFlow, Input, op
    >>>
    >>> class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    ...     def handle(self):
    ...         data = str(self.request.recv(1024), "ascii")
    ...         response = bytes("{}".format(data), "ascii")
    ...         self.request.sendall(response)
    >>>
    >>> class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    ...     pass
    >>>
    >>> @op
    ... def client(ip: str, port: int, message: str):
    ...     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    ...         sock.connect((ip, port))
    ...         sock.sendall(bytes(message, "ascii"))
    ...         response = str(sock.recv(1024), "ascii")
    ...         print("Received: {}".format(response))
    >>>
    >>> dataflow = DataFlow.auto(client)
    >>>
    >>> messages = [
    ...     Input(value="Hello World!", definition=client.op.inputs["message"])
    ...     for _ in range(0, 2)
    ... ]
    >>>
    >>> def main():
    ...     # Port 0 means to select an arbitrary unused port
    ...     HOST, PORT = "localhost", 0
    ...
    ...     server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ...     with server:
    ...         ip, port = server.server_address
    ...
    ...         # Start a thread with the server -- that thread will then start one
    ...         # more thread for each request
    ...         server_thread = threading.Thread(target=server.serve_forever)
    ...         # Exit the server thread when the main thread terminates
    ...         server_thread.daemon = True
    ...         server_thread.start()
    ...         print("Server loop running in a thread")
    ...
    ...         inputs = messages + [
    ...             Input(value=ip, definition=client.op.inputs["ip"]),
    ...             Input(value=port, definition=client.op.inputs["port"]),
    ...         ]
    ...
    ...         try:
    ...             for ctx, results in run(dataflow, inputs):
    ...                 pass
    ...         finally:
    ...             server.shutdown()
    >>>
    >>> main()
    Server loop running in a thread
    Received: Hello World!
    Received: Hello World!
    """
    async_gen = high_level.run(*args, **kwargs).__aiter__()

    loop = asyncio.new_event_loop()

    def cleanup():
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    while True:
        try:
            yield loop.run_until_complete(async_gen.__anext__())
        except StopAsyncIteration:
            cleanup()
            return
        except:
            cleanup()
            raise
