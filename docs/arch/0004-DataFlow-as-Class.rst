4. DataFlow as Class
====================

Date: 2022-03-12

Status
------

Draft

Context
-------

Plugins are classes. For ease of implemention / dynamic implmentation of a
plugin we can leverage DataFlows.

Decision
--------

We want to create a helper which takes a DataFlow and information about method
names and arguments to output a class. We can offer multiple implementations,
for example we could offer one to write out a class in a given programming
language.

Consequences
------------

We're going to do an initial implementation by making a class method on DataFlow
which takes

- Class Definition

  - Name of class

  - RunDataFlow CLI-esq config with orchestrator

  - Allow for mapping arguments to class ``__init__`` to anywhere within the
    DataFlow by taking arguments as a config class. Mapped to function which
    should accept as arguments, in order: ``dataclass`` the object we are
    expressing as a class, ``config`` the instantiated config object to access
    other config values, ``field`` the current field, ``value`` the value we
    need to set on the object we are expressing as a class (``dataflow``).

    - From ``field.metadata.as_class.dataflow`` first

    - Overridable by dict passed as ``init_argument_map`` during call to
      ``as_class``.

- Class instantiation

  - Double context entry on orchestrator

- Method Definition

  - Method name as input similar using context def from dataflow run context CLI

  - Map arguments and keyword arguments to inputs and definitions

  - Allow for adding a predefined set of inputs for a given method

  - Inputs may also come from seed, auto started operations, or input networks

  - DataFlow with output operations which will be used to query outputs from
    input network context of the class's dataflow.

  - Similar to context def with ability to pass class instance as value for
    input.

- Method Call

  - Submit new context

  - Wait for context done event for your context

    - Could leverage :py:func:`dffml.df.memory.NotificationSet`

      - TODO Make ``BaseNotificationSet``

  - Run method's DataFlow containing output operations to query outputs of
    method run.

**dataflow_as_class_dbm_source.py**

