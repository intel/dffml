DataFlows
=========

A running DataFlow is an event loop. First we'll look at terminology associated
with DataFlows. Then we'll go through the sequence of events that constitute the
running of a DataFlow. Lastly we'll go over the benefits of using DataFlows.

Terminology
-----------

- :py:class:`Operation <dffml.dfold.types.Operation>`

  - Things that will happen when the DataFlow is running. They define inputs and
    outputs. Inputs are the data they require to run, and outputs are the data
    they produce as a result.

  - Similar to a function prototype in C, an
    :py:class:`Operation <dffml.dfold.types.Operation>` only contains metadata.

- :py:class:`OperationImplementation <dffml.dfold.base.OperationImplementation>`

  - The implementation of an :py:class:`Operation <dffml.dfold.types.Operation>`.
    This is the code that gets run when we talk about "running an operation".

  - A Python function can be an
    :py:class:`OperationImplementation <dffml.dfold.base.OperationImplementation>`

- :py:class:`Input <dffml.dfold.types.Input>`

  - Data that will be given to an
    :py:class:`Operation <dffml.dfold.types.Operation>` when it runs.

- :py:class:`DataFlow <dffml.dfold.types.DataFlow>`

  - Description of how :py:class:`Operations <dffml.dfold.types.Operation>` are
    connected.

  - Defines where :py:class:`Operations <dffml.dfold.types.Operation>` should get
    their inputs from.

  - Inputs can be received from the outputs of other operations, predefined
    ``seed`` values, or anywhere else.

- :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>`

  - The runner of the DataFlow. Facilitates running of operations and manages
    input data.

  - The :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>` makes use of
    four different "Networks" and a
    :py:class:`RedundancyChecker <dffml.dfold.base.BaseRedundancyChecker>`.

    - The :py:class:`InputNetwork <dffml.dfold.base.BaseInputNetwork>` stores all
      the (:py:class:`Input <dffml.dfold.types.Input>`) data. It accepts incoming
      data and notifies the
      :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>` when there is
      new data.

    - The :py:class:`OperationNetwork <dffml.dfold.base.BaseOperationNetwork>`
      stores all :py:class:`Operations <dffml.dfold.types.Operation>` the
      :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>` knows about.

    - The :py:class:`OperationImplementationNetwork <dffml.dfold.base.BaseOperationImplementationNetwork>`
      is responsible for running an
      :py:class:`Operation <dffml.dfold.types.Operation>` with a set of
      :py:class:`Inputs <dffml.dfold.types.Input>`. A unique set of
      :py:class:`Inputs <dffml.dfold.types.Input>` for an
      :py:class:`Operation <dffml.dfold.types.Operation>` is known as a
      :py:class:`ParameterSet <dffml.dfold.base.BaseParameterSet>`.

    - The :py:class:`LockNetwork <dffml.dfold.base.BaseLockNetwork>`
      manages locking of :py:class:`Inputs <dffml.dfold.types.Input>`. This is used
      when the :py:class:`Definition <dffml.dfold.types.Definition>` of the data
      type of an :py:class:`Input <dffml.dfold.types.Input>` declares that it may
      only be used when locked.

    - The :py:class:`RedundancyChecker <dffml.dfold.base.BaseRedundancyChecker>`
      ensures that :py:class:`Operations <dffml.dfold.types.Operation>` don't get
      run with the same
      :py:class:`ParameterSet <dffml.dfold.base.BaseParameterSet>` more than once.

  - :py:class:`Operations <dffml.dfold.types.Operation>` get their inputs from
    the outputs of other :py:class:`Operations <dffml.dfold.types.Operation>`
    within the same
    :py:class:`InputSetContext <dffml.dfold.base.BaseInputSetContext>`.
    :py:class:`InputSetContexts <dffml.dfold.base.BaseInputSetContext>` create
    barriers which prevent
    :py:class:`Inputs <dffml.dfold.types.Input>` within one context from being
    combined with :py:class:`Inputs <dffml.dfold.types.Input>` within another
    context.

.. Not sure if we want this example here, no other bullet points have examples.

  In the :doc:`/examples/integration` example use case. There is a DataFlow
  which collects information on a Git repo. Each URL is used as a context,
  as well as an :py:class:`Input <dffml.dfold.types.Input>`. By using the URL
  as a context we ensure all
  :py:class:`ParameterSets <dffml.dfold.base.BaseParameterSet>` created
  only contain inputs associated with their URL. For example, this prevents
  commit hashes extracted from a downloaded repository from being used as
  as an :py:class:`Input <dffml.dfold.types.Input>` in a
  :py:class:`ParameterSet <dffml.dfold.base.BaseParameterSet>` where the
  directory of downloaded source code contains the code downloaded from a
  different URL.

What Happens When A DataFlow Runs
---------------------------------

When the :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>` starts
running a DataFlow. The following sequence of events take place.

- :py:class:`OperationImplementationNetwork <dffml.dfold.base.BaseOperationImplementationNetwork>`
  instantiates all of the
  :py:class:`OperationImplementations <dffml.dfold.base.OperationImplementation>`
  that are needed by the DataFlow.

- Our first stage is the ``Processing Stage``,  where data will be generated.

- The :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>` kicks off any
  contexts that were given to the
  :py:class:`run <dffml.dfold.base.BaseOrchestratorContext.run>` method along with
  the inputs for each context.

  - All ``seed`` :py:class:`Inputs <dffml.dfold.types.Input>` are added to each
    context.

  - All inputs for each context are added to the
    :py:class:`InputNetwork <dffml.dfold.base.BaseInputNetwork>`. This is the ``New
    Inputs`` step in the flow chart below.

