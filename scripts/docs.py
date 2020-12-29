# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import os
import pwd
import pathlib
import inspect
import argparse
import importlib
import configparser
import pkg_resources
import unittest.mock
from typing import List, Type


def traverse_get_config(target, *args):
    current = target
    last = target
    for level in args:
        last = current[level]
        current = last["config"]
    return current


MODULE_TEMPLATE = """{tag}

{name}
{underline}

.. code-block:: console

    pip install {install}


"""


TEMPLATE = """{tag}

{name}
{underline}

*{maintenance}*

{help}"""


def data_type_string(data_type, nargs=None):
    if nargs is not None:
        return "List of %ss" % (data_type_string(data_type).lower(),)
    elif hasattr(data_type, "SINGLETON"):
        return "List of %ss" % (data_type_string(data_type.SINGLETON).lower(),)
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
    return default


def build_args(config):
    args = []
    for key, value in config.items():
        plugin = value["plugin"]
        if plugin is None:
            continue
        build = ""
        build += "- %s: %s\n" % (
            key,
            data_type_string(
                plugin.get("type", str), plugin.get("nargs", None)
            ),
        )
        if "default" in plugin or "help" in plugin:
            build += "\n"
        if "default" in plugin:
            build += "  - default: %s\n" % (
                sanitize_default(plugin["default"]),
            )
        if "help" in plugin:
            build += "  - %s\n" % (plugin["help"],)
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


def gen_docs(entrypoint: str, maintenance: str = "Official"):
    per_module = {}
    packagesconfig = configparser.ConfigParser()
    packagesconfig.read("scripts/packagesconfig.ini")
    # For some reason duplicates are showing up
    done = set()
    for i in pkg_resources.iter_entry_points(entrypoint):
        # Skip duplicates
        if i.name in done:
            continue
        cls = i.load()
        plugin_type = "_".join(cls.ENTRY_POINT_NAME)
        if plugin_type == "opimp":
            plugin_type = "operation"
        module_name = i.module_name.split(".")[0]
        per_module.setdefault(module_name, [None, "", []])
        per_module[module_name][0] = importlib.import_module(module_name)
        per_module[module_name][1] = plugin_type
        doc = cls.__doc__
        if doc is None:
            doc = "No description"
        else:
            doc = inspect.cleandoc(doc)
        formatting = {
            "tag": f".. _plugin_{plugin_type}_{module_name}_{i.name.replace('.', '_')}:",
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
            per_module[module_name][2].append(formatted)
        done.add(i.name)
    return "\n\n".join(
        [
            MODULE_TEMPLATE.format(
                **{
                    "tag": f".. _plugin_{plugin_type}_{name}:",
                    "name": name,
                    "install": name.replace("_", "-"),
                    "underline": "+" * len(name),
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
            for name, (module, plugin_type, docs) in per_module.items()
            if docs
        ]
    )


def fake_getpwuid(uid):
    return pwd.struct_passwd(
        ("user", "x", uid, uid, "", "/home/user", "/bin/bash")
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

    args = parser.parse_args()

    with unittest.mock.patch("pwd.getpwuid", new=fake_getpwuid):

        if getattr(args, "entrypoint", False):
            print(gen_docs(args.entrypoint, args.maintenance))
            return

        templates_dir = pathlib.Path("scripts", "docs", "templates")

        for template_path in templates_dir.glob("dffml_*.rst"):
            entrypoint = template_path.stem.replace("_", ".")
            pathlib.Path("docs", "plugins", template_path.name).write_text(
                template_path.read_text() + gen_docs(entrypoint)
            )


if __name__ == "__main__":
    main()
