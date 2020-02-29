import pkg_resources

from ..source.source import BaseSource
from ..model import Model
from ..util.cli.cmd import CMD
from ..util.cli.cmds import SourcesCMD, ListEntrypoint


class ListRecords(SourcesCMD):
    """
    List records stored in sources
    """

    async def run(self):
        async with self.sources as sources:
            async with sources() as sctx:
                async for record in sctx.records():
                    print(record)


class ListServices(ListEntrypoint):
    """
    List installed services
    """

    async def run(self):
        for i in pkg_resources.iter_entry_points("dffml.service.cli"):
            loaded = i.load()
            if issubclass(loaded, CMD):
                self.display(loaded)


class ListSources(ListEntrypoint):
    """
    List installed sources
    """

    ENTRYPOINT = BaseSource


class ListModels(ListEntrypoint):
    """
    List installed models
    """

    ENTRYPOINT = Model


class List(CMD):
    """
    List records and installed interfaces
    """

    records = ListRecords
    sources = ListSources
    models = ListModels
    services = ListServices
