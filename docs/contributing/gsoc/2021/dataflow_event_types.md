# Refactor of DataFlows to Include Event Type

A large part of DFFML is the concept of a DataFlow.

Chance orchestrator context run so that it yields three objects, context, event
type, results.

Currently we have a lot of code that looks like this:

```python
for ctx, results in run(dataflow, [... inputs ...]):
    print("The results of", ctx, "are", results)
```

When this project is over, those `for` loops will look like this:

```python
for ctx, event, data in run(dataflow, [... inputs ...]):
    if event == EventType.OUTPUT:
        print("The results of", ctx, "are", data)
    elif event == EventType.INPUT:
        print("An input entered network for context", ctx, ":", data)
```

The way things currently work is that the `run` function `yield`s when the
context is finished running. It `yield`s the context that was running and the
results.

We need to add another part to a data flow so we can yield `Input`s. The event
type would be `INPUT`, and in the DataFlow we should add a section for events.
In the events section for `INPUT` events we could specify when an
input should be yielded. We use the inputs section to specify which transitions
between operations should be yielded.

This will enable us to do things like running a DataFlow and not only `yield`ing
the results, but data that's moving through the network as the DataFlow is
running. This allows developers to build applications that show the progress of
a DataFlow as it's running.

## Skills

- Python
- Refactoring a large codebase
- Asyncio knowledge would be very helpful here

## Difficulty

Intermediate/Hard

## Related Readings

- https://intel.github.io/dffml/master/contributing/gsoc/2021/index.html

## Getting Started

- Read the contributing guidelines
  - https://intel.github.io/dffml/master/contributing/index.html
- Go through the quickstart
  - https://intel.github.io/dffml/master/quickstart/model.html
- Go through the data flow related docs and tutorials
  - https://intel.github.io/dffml/master/tutorials/dataflows/index.html
  - https://intel.github.io/dffml/master/examples/integration.html
  - https://intel.github.io/dffml/master/examples/shouldi.html
  - https://intel.github.io/dffml/master/examples/dataflows.html
  - https://intel.github.io/dffml/master/examples/mnist.html
  - https://intel.github.io/dffml/master/examples/flower17/flower17.html
  - https://intel.github.io/dffml/master/examples/webhook/index.html
- Read about what data flows are and how they work
  - https://intel.github.io/dffml/master/concepts/index.html#dataflows
  - https://intel.github.io/dffml/master/concepts/dataflow.html
- Come up with a basic example where the user will see inputs moving through the
  network.
  - Make it simple and include a few operations.
  - Get the DataFlow running.
- Look at the code in `dffml/df/memory.py` and understand how it relates to the
  docs covering DataFlows conceptually.
- Plan out what all needs to change within `dffml/df/memory.py` and the other
  code and examples that would change as a result.

## Potential Mentors

- [John Andersen](https://github.com/pdxjohnny)
- [Saksham Arora](https://github.com/sakshamarora1)

## Tracking and Discussion

This project is related to the following issues. Please discuss and ask
questions in the issue comments. Please also ping mentors on
[Gitter](https://gitter.im/dffml/community) when you post on the following
issues so that they are sure to see that you've commented.

- https://github.com/intel/dffml/issues/919
