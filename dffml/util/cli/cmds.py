import os
import sys
import ast
import copy
import json
import asyncio
import inspect
import logging
import argparse
from typing import Optional

from ...repo import Repo
from ...port import Port
from ...feature import Feature, Features
from ...source.source import BaseSource, Sources
from ...source.json import JSONSource
from ...source.file import FileSourceConfig
from ...model import Model

from ...df.types import Operation
from ...df.base import (
    Input,
    BaseInputNetwork,
    BaseOperationNetwork,
    BaseLockNetwork,
    BaseRedundancyChecker,
    BaseOperationImplementationNetwork,
    BaseOrchestrator,
    StringInputSetContext,
)

from ...df.memory import (
    MemoryInputNetwork,
    MemoryOperationNetwork,
    MemoryLockNetwork,
    MemoryRedundancyChecker,
    MemoryOperationImplementationNetwork,
    MemoryOrchestrator,
    MemoryInputSet,
    MemoryInputSetConfig,
)

from .arg import Arg
from .cmd import CMD
from .parser import (
    list_action,
    ParseOutputSpecsAction,
    ParseInputsAction,
    ParseRemapAction,
)


class ListEntrypoint(CMD):
    """
    Subclass this with an Entrypoint to display all registered classes.
    """

    def display(self, cls):
        """
        Print out the loaded but uninstantiated class
        """
        if not cls.__doc__ is None:
            print("%s:" % (cls.__qualname__))
            print(cls.__doc__.rstrip())
        else:
            print("%s" % (cls.__qualname__))
        print()

    async def run(self):
        """
        Display all classes registered with the entrypoint
        """
        for cls in self.ENTRYPOINT.load():
            self.display(cls)


class FeaturesCMD(CMD):
    """
    Set timeout for features
    """

    arg_features = Arg(
        "-features",
        nargs="+",
        required=True,
        type=Feature.load,
        action=list_action(Features),
    )
    arg_timeout = Arg(
        "-timeout",
        help="Feature evaluation timeout",
        required=False,
        default=Features.TIMEOUT,
        type=int,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.features.timeout = self.timeout


class SourcesCMD(CMD):

    arg_sources = Arg(
        "-sources",
        help="Sources for loading and saving",
        nargs="+",
        default=Sources(
            JSONSource(
                FileSourceConfig(
                    filename=os.path.join(
                        os.path.expanduser("~"), ".cache", "dffml.json"
                    )
                )
            )
        ),
        type=BaseSource.load_labeled,
        action=list_action(Sources),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Go through the list of sources and instantiate them with a config
        # created from loading their arguments from cmd (self).
        for i in range(0, len(self.sources)):
            if inspect.isclass(self.sources[i]):
                self.sources[i] = self.sources[i].withconfig(self.extra_config)


class ModelCMD(CMD):
    """
    Set a models model dir.
    """

    arg_model = Arg(
        "-model", help="Model used for ML", type=Model.load, required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = self.model.withconfig(self.extra_config)


class PortCMD(CMD):

    arg_port = Arg("port", type=Port.load)


class KeysCMD(CMD):

    arg_keys = Arg(
        "-keys",
        help="Key used for source lookup and evaluation",
        nargs="+",
        required=True,
    )


class BaseOrchestratorCMD(CMD):
    """
    Data Flow commands
    """

    arg_orchestrator = Arg(
        "-orchestrator", type=BaseOrchestrator.load, default=MemoryOrchestrator
    )
    arg_output_specs = Arg(
        "-output-specs", nargs="+", action=ParseOutputSpecsAction, default=[]
    )
    arg_inputs = Arg(
        "-inputs",
        nargs="+",
        action=ParseInputsAction,
        default=[],
        help="Other inputs to add under each ctx (repo's src_url will "
        + "be used as the context)",
    )
    arg_repo_def = Arg(
        "-repo-def",
        default=False,
        type=str,
        help="Definition to be used for repo.src_url."
        + "If set, repo.src_url will be added to the set of inputs "
        + "under each context (which is also the repo's src_url)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = self.orchestrator.withconfig(self.extra_config)

    # Load all entrypoints which may possibly be selected. Then have them add
    # their arguments to the DataFlowFacilitator-tots command.
    @classmethod
    def add_bases(cls):
        # TODO Add args() for each loaded class as argparse arguments
        return cls
        cls = copy.deepcopy(cls)
        for base in [
            BaseInputNetwork,
            BaseOperationNetwork,
            BaseLockNetwork,
            BaseRedundancyChecker,
            BaseOperationImplementationNetwork,
            BaseOrchestrator,
        ]:
            for loaded in base.load():
                loaded.args(cls.EXTRA_CONFIG_ARGS)
        return cls


OrchestratorCMD = BaseOrchestratorCMD.add_bases()
