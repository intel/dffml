import os
import inspect
from typing import List

from ...port import Port
from ...source.source import Sources
from ...source.json import JSONSource
from ...source.file import FileSourceConfig
from ...model import Model
from ...base import config, field


from .arg import Arg
from .cmd import CMD, CMDConfig


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


@config
class SourcesCMDConfig(CMDConfig):
    sources: Sources = field(
        "Sources for loading and saving",
        default_factory=lambda: Sources(
            JSONSource(
                FileSourceConfig(
                    filename=os.path.join(
                        os.path.expanduser("~"), ".cache", "dffml.json"
                    )
                )
            )
        ),
        labeled=True,
    )


class SourcesCMD(CMD):

    CONFIG = SourcesCMDConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Correct type of sources list if its a list and not Sources
        if not isinstance(self.sources, Sources) and isinstance(
            self.sources, list
        ):
            self.sources = Sources(*self.sources)
        # Go through the list of sources and instantiate them with a config
        # created from loading their arguments from cmd (self).
        for i in range(0, len(self.sources)):
            if inspect.isclass(self.sources[i]):
                self.sources[i] = self.sources[i].withconfig(self.extra_config)


@config
class ModelCMDConfig(CMDConfig):
    model: Model = field(
        "Model used for ML", required=True,
    )


class ModelCMD(CMD):
    """
    Set a models model dir.
    """

    CONFIG = ModelCMDConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if inspect.isclass(self.model):
            self.model = self.model.withconfig(self.extra_config)


@config
class PortCMDConfig(CMDConfig):
    port: Port = field(
        "Port", required=True, position=0,
    )


class PortCMD(CMD):

    CONFIG = PortCMDConfig


@config
class KeysCMDConfig(CMDConfig):
    keys: List[str] = field(
        "Key used for source lookup and evaluation", required=True,
    )


class KeysCMD(CMD):

    CONFIG = KeysCMDConfig