.. code-block:: python
    :test:
    :filepath: dataflow_as_class_dbm_source.py

    import dbm
    import json
    import functools
    import contextlib
    from typing import Any, Dict, Callable

    import dffml


    # TODO Move this helper function to util
    def gen_fn(args: Dict[str, Any], new_fn: Callable) -> Callable:
        """
        Source (CC BY-SA 4.0): https://stackoverflow.com/a/50385115
        https://creativecommons.org/licenses/by-sa/4.0/legalcode
        From stackoverflow user Aran-Fey. Copied 2022-03-13.

        Examples

        >>> print(inspect.signature(gen_fn({'a': int})))
        (a:int,)
        >>> print(get_type_hints(gen_fn({'a': int})))
        {'a': <class 'int'>}
        """
        # TODO Move this to global scope
        import inspect


        params = [inspect.Parameter(param,
                                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                    annotation=type_)
                                for param, type_ in args.items()]
        new_fn.__signature__ = inspect.Signature(params)
        new_fn.__annotations__ = args

        return new_fn


    def config_to_new_fn(
        new_fn: Callable,
    ) -> Callable:
        # The function which will be in charge of running the dataflow
        # We will fixup it's method signature using inspect.
        def func_run_dataflow(self, *args, **kwargs):
            return self._func_run_dataflow(*args, **kwargs)

        func_run_dataflow = gen_fn(args)

        # {'a': int}
        return func_run_dataflow



    records = [
        dffml.Record("a", data={"features": {"one": 42}}),
        dffml.Record("b", data={"features": {"one": 420}}),
    ]

    DBM_FILENAME = "mydbm.dbm"

    # Create the database with stdlib dbm API
    with dbm.open(DBM_FILENAME, "c") as db:
        # Write some records
        for record in records:
            db[record.key] = json.dumps(record.export())


    class DataFlowClass:
        @classmethod
        def _add_dataflow_method(cls, name, config: RunCMDConfig):
            """
            @config
            class RunCMDConfig:
                dataflow: str = field(
                    "File containing exported DataFlow", required=True,
                )
                configloader: BaseConfigLoader = field(
                    "ConfigLoader to use for importing DataFlow", default=None,
                )
                sources: Sources = FIELD_SOURCES
                caching: List[str] = field(
                    "Skip running DataFlow if a record already contains these features",
                    default_factory=lambda: [],
                )
                no_update: bool = field(
                    "Update record with sources", default=False,
                )
                no_echo: bool = field(
                    "Do not echo back records", default=False,
                )
                no_strict: bool = field(
                    "Do not exit on operation exceptions, just log errors", default=False,
                )
                orchestrator: BaseOrchestrator = field(
                    "Orchestrator", default=MemoryOrchestrator,
                )
                inputs: List[str] = field(
                    "Other inputs to add under each ctx (record's key will "
                    + "be used as the context)",
                    action=ParseInputsAction,
                    default_factory=lambda: [],
                )
                record_def: str = field(
                    "Definition to be used for record.key."
                    + "If set, record.key will be added to the set of inputs "
                    + "under each context (which is also the record's key)",
                    default=False,
                )
            """
            setattr(
                cls,
                name,
                config_to_new_fn(
                    name,
                    config,
                    dataflow,
                )
            )


    # TODO Implement calling lambda's defined within config field metadata
    def as_class_from_config():
        pass


    @classmethod
    def make_class(cls, name, dataflow, config_cls, base_classes = None):
        if base_classes is None:
            base_classes = tuple()
        type_classes = tuple(
            [
                *base_classes,
                DataFlowClass,
            ],
        )
        new_class = type(
            name,
            type_classes,
            {
                "DATAFLOW": dataflow,
            },
        )
        new_class.__init__ = gen_fn({}, functools.partial(as_class_from_config, "dataflow"))
        return new_class


    dffml.DataFlow.make_class = make_class


    @classmethod
    def as_class(cls, name, dataflow, config_cls, methods, base_classes = None):
        dataflow_cls = cls.make_class(name, dataflow, config_cls, base_classes=base_classes)
        # TODO This for loop is just a sketch, fill it out and validate it
        for method_name, method_kwargs in methods.items():
            dataflow_cls._add_dataflow_method(method_name, **method_kwargs)
        return dataflow_cls


    dffml.DataFlow.as_class = as_class


    @classmethod
    def as_plugin(cls, name, dataflow, config_cls, methods, base_classes = None):
        """
        Call and return the same class as the ``as_class`` classmethod. However,
        set dffml plugin specific properties, such as ``CONFIG``,
        ``entrypoint``, etc.
        """
        if base_classes is None:
            base_classes = tuple()
        base_classes = tuple(
            [
                *base_classes,
                dffml.BaseDataFlowFacilitatorObject,
            ],
        )
        # Check if we need to set config object for __init__ as CONFIG to
        # support DFFML plugin classes
        plugin_cls = cls.as_class(
            name,
            dataflow,
            config_cls,
            methods,
            base_classes=base_classes,
        )
        return plugin_cls


    dffml.DataFlow.as_plugin = as_plugin


    # Configuration for operations
    # TODO(shared_config) We can share the opener object across DBM Operations.
    @dffml.config
    class DBMHandleConfig:
        filename: str


    # We've effectivly created a new plugin type here
    # We leave off the context for now
    # NOTE Wow, so much boilerplate.
    class DBMHandleContext(dffml.BaseDataFlowFacilitatorObjectContext):
        async def __aenter__(self):
            with dbm.open(self.config.filename, "c") as db:
                self.db = self
                return self

    @dffml.base_entry_point("dffml.operation.dbm.handle", "dbm", "handle")
    class DBMHandle(dffml.BaseDataFlowFacilitatorObject):
        CONFIG = DBMHandleConfig
        CONTEXT = DBMHandleContext

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.db = None

        async def __aenter__(self):
            if self.db is not None:
                # Open database connection if not already open
                with dbm.open(self.config.filename, "c") as db:
                    self.db = self
            return self


    @dffml.config
    class DBMOperationConfig:
        dbm: DBMHandle


    @dffml.op(
        config_cls=DBMOperationConfig,
        imp_enter={
            "dbm": lambda self: self.config.dbm,
        },
        ctx_enter={
            "dbm_ctx": lambda self: self.parent.dbm(),
        },
    )
    async def dbm_record(self, key: str) -> dict:
        return dffml.Record(key, data=json.loads(self.dbm_ctx.dbm[key]))


    # TODO(shared_config) Share same instance of db returned from dbm.open via
    # shared config across operation implementation instances.
    dbm_handle = DBMHandle(
        filename=DBM_FILENAME,
    )

    # The DataFlow with operations used to access the DBM
    dbm_source_dataflow = dffml.DataFlow(
        # TODO Write operations
        dbm_record,
        # dbm_records,
        # dbm_update,
        configs={
            dbm_record.op.name: {
                "dbm": dbm_handle,
            },
        }
    )


    # The config for the dataflow class.
    # Contains mapping functions as lambdas
    @dffml.config
    class DBMSourceConfig:
        filename: str = dffml.field(
            "The filename to use for the dbm",
            metadata={
                "as_class": {
                    # TODO(shared_config) Right now these all map to the
                    # same instance in memory. We need to implmenent shared
                    # config so that non-python interfaces can share
                    # instances of objects between configs. We'll probably
                    # also need to make sure their context managers are
                    # re-intrant.
                    # References:
                    # - https://stackoverflow.com/questions/47808851/python-how-to-create-a-concurrent-safe-reentrant-context-manager-which-is-diffe
                    # - https://docs.python.org/3/library/contextvars.html
                    # - https://peps.python.org/pep-0567/
                    "dataflow": lambda _dataflow, _config, _field, value: setattr(dataflow.configs, dbm_record.op.name, {"filename": value})
                }
            }
        )

    # We
    # Create class
    DBMSource = dffml.DataFlow.as_plugin(
        "DBMSource",
        dbm_source_dataflow,
        DBMSourceConfig,
        {
            "record": {
                "dataflow": dffml.DataFlow(
                    dffml.GetSingle,
                    seed=[
                        dffml.Input(
                            value=[dbm_record.op.outputs["result"].name],
                            definition=dffml.GetSingle.op.inputs["spec"],
                        ),
                    ],
                ),
            },
        }
    )

    # Run load on a single record
    print(list(dffml.noasync.load(DBMSource(filename=DBM_FILENAME), "a")))

    # TODO Run load on all records

    # TODO Update a record

    # TODO Implment DBMHandle using DataFlow.as_plugin to use filelock

.. code-block:: console
    :test:

    $ python -u dataflow_as_class_dbm_source.py
