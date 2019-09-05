import os
import uuid
import json
import pydoc
import getpass
import importlib
import configparser
import pkg_resources
from pathlib import Path

from ..util.skel import Skel
from ..util.cli.cmd import CMD
from ..version import VERSION
from ..util.skel import Skel, SkelTemplateConfig
from ..util.cli.arg import Arg
from ..util.cli.cmd import CMD
from ..base import MissingConfig
from ..util.data import traverse_config_get
from ..df.types import Input
from ..df.base import Operation
from ..df.memory import MemoryOrchestrator
from ..operation.output import GetSingle

config = configparser.ConfigParser()
config.read(Path("~", ".gitconfig").expanduser())

USER = getpass.getuser()
NAME = config.get("user", "name", fallback="Unknown")
EMAIL = config.get("user", "email", fallback="unknown@example.com")


def create_from_skel(name):
    """
    Copies samples out of skel/ and does re-naming.
    """

    class CreateCMD(CMD):

        skel = Skel()

        arg_user = Arg(
            "-user",
            help=f"Your username (default: {USER})",
            default=USER,
            required=False,
        )
        arg_name = Arg(
            "-name",
            help=f"Your name (default: {NAME})",
            default=NAME,
            required=False,
        )
        arg_email = Arg(
            "-email",
            help=f"Your email (default: {EMAIL})",
            default=EMAIL,
            required=False,
        )
        arg_description = Arg(
            "-description",
            help=f"Description of python package (default: DFFML {name} {{package name}})",
            default=None,
            required=False,
        )
        arg_target = Arg(
            "-target",
            help=f"Directory to put code in (default: same as package name)",
            default=None,
            required=False,
        )
        arg_package = Arg("package", help="Name of python package to create")

        async def run(self):
            # Set description if None
            if not self.description:
                self.description = f"DFFML {name} {self.package}"
            # Set target directory to package name if not given
            if not self.target:
                self.target = self.package
            # Extract
            self.skel.from_template(
                name,
                self.target,
                SkelTemplateConfig(
                    org=self.user,
                    package=self.package,
                    description=self.description,
                    name=self.name,
                    email=self.email,
                    dffml_version=VERSION,
                ),
            )

    return CreateCMD


class Create(CMD):
    """
    Create new models, operations, etc.
    """

    model = create_from_skel("model")
    operations = create_from_skel("operations")
    service = create_from_skel("service")
    source = create_from_skel("source")


class Link(CMD):
    """
    Create required symlinks from skel/common to the other template directories
    """

    skel = Skel()

    async def run(self):
        for plugin in self.skel.plugins():
            self.skel.create_symlinks(plugin)


class Skeleton(CMD):
    """
    Work with the skeleton directories (create service templates)
    """

    link = Link



class Run(CMD):
    """
    Run a single operation
    """

    arg_operation = Arg("operation", help="Python path to operation")

    async def run(self):
        # Lookup
        modname, qualname_separator, qualname = self.operation.partition(":")
        obj = importlib.import_module(modname)
        if qualname_separator:
            for attr in qualname.split("."):
                obj = getattr(obj, attr)
                self.logger.debug("Loaded operation: %s(%s)", attr, obj)
                return await self.run_op(attr, obj)

    def config_get(self, op, key, definition):
        # TODO De-duplicate code from dffml/base.py
        try:
            value = traverse_config_get(self.extra_config, key)
        except KeyError as error:
            raise MissingConfig("%s missing %s" % (op.name, key))
        # TODO Argparse nargs and Arg and primitives need to be unified
        if "Dict" in definition.primitive:
            # TODO handle Dict / spec completely
            self.logger.ciritical(
                "Dict / spec'd arguments are not yet completely handled"
            )
            value = json.loads(value)
        else:
            typecast = pydoc.locate(
                definition.primitive.replace("List[", "").replace("[", "")
            )
            # TODO This is a oversimplification of argparse's nargs
            if definition.primitive.startswith("List["):
                value = list(map(typecast, value))
            else:
                value = typecast(value[0])
                if typecast is str and value in ["True", "False"]:
                    raise MissingConfig("%s missing %s" % (op.name, key))
        return value

    async def run_op(self, name, opimp):
        # Create an instance of BaseConfigurable and have it parse the inputs
        # from self.extra_config. Use the op.inputs to know what we should pass
        # to config_get
        inputs = []
        for name, definition in opimp.op.inputs.items():
            try:
                inputs.append(
                    Input(
                        value=self.config_get(opimp.op, name, definition),
                        definition=definition,
                    )
                )
            except MissingConfig as error:
                error.args = (f"{opimp.op.inputs}: {error.args[0]}",)
                raise error
        # Run the operation in an orchestrator
        async with MemoryOrchestrator.basic_config(
            opimp.imp, GetSingle.imp
        ) as orchestrator:
            async with orchestrator() as octx:
                # TODO Assign a sha384 string as the random string context
                await octx.ictx.sadd(
                    str(uuid.uuid4()),
                    Input(
                        value=[
                            definition.name
                            for definition in opimp.op.outputs.values()
                        ],
                        definition=GetSingle.op.inputs["spec"],
                    ),
                    *inputs,
                )
                async for ctx, results in octx.run_operations():
                    # TODO There is probably an issue if multiple outputs have
                    # the same data type that only one will be shown
                    return results[GetSingle.op.name]

class ListEntrypoints(CMD):

    arg_entrypoint = Arg(
        "entrypoint", help="Entrypoint to list, example: dffml.model"
    )

    async def run(self):
        for entrypoint in pkg_resources.iter_entry_points(self.entrypoint):
            print(f"{entrypoint} -> {entrypoint.dist!r}")


class Entrypoints(CMD):

    _list = ListEntrypoints


class Develop(CMD):
    """
    Development utilities for hacking on DFFML itself
    """

    create = Create
    skel = Skeleton
    run = Run
    entrypoints = Entrypoints