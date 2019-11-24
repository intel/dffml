import os
import inspect

from ...port import Port
from ...source.source import BaseSource, Sources
from ...source.json import JSONSource
from ...source.file import FileSourceConfig
from ...model import Model


from .arg import Arg
from .cmd import CMD
from .parser import list_action


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
