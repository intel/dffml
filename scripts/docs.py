# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import getpass
import inspect
import argparse
import importlib
import pkg_resources
import configparser
from typing import List, Type


def traverse_get_config(target, *args):
    current = target
    last = target
    for level in args:
        last = current[level]
        current = last["config"]
    return current


MODULE_TEMPLATE = """{name}
{underline}

.. code-block:: console

    pip install {install}


"""


TEMPLATE = """{name}
{underline}

*{maintenance}*

{help}"""


def data_type_string(data_type, nargs=None):
    if nargs is not None:
        return "List of %ss" % (data_type_string(data_type).lower(),)
    if hasattr(data_type, "__func__"):
        return data_type_string(data_type.__func__)
    elif data_type is str:
        return "String"
    elif data_type is int:
        return "Integer"
    elif data_type is bool:
        return "Boolean"
    elif data_type is Type:
        return "Type"
    elif hasattr(data_type, "__qualname__"):
        name = data_type.__qualname__
        if name[::-1].startswith(".load"[::-1]):
            return name[: -len(".load")]
        return name
    else:
        return str(data_type)


def sanitize_default(default):
    if not isinstance(default, str):
        return sanitize_default(str(default))
    return default.replace(getpass.getuser(), "user")


def build_args(config):
    args = []
    for key, value in config.items():
        arg = value["arg"]
        if arg is None:
            continue
        build = ""
        build += "- %s: %s\n" % (
            key,
            data_type_string(arg.get("type", str), arg.get("nargs", None)),
        )
        if "default" in arg or "help" in arg:
            build += "\n"
        if "default" in arg:
            build += "  - default: %s\n" % (sanitize_default(arg["default"]),)
        if "help" in arg:
            build += "  - %s\n" % (arg["help"],)
        args.append(build.rstrip())
    if args:
        return "**Args**\n\n" + "\n\n".join(args)
    return False


def type_name(value):
    if inspect.isclass(value):
        return value.__qualname__
    return value


def format_op_definitions(definitions):
    for key, definition in definitions.items():
        item = "- %s: %s(type: %s)" % (
            key,
            definition.name,
            definition.primitive,
        )
        if definition.spec is not None:
            item += "\n\n"
            item += "\n".join(
                [
                    "  - %s: %s%s"
                    % (
                        name,
                        type_name(param.annotation),
                        "(default: %s)" % (param.default,)
                        if param.default is not inspect.Parameter.empty
                        else "",
                    )
                    for name, param in inspect.signature(
                        definition.spec
                    ).parameters.items()
                ]
            )
        yield item


def format_op(op):
    build = []
    build.append("**Stage: %s**\n\n" % (op.stage.value))
    if op.inputs:
        build.append(
            "**Inputs**\n\n" + "\n".join(format_op_definitions(op.inputs))
        )
    if op.outputs:
        build.append(
            "**Outputs**\n\n" + "\n".join(format_op_definitions(op.outputs))
        )
    if op.conditions:
        build.append(
            "**Conditions**\n\n"
            + "\n".join(
                [
                    "- %s: %s" % (definition.name, definition.primitive)
                    for definition in op.conditions
                ]
            )
        )
    return "\n\n".join(build)


def gen_docs(
    entrypoint: str, modules: List[str], maintenance: str = "Official"
):
    per_module = {name: [None, []] for name in modules}
    packagesconfig = configparser.ConfigParser()
    packagesconfig.read("scripts/packagesconfig.ini")
    for i in pkg_resources.iter_entry_points(entrypoint):
        cls = i.load()
        module_name = i.module_name.split(".")[0]
        if module_name not in modules:
            continue
        per_module[module_name][0] = importlib.import_module(module_name)
        doc = cls.__doc__
        if doc is None:
            doc = "No description"
        else:
            doc = inspect.cleandoc(doc)
        formatting = {
            "name": i.name,
            "underline": "~" * len(i.name),
            "maintenance": maintenance,
            "help": doc,
        }
        formatted = TEMPLATE.format(**formatting)
        if getattr(cls, "imp", False):
            cls = cls.imp
        if getattr(cls, "op", False):
            formatted += "\n\n" + format_op(cls.op)
        if getattr(cls, "args", False):
            defaults = cls.args({})
            if defaults:
                config = traverse_get_config(defaults, *cls.add_orig_label())
                formatted += "\n\n" + build_args(config)
            per_module[module_name][1].append(formatted)
    return "\n\n".join(
        [
            MODULE_TEMPLATE.format(
                **{
                    "name": name,
                    "install": name.replace("_", "-"),
                    "underline": "-" * len(name),
                }
            )
            + (
                (
                    inspect.getdoc(module) + "\n\n"
                    if inspect.getdoc(module)
                    else ""
                )
                + (
                    "\n\n".join(docs)
                    if name not in packagesconfig["NO ARGS"]
                    else ""
                )
            )
            for name, (module, docs) in per_module.items()
            if docs
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="Generate plugin docs")
    parser.add_argument("--entrypoint", help="Entrypoint to document")
    parser.add_argument("--modules", help="Modules to care about", nargs="+")
    parser.add_argument(
        "--maintenance",
        default="Official",
        help="Maintained as a part of DFFML or community managed",
    )

    parser.add_argument(
        "--care",
        default="scripts/docs/care",
        help="File with each line being: entrypoint package_name package_name...",
    )
    args = parser.parse_args()

    if getattr(args, "entrypoint", False) and getattr(args, "modules", False):
        print(gen_docs(args.entrypoint, args.modules, args.maintenance))
        return

    with open(args.care, "rb") as genspec:
        for line in genspec:
            entrypoint, modules = line.decode("utf-8").split(maxsplit=1)
            modules = modules.split()
            template = entrypoint.replace(".", "_") + ".rst"
            output = os.path.join("docs", "plugins", template)
            template = os.path.join("scripts", "docs", "templates", template)
            with open(template, "rb") as template_fd, open(
                output, "wb"
            ) as output_fd:
                output_fd.write(
                    (
                        template_fd.read().decode("utf-8")
                        + gen_docs(entrypoint, modules)
                    ).encode("utf-8")
                )


if __name__ == "__main__":
    main()
