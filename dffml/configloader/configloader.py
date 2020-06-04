import os
import abc
import pathlib
import contextlib
from typing import Dict, Optional, Union

from ..util.entrypoint import base_entry_point
from ..util.asynchelper import AsyncContextManagerList
from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from ..util.data import explore_directories, nested_apply


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


@base_entry_point("dffml.configloader", "config")
class BaseConfigLoader(BaseDataFlowFacilitatorObject):
    def __call__(self) -> BaseConfigLoaderContext:
        return self.CONTEXT(self)

    @classmethod
    async def load_single_file(
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

    @classmethod
    async def load_file(
        cls,
        parsers: Dict[str, "BaseConfigLoader"],
        exit_stack: contextlib.AsyncExitStack,
        path: pathlib.Path,
        *,
        base_dir: Optional[pathlib.Path] = None,
    ) -> Dict:
        async def _get_config(temp_filepath):
            if not isinstance(temp_filepath, pathlib.Path):
                temp_filepath = pathlib.Path(temp_filepath)
            config_path, loaded = await BaseConfigLoader.load_single_file(
                parsers, exit_stack, temp_filepath, base_dir=base_dir
            )
            return config_path, loaded

        async def _get_config_aux(temp_filepath):
            _, loaded = await _get_config(temp_filepath)
            return loaded

        if len(path.suffixes) >= 2 and path.suffixes[-2] == ".dirconf":
            dir_name = path.parts[-1].split(".")[0]
            dir_path = os.path.join(*(path.parts[:-1] + (dir_name,)))

            temp_conf_dict = {dir_name: dir_path}
            config_path, conf_dict = await _get_config(path)
            explored = explore_directories(temp_conf_dict)
            explored = await nested_apply(explored, _get_config_aux)
            conf_dict.update(explored[dir_name])
        else:
            config_path, conf_dict = await _get_config(path)
        return config_path, conf_dict


class ConfigLoaders(AsyncContextManagerList):
    """
    A class similar to Sources in that it will hold all the config
    loaders that get loaded as needed (based on filetype).
    """

    SINGLETON = BaseConfigLoader

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parsers: Dict[str, "BaseConfigLoader"] = {}

    async def load_file(
        self,
        filepath: Union[str, pathlib.Path],
        *,
        base_dir: Optional[pathlib.Path] = None,
    ) -> Dict:

        if not isinstance(filepath, pathlib.Path):
            filepath = pathlib.Path(filepath)
        conf_dict = await BaseConfigLoader.load_file(
            self.parsers, self.async_exit_stack, filepath, base_dir=base_dir
        )
        return conf_dict
