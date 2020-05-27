import inspect
from typing import List

from ...port import Port
from ...source.source import Sources
from ...model import Model
from ...base import config, field


from .cmd import CMD
from ...util.config.fields import FIELD_SOURCES


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
class SourcesCMDConfig:
    sources: Sources = FIELD_SOURCES


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
class ModelCMDConfig:
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
class PortCMDConfig:
    port: Port = field("Port")


class PortCMD(CMD):

    CONFIG = PortCMDConfig


@config
class KeysCMDConfig:
    keys: List[str] = field(
        "Key used for source lookup and evaluation", required=True,
    )


class KeysCMD(CMD):

    CONFIG = KeysCMDConfig
