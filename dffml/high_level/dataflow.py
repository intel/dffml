import asyncio
from typing import Optional, Tuple, List, Union, Dict, Any, AsyncIterator

from ..overlay.overlay import Overlay
from ..df.types import DataFlow, Input
from ..df.memory import MemoryOrchestrator
from ..df.base import BaseInputSetContext, BaseOrchestrator, BaseInputSet


class _LOAD_DEFAULT:
    pass


LOAD_DEFAULT = _LOAD_DEFAULT()


async def run(
    dataflow: DataFlow,
    *input_sets: Union[List[Input], BaseInputSet],
    orchestrator: Optional[BaseOrchestrator] = None,
    strict: bool = True,
    ctx: Optional[BaseInputSetContext] = None,
    halt: Optional[asyncio.Event] = None,
    overlay: Union[None, _LOAD_DEFAULT, DataFlow] = LOAD_DEFAULT,
) -> AsyncIterator[Tuple[BaseInputSetContext, Dict[str, Any]]]:
    """
    Run a DataFlow

    Run a DataFlow using the the default orchestrator
    (:py:class:`MemoryOrchestrator <dffml.df.memory.MemoryOrchestrator>`),
    or the specified one.

    Parameters
    ----------
    dataflow : DataFlow
        :py:class:`DataFlow <dffml.df.types.DataFlow>` to run.
    input_sets : InputSet, list, dict, optional
        :py:class:`Inputs <dffml.df.types.Input>` to give to the
        :py:class:`DataFlow <dffml.df.types.DataFlow>` when it starts. Can be in
        multiple formats.

        If each element is a ``list`` then it's expected that each element of
        that list be an :py:class:`Input <dffml.df.types.Input>`, in this case
        an :py:class:`InputSet <dffml.df.base.BaseInputSet>` will be created
        with a random string used as the
        :py:class:`StringInputSetContext <dffml.df.base.StringInputSetContext>`.

        If a ``dict`` is given then each key will become a
        :py:class:`StringInputSetContext <dffml.df.base.StringInputSetContext>`.
        The value for each key should be a ``list`` of
        :py:class:`Input <dffml.df.types.Input>` objects.

        If each element is a :py:class:`InputSet <dffml.df.base.BaseInputSet>`
        then each context
        :py:class:`InputSetContext <dffml.df.base.BaseInputSetContext>`
        will have its respective :py:class:`Inputs <dffml.df.types.Input>` added
        to it.
    orchestrator : BaseOrchestrator, optional
        Orchestrator to use, defaults to
        :py:class:`MemoryOrchestrator <dffml.df.memory.MemoryOrchestrator>`
        if ``None``.
    strict : bool, optional
        If true (default), raise exceptions when they occur in operations. If
        false, log exceptions without raising.
    ctx : BaseInputSetContext, optional
        If given and input_sets is a ``list`` then add inputs under the given
        context. Otherwise they are added under randomly generated contexts.
    halt : Event, optional
        If given, keep the dataflow running until this :py:class:`asyncio.Event`
        is set.

    Returns
    -------
    asynciterator
        ``tuple`` of
        :py:class:`InputSetContext <dffml.df.base.BaseInputSetContext>`
        and ``dict`` where contents are determined by output operations.
        If multiple output operations are used, then the top level keys will be
        the names of the output operations. If only one is used, then the
        ``dict`` will be whatever the return value of that output operation was.

    Examples
    --------

    The following creates a TCP echo server. We write an operation which using a
    DataFlow to open a connection and send a message to the server.

    For the inputs to the DataFlow, we create 2 Input objects whose values are
    the message to be sent to the TCP server. We also create Input objects for
    the host and port. When running a DataFlow, operations will be run with each
    possible permutation of their inputs.

    .. TODO Autogenerate this image during docs build

        graph LR
          send_to_server

          1[First echo message]
          port[Port]
          host[Host]
          2[Second echo message]

          1_c[Host, Port, First echo]
          2_c[Host, Port, Second echo]

          host --> 1_c
          port --> 1_c
          2 --> 2_c
          port --> 2_c
          host --> 2_c
          1 --> 1_c

          1_c --> send_to_server
          2_c --> send_to_server

    .. image:: /images/high_level_run_echo_server_input_combination.svg
        :alt: Flow chart showing how both echo messages create a parameter set including that echo message and the host and port

    Because there is a different Input object for each of the 2 "echo" messages,
    one will get combined with the host and port to make an argument list for
    the ``send_to_server`` operation. The other also combines with the host and
    port to make another argument list. Both argument lists are used to call the
    ``send_to_server`` operation.

    >>> # Socket server derived from
    >>> # https://docs.python.org/3/library/socketserver.html#asynchronous-mixins
    >>> import asyncio
    >>> import threading
    >>> import socketserver
    >>> from dffml import *
    >>>
    >>> class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    ...     def handle(self):
    ...         self.request.sendall(self.request.recv(1024))
    >>>
    >>> class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    ...     pass
    >>>
    >>> @op
    ... async def send_to_server(host: str, port: int, message: str):
    ...     reader, writer = await asyncio.open_connection(host, port)
    ...
    ...     writer.write(message.encode())
    ...     await writer.drain()
    ...
    ...     data = await reader.read(100)
    ...     print(f"Client sent {message!r}, got: {data.decode()!r}")
    ...
    ...     writer.close()
    ...     await writer.wait_closed()
    >>>
    >>> # List of messages to send to the server, 2 long, each value is "echo"
    >>> messages = [Input(value="echo", definition=send_to_server.op.inputs["message"])
    ...             for _ in range(0, 2)]
    >>>
    >>> # DataFlow consisting of the single operation
    >>> dataflow = DataFlow.auto(send_to_server)
    >>>
    >>> async def main():
    ...     # Create a server with and pass 0 to get a random port assigned
    ...     server = ThreadedTCPServer(("127.0.0.1", 0), ThreadedTCPRequestHandler)
    ...     with server:
    ...         host, port = server.server_address
    ...
    ...         # Start a thread to run the server in the background
    ...         server_thread = threading.Thread(target=server.serve_forever)
    ...         # Exit the server thread when the main thread terminates
    ...         server_thread.daemon = True
    ...         server_thread.start()
    ...
    ...         # Add the host and port to the list of Inputs for the DataFlow
    ...         inputs = messages + [
    ...             Input(value=host, definition=send_to_server.op.inputs["host"]),
    ...             Input(value=port, definition=send_to_server.op.inputs["port"])
    ...         ]
    ...
    ...         try:
    ...             async for ctx, results in run(dataflow, inputs):
    ...                 pass
    ...         finally:
    ...             server.shutdown()
    >>>
    >>> asyncio.run(main())
    Client sent 'echo', got: 'echo'
    Client sent 'echo', got: 'echo'
    """
    if orchestrator is None:
        orchestrator = MemoryOrchestrator.withconfig({})
    # TODO(alice) Rework once we have system context. Run overlay system context
    # using orchestrator from that. System context is basic clay a dataclass
    # with the properties as this functions arguments.
    if overlay is LOAD_DEFAULT:
        # Load defaults via entrypoints, aka installed dataflows registered as
        # plugins.
        # TODO Maybe pass orchestrator to default
        overlay = await Overlay.default(orchestrator)
    # Apply overlay if given or installed
    if overlay is not None:
        # This effectivly creates a new system context, a direct ancestor of the
        # of the one that got passed in and the overlay. Therefore they are both
        # listed in the input parents when we finally split this out so that run
        # is called as an operation, where the overlay is applied prior to
        # calling run.
        dataflow = await overlay.apply(orchestrator, dataflow)
    async with orchestrator:
        async with orchestrator(dataflow) as ctx:
            async for ctx, results in ctx.run(*input_sets, strict=strict):
                yield ctx, results
