import inspect
import itertools

from .types import Definition, Operation, Output


class Linker(object):
    def resolve(self, source: dict):
        definitions = {}
        operations = {}
        outputs = {}
        for name, kwargs in source.get("definitions", {}).items():
            definitions[name] = Definition(name=name, **kwargs)
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
                try:
                    kwargs[arg] = [definitions[i] for i in kwargs[arg]]
                except KeyError as error:
                    raise KeyError(
                        "Definition missing while resolving %s.%s"
                        % (name, arg)
                    ) from error
            for arg in ["inputs", "outputs"]:
                try:
                    kwargs[arg] = {
                        i: definitions[kwargs[arg][i]] for i in kwargs[arg]
                    }
                except KeyError as error:
                    raise KeyError(
                        "Definition missing while resolving %s.%s"
                        % (name, arg)
                    ) from error
            operations[name] = Operation(name=name, **kwargs)
        return definitions, operations, outputs

    def export(self, *args):
        exported = {"definitions": {}, "operations": {}}
        for operation in args:
            exported["operations"][operation.name] = operation.export()
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
        return exported
