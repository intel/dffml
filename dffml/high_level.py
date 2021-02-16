"""
High level abstraction interfaces to DFFML. These are probably going to be used
in a lot of quick and dirty python files.
"""
import asyncio
import pathlib
import contextlib
from typing import Optional, Tuple, List, Union, Dict, Any, AsyncIterator

from .record import Record
from .model.model import Model
from .df.types import DataFlow, Input
from .df.memory import MemoryOrchestrator
from .source.source import (
    Sources,
    SourcesContext,
    BaseSource,
    BaseSourceContext,
    BaseSource,
)
from .source.memory import MemorySource, MemorySourceConfig
from .df.base import BaseInputSetContext, BaseOrchestrator, BaseInputSet


@contextlib.asynccontextmanager
async def _records_to_sources(*args):
    """
    Create a memory source out of any records passed as a variable length list.
    Add all sources found in the variable length list to a list of sources, and
    the created source containing records, and return that list of sources.
    """
    sources = Sources()
    sctxs = []
    # Records to add to memory source
    records = []
    # Convert dicts to records
    for i, arg in enumerate(args):
        if isinstance(arg, dict):
            arg = Record(i, data={"features": arg})
        if isinstance(arg, Record):
            records.append(arg)
        elif isinstance(arg, pathlib.Path) or (
            isinstance(arg, str) and "." in arg
        ):
            filepath = pathlib.Path(arg)
            source = BaseSource.load(filepath.suffixes[0].replace(".", ""))
            sources.append(source(filename=arg))
        elif isinstance(arg, (Sources, BaseSource)):
            sources.append(arg)
        elif isinstance(arg, (SourcesContext, BaseSourceContext)):
            sctxs.append(arg)
        else:
            raise ValueError(
                f"Don't know what to do with non-source type: {arg!r}"
            )
    # Create memory source if there are any records
    if records:
        sources.append(MemorySource(MemorySourceConfig(records=records)))
    # Open the sources
    async with sources as sources:
        async with sources() as sctx:
            # Add any already open source contexts
            for already_open_sctx in sctxs:
                sctx.append(already_open_sctx)
            yield sctx


