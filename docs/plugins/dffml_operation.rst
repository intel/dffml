Operations
==========

Operations Implementations are subclasses of
:class:`dffml.df.base.OperationImplementation`, they are functions or classes
which could do anything, make HTTP requests, do inference, etc.

They don't necessarily have to be written in Python. Although DFFML isn't quite
to the point where it can use operations written in other languages yet, it's on
the roadmap.

dffml
-----

.. code-block:: console

    pip install dffml


associate
~~~~~~~~~

*Official*

No description

**Stage: output**



**Inputs**

- spec: associate_spec(type: List[str])

**Outputs**

- output: associate_output(type: Dict[str, Any])

dffml.dataflow.run
~~~~~~~~~~~~~~~~~~

*Official*

Starts a subflow ``self.config.dataflow`` and adds ``inputs`` in it.

Parameters
----------
inputs : dict
    The inputs to add to the subflow. These should be a key value mapping of
    the context string to the inputs which should be seeded for that context
    string.

Returns
-------
dict
    Maps context strings in inputs to output after running through dataflow.

Examples
--------

>>> URL = Definition(name="URL", primitive="string")
>>>
>>> subflow = DataFlow.auto(GetSingle)
>>> subflow.definitions[URL.name] = URL
>>> subflow.seed.append(
...     Input(
...         value=[URL.name],
...         definition=GetSingle.op.inputs["spec"]
...     )
... )
>>>
>>> dataflow = DataFlow.auto(run_dataflow, GetSingle)
>>> dataflow.configs[run_dataflow.imp.op.name] = RunDataFlowConfig(subflow)
>>> dataflow.seed.append(
...     Input(
...         value=[run_dataflow.imp.op.outputs["results"].name],
...         definition=GetSingle.op.inputs["spec"]
...     )
... )
>>>
>>> async def main():
...     async for ctx, results in MemoryOrchestrator.run(dataflow, {
...         "run_subflow": [
...             Input(
...                 value={
...                     "dffml": [
...                         {
...                             "value": "https://github.com/intel/dffml",
...                             "definition": URL.name
...                         }
...                     ]
...                 },
...                 definition=run_dataflow.imp.op.inputs["inputs"]
...             )
...         ]
...     }):
...         print(results)
>>>
>>> asyncio.run(main())
{'flow_results': {'dffml': {'URL': 'https://github.com/intel/dffml'}}}

**Stage: processing**



**Inputs**

- inputs: flow_inputs(type: Dict[str,Any])

**Outputs**

- results: flow_results(type: Dict[str,Any])

**Args**

- dataflow: DataFlow

dffml.mapping.create
~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- key: key(type: str)
- value: value(type: generic)

**Outputs**

- mapping: mapping(type: map)

dffml.mapping.extract
~~~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- mapping: mapping(type: map)
- traverse: mapping_traverse(type: List[str])

**Outputs**

- value: value(type: generic)

dffml.model.predict
~~~~~~~~~~~~~~~~~~~

*Official*

No description

**Stage: processing**



**Inputs**

- features: record_features(type: Dict[str, Any])

**Outputs**

- prediction: model_predictions(type: Dict[str, Any])

**Args**

- model: Entrypoint

get_single
~~~~~~~~~~

*Official*

No description

**Stage: output**



**Inputs**

- spec: get_single_spec(type: array)

**Outputs**

- output: get_single_output(type: map)

group_by
~~~~~~~~

*Official*

No description

**Stage: output**



**Inputs**

- spec: group_by_spec(type: Dict[str, Any])

**Outputs**

- output: group_by_output(type: Dict[str, List[Any]])