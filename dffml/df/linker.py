import inspect
import itertools

from .types import Definition, Operation, Output, DataFlow


class Linker(object):
    @classmethod
    def resolve(cls, source: dict):
        definitions = {}
        operations = {}
        outputs = {}
        for name, kwargs in source.get("definitions", {}).items():
            kwargs.setdefault("name", name)
            definitions[name] = Definition(**kwargs)
        sig = inspect.signature(Operation)
        for name, kwargs in source.get("operations", {}).items():
            for arg, parameter in sig.parameters.items():
                if (
                    arg != "name"
                    and not arg in kwargs
                    and parameter.default == inspect.Parameter.empty
                ):
                    # From 3.7/Lib/typing.py:
                    # "For internal bookkeeping of generic types __origin__
                    # keeps a reference to a type that was subscripted."
                    kwargs[arg] = parameter.annotation.__origin__()
            # Replaces strings referencing definitions with definitions
            for arg in ["conditions"]:
                if not arg in kwargs:
                    continue
                try:
                    kwargs[arg] = [definitions[i] for i in kwargs[arg]]
                except KeyError as error:
                    raise KeyError(
                        "Definition missing while resolving %s.%s"
                        % (name, arg)
                    ) from error
            for arg in ["inputs", "outputs"]:
                if not arg in kwargs:
                    continue
                try:
                    kwargs[arg] = {
                        i: definitions[kwargs[arg][i]["name"]] for i in kwargs[arg]
                    }
                except KeyError as error:
                    raise KeyError(
                        "Definition missing while resolving %s.%s"
                        % (name, arg)
                    ) from error
            kwargs.setdefault("name", name)
            operations[name] = Operation(**kwargs)
        return DataFlow(operations=operations)

    @classmethod
    def export(cls, dataflow: DataFlow):
        exported = {"definitions": {}, "operations": {}}
        for operation in dataflow.operations.values():
            exported["operations"][operation.instance_name] = operation.export()
            exported["definitions"].update(
                {
                    definition.name: definition.export()
                    for definition in itertools.chain(
                        operation.inputs.values(),
                        operation.outputs.values(),
                        operation.conditions,
                    )
                }
            )
        if dataflow.flow:
            exported["flow"] = dataflow.export()["flow"].copy()
        return exported