async def run(
    dataflow: DataFlow,
    *input_sets: Union[List[Input], BaseInputSet],
    orchestrator: Optional[BaseOrchestrator] = None,
    strict: bool = True,
    ctx: Optional[BaseInputSetContext] = None,
    halt: Optional[asyncio.Event] = None,
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
    async with orchestrator:
        async with orchestrator(dataflow) as ctx:
            async for ctx, results in ctx.run(*input_sets):
                yield ctx, results


async def save(source: BaseSource, *args: Record) -> None:
    """
    Update a source's knowledge about given records.

    For each record given, call
    :py:func:`update <dffml.source.source.BaseSourceContext.update>` on the
    source. Effectively saving all the records to the source.

    Parameters
    ----------
    source : BaseSource
        Data source to use. See :doc:`/plugins/dffml_source` for sources and
        options.
    *args : list
        Records to be saved.

    Examples
    --------

    >>> import asyncio
    >>> import pathlib
    >>> from dffml import *
    >>>
    >>> source = CSVSource(filename="save.csv", allowempty=True, readwrite=True)
    >>>
    >>> async def main():
    ...     await save(
    ...         source,
    ...         Record(
    ...             "myrecord",
    ...             data={
    ...                 "features": {"Years": 0, "Expertise": 1, "Trust": 0.1},
    ...                 "prediction": {"Salary": {"value": 10, "confidence": 1.0}},
    ...             }
    ...         )
    ...     )
    ...     print(pathlib.Path("save.csv").read_text().strip())
    >>>
    >>> asyncio.run(main())
    key,tag,Expertise,Trust,Years,prediction_Salary,confidence_Salary
    myrecord,untagged,1,0.1,0,10,1.0
    """
    async with _records_to_sources(source) as sctx:
        for record in args:
            await sctx.update(record)


async def load(source: BaseSource, *args: str) -> AsyncIterator[Record]:
    """
    Yields records from a source.

    Yields all the records from the source, if record keys are given then only
    those records are yielded.

    Parameters
    ----------
    source : BaseSource
        Data source to use. See :doc:`/plugins/dffml_source` for sources and
        options.
    *args : str
        Records to be returned. If empty, all the records in a source will be returned.

    Returns
    -------
    asynciterator
        :py:class:`Record <dffml.record.Record>` object

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> source = CSVSource(filename="load.csv", allowempty=True, readwrite=True)
    >>>
    >>> async def main():
    ...     await save(
    ...         source,
    ...         Record("1", data={"features": {"A": 0, "B": 1}}),
    ...         Record("2", data={"features": {"A": 3, "B": 4}}),
    ...     )
    ...
    ...     # All records in source
    ...     async for record in load(source):
    ...         print(record.export())
    ...
    ...     # For specific records in a source
    ...     async for record in load(source, "1"):
    ...         print(record.export())
    ...
    ...     # Lightweight source syntax
    ...     async for record in load("load.csv", "2"):
    ...         print(record.export())
    >>>
    >>> asyncio.run(main())
    {'key': '1', 'features': {'A': 0, 'B': 1}, 'extra': {}}
    {'key': '2', 'features': {'A': 3, 'B': 4}, 'extra': {}}
    {'key': '1', 'features': {'A': 0, 'B': 1}, 'extra': {}}
    {'key': '2', 'features': {'A': 3, 'B': 4}, 'extra': {}}
    """
    async with _records_to_sources(source) as sctx:
        if args:
            # If specific records are to be loaded
            for record in args:
                yield await sctx.record(record)
        else:
            # All the records are loaded
            async for record in sctx.records():
                yield record


async def train(model, *args: Union[BaseSource, Record, Dict[str, Any]]):
    """
    Train a machine learning model.

    Provide records to the model to train it. The model should be already
    instantiated.

    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    *args : list
        Input data for training. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> model = SLRModel(
    ...     features=Features(
    ...         Feature("Years", int, 1),
    ...     ),
    ...     predict=Feature("Salary", int, 1),
    ...     directory="tempdir",
    ... )
    >>>
    >>> async def main():
    ...     await train(
    ...         model,
    ...         {"Years": 0, "Salary": 10},
    ...         {"Years": 1, "Salary": 20},
    ...         {"Years": 2, "Salary": 30},
    ...         {"Years": 3, "Salary": 40},
    ...     )
    >>>
    >>> asyncio.run(main())
    """
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(_records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        # Run training
        return await mctx.train(sctx)


async def accuracy(
    model, *args: Union[BaseSource, Record, Dict[str, Any]]
) -> float:
    """
    Assess the accuracy of a machine learning model.

    Provide records to the model to assess the percent accuracy of its
    prediction abilities. The model should be already instantiated and trained.

    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    *args : list
        Input data for training. Could be a ``dict``, :py:class:`Record`,
        filename, one of the data :doc:`/plugins/dffml_source`, or a filename
        with the extension being one of the data sources.

    Returns
    -------
    float
        A decimal value representing the percent of the time the model made the
        correct prediction. For some models this has another meaning. Please see
        the documentation for the model your using for further details.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> model = SLRModel(
    ...     features=Features(
    ...         Feature("Years", int, 1),
    ...     ),
    ...     predict=Feature("Salary", int, 1),
    ...     directory="tempdir",
    ... )
    >>>
    >>> async def main():
    ...     print(
    ...         "Accuracy:",
    ...         await accuracy(
    ...             model,
    ...             {"Years": 4, "Salary": 50},
    ...             {"Years": 5, "Salary": 60},
    ...         ),
    ...     )
    >>>
    >>> asyncio.run(main())
    Accuracy: 1.0
    """
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(_records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        # Run accuracy method
        return float(await mctx.accuracy(sctx))


async def predict(
    model,
    *args: Union[BaseSource, Record, Dict[str, Any]],
    update: bool = False,
    keep_record: bool = False,
):
    """
    Make a prediction using a machine learning model.

    The model must be trained before using it to make a prediction.

    Parameters
    ----------
    model : Model
        Machine Learning model to use. See :doc:`/plugins/dffml_model` for
        models options.
    *args : list
        Input data for prediction. Could be a ``dict``, :py:class:`Record`,
        filename, or one of the data :doc:`/plugins/dffml_source`.
    update : boolean, optional
        If ``True`` prediction data within records will be written back to all
        sources given. Defaults to ``False``.
    keep_record : boolean, optional
        If ``True`` the results will be kept as their ``Record`` objects instead
        of being converted to a ``(record.key, features, predictions)`` tuple.
        Defaults to ``False``.

    Returns
    -------
    asynciterator
        ``Record`` objects or ``(record.key, features, predictions)`` tuple.

    Examples
    --------

    >>> import asyncio
    >>> from dffml import *
    >>>
    >>> model = SLRModel(
    ...     features=Features(
    ...         Feature("Years", int, 1),
    ...     ),
    ...     predict=Feature("Salary", int, 1),
    ...     directory="tempdir",
    ... )
    >>>
    >>> async def main():
    ...     async for i, features, prediction in predict(
    ...         model,
    ...         {"Years": 6},
    ...         {"Years": 7},
    ...     ):
    ...         features["Salary"] = round(prediction["Salary"]["value"])
    ...         print(features)
    >>>
    >>> asyncio.run(main())
    {'Years': 6, 'Salary': 70}
    {'Years': 7, 'Salary': 80}
    """
    async with contextlib.AsyncExitStack() as astack:
        # Open sources
        sctx = await astack.enter_async_context(_records_to_sources(*args))
        # Allow for keep models open
        if isinstance(model, Model):
            model = await astack.enter_async_context(model)
            mctx = await astack.enter_async_context(model())
        # Run predictions
        async for record in mctx.predict(sctx):
            yield record if keep_record else (
                record.key,
                record.features(),
                record.predictions(),
            )
            if update:
                await sctx.update(record)