- The :py:class:`OperationNetwork <dffml.dfold.base.BaseOperationNetwork>` looks at
  what inputs just arrived. It ``determines which Operations may have new
  parameter sets``. If an :py:class:`Operation <dffml.dfold.types.Operation>`
  has inputs whose possible origins include the origin of one of the inputs
  which just arrived, then it may have a new
  :py:class:`ParameterSet <dffml.dfold.base.BaseParameterSet>`.

- We ``generate Operation parameter set pairs`` by checking if there are any new
  permutations of :py:class:`Inputs <dffml.dfold.types.Input>` for an
  :py:class:`Operation <dffml.dfold.types.Operation>`. If the
  :py:class:`RedundancyChecker <dffml.dfold.base.BaseRedundancyChecker>`
  has no record of that permutation being run we create a new
  :py:class:`ParameterSet <dffml.dfold.base.BaseParameterSet>` composed of
  those :py:class:`Inputs <dffml.dfold.types.Input>`.

- We ``dispatch operations for running`` which have new
  :py:class:`ParameterSets <dffml.dfold.base.BaseParameterSet>`.

- The :py:class:`LockNetwork <dffml.dfold.base.BaseLockNetwork>` locks any
  of :py:class:`Inputs <dffml.dfold.types.Input>` which can't have multiple
  operations use them at the same time.

- The :py:class:`OperationImplementationNetwork <dffml.dfold.base.BaseOperationImplementationNetwork>`
  ``runs each operation using given parameter set as inputs``.

- The outputs of the
  :py:class:`Operation <dffml.dfold.types.Operation>` are added to the
  :py:class:`InputNetwork <dffml.dfold.base.BaseInputNetwork>` and the loop
  repeats.

- Once there are no more
  :py:class:`Operation <dffml.dfold.types.Operation>`
  :py:class:`ParameterSet <dffml.dfold.base.BaseParameterSet>` pairs
  which the
  :py:class:`RedundancyChecker <dffml.dfold.base.BaseRedundancyChecker>` knows to
  be unique, the ``Cleanup Stage`` begins.

- The ``Cleanup Stage`` contains operations which will release any underlying
  resources allocated for :py:class:`Inputs <dffml.dfold.types.Input>` generated
  during the ``Processing Stage``.

- Finally the ``Output Stage`` runs.
  :py:class:`Operations <dffml.dfold.types.Operation>` running in this stage query
  the :py:class:`InputNetwork <dffml.dfold.base.BaseInputNetwork>` to organize the
  data within it into the users desired output format.

.. TODO Auto generate this

    graph TD

    inputs[New Inputs]
    operations[Operations]
    opimps[Operation Implementations]

    ictx[Input Network]
    opctx[Operation Network]
    opimpctx[Operation Implementation Network]
    rctx[Redundency Checker]
    lctx[Lock Network]


    opctx_operations[Determine which Operations may have new parameter sets]
    ictx_gather_inputs[Generate Operation parameter set pairs]
    opimpctx_dispatch[Dispatch operation for running]
    opimpctx_run_operation[Run an operation using given parameter set as inputs]

    inputs --> ictx

    operations -->|Register With| opctx
    opimps -->|Register With| opimpctx

    ictx --> opctx_operations
    opctx --> opctx_operations

    opctx_operations --> ictx_gather_inputs
    ictx_gather_inputs --> rctx
    rctx --> |If operation has not been run with given parameter set before| opimpctx_dispatch

    opimpctx_dispatch --> opimpctx

    opimpctx --> lctx

    lctx --> |Lock any inputs that can't be used at the same time| opimpctx_run_operation

    opimpctx_run_operation --> |Outputs of Operation become inputs to other operations| inputs

.. image:: /images/dataflow_diagram.svg
    :alt: Flow chart showing how DataFlow Orchestrator works

Benifits of DataFlows
---------------------

- Modularity

  - Adding a layer of abstraction to separate the operations from their
    implementations means we focus on the logic of the application rather than
    how it's implemented.

  - Implementations are easily unit testable. They can be swapped out for
    another implementation with similar functionality. For example if you had a
    "send email" operation you could swap the implementation from sending via
    your email server to sending via a third party service.

- Visibility

  - Inputs are tracked to understand where they came from and or what sequence
    of operations generated them.

  - DataFlows can be visualized to understand where inputs can come from. What
    you see is what you get. Diagrams showing how your application works in your
    documentation will never get out of sync.

- Ease of use

  - Execute code concurrently with managed locking of
    :py:class:`Inputs <dffml.dfold.types.Input>` which require locks to be used
    safely in a concurrent environment.

    - If a resource can only be used by one operation at a time, the writer of
      the operation doesn't need concern themselves of how to prevent against
      unknown user defined operations clobbering it. The
      :py:class:`Orchestrator <dffml.dfold.base.BaseOrchestrator>` manages locking.

    - As DFFML is plugin based, this enables developers to easily write and
      publish operations without users having to worry about how various
      operations will interact with each other.

  - DataFlows can be used in many environments. They are a generic way to
    describe application logic and not tied to any particular programming
    language (currently we only have an implementation for Python, we provide
    multiple deployment options).

- Security

  - Clear trust boundaries via :py:class:`Input <dffml.dfold.types.Input>` origins
    and built in input validation enable developers to ensure that untrusted
    inputs are properly validated.

  - DataFlows are a serializeable programming language agnostic concept which
    can be validated according to any set of custom rules.
