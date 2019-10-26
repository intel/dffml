import abc
import pathlib
import contextlib
from typing import Dict, Any, Optional

from ..util.entrypoint import base_entry_point
from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)


class BaseConfigLoaderContext(BaseDataFlowFacilitatorObjectContext):
    def __init__(self, parent: "BaseConfigLoader") -> None:
        super().__init__()
        self.parent = parent

    @abc.abstractmethod
    async def loadb(self, resource: bytes) -> Dict:
        """
        ConfigLoaders need to be able to return the dict representation of the
        resources they are asked to load.
        """

    @abc.abstractmethod
    async def dumpb(self, resource: Dict) -> bytes:
        """
        ConfigLoaders need to be serialize a dict representation of the
        resources they are asked to dump.
        """


@base_entry_point("dffml.config", "config")
class BaseConfigLoader(BaseDataFlowFacilitatorObject):
    def __call__(self) -> BaseConfigLoaderContext:
        return self.CONTEXT(self)

    @classmethod
    async def load_file(
        cls,
        parsers: Dict[str, "BaseConfigLoader"],
        exit_stack: contextlib.AsyncExitStack,
        path: pathlib.Path,
        *,
        base_dir: Optional[pathlib.Path] = None,
    ) -> Dict:
        """
        Load one file and load the ConfigLoader for it if necessary, using the
        AsyncExitStack provided.
        """
        filetype = path.suffix.replace(".", "")
        # Load the parser for the filetype if it isn't already loaded
        if not filetype in parsers:
            # TODO Get configs for loaders from somewhere, probably the
            # config of the multicomm
            loader_cls = cls.load(filetype)
            loader = await exit_stack.enter_async_context(
                loader_cls(BaseConfig())
            )
            parsers[filetype] = await exit_stack.enter_async_context(loader())
        # The config will be stored by its unique filepath split on dirs
        config_path = list(
            path.parts[len(base_dir.parts) :]
            if base_dir is not None
            else path.parts
        )
        # Get rid of suffix for last member of path
        if config_path:
            config_path[-1] = path.stem
        config_path = tuple(config_path)
        # Load the file
        return config_path, await parsers[filetype].loadb(path.read_bytes())
