import abc
import pathlib
import contextlib
from typing import Union, Tuple, Dict

from ..util.data import merge
from ..util.entrypoint import base_entry_point
from ..config.config import BaseConfigLoader
from .base import BaseDataFlowObjectContext, BaseDataFlowObject
from .types import DataFlow

# Filetypes to ignore (don't try to load as a config)
IGNORE = ["swp"]


class MultiCommInAtomicMode(Exception):
    """
    Raised when registration is locked.
    """


class NoConfigsForMultiComm(Exception):
    """
    Raised when no configs are found for the loaded type of multicomm
    """


class NoDataFlows(Exception):
    """
    Raised when no dataflows are found
    """


class NoDataFlowsForConfig(Exception):
    """
    Raised when no dataflows are found for a channel config
    """


class BaseCommChannelConfig:
    """
    Config structure for a communication channel. It MUST include a ``dataflow``
    parameter.
    """


class BaseMultiCommContext(BaseDataFlowObjectContext, abc.ABC):
    """
    Abstract Base Class for mutlicomm contexts
    """

    def __init__(self, parent: "BaseMultiComm") -> None:
        self.parent = parent

    @abc.abstractmethod
    async def register(self, config: BaseCommChannelConfig) -> None:
        """
        Register a communication channel with the multicomm context.
        """

    @abc.abstractmethod
    def register_config(self) -> BaseCommChannelConfig:
        """
        Return the config object to be passed to the resigter method
        """

    def _iter_configs(self, directory: pathlib.Path) -> Dict:
        """
        Yield pathlib.Path objects for each relevant config file. Ignore some
        filetypes.
        """
        for path in directory.rglob("*"):
            if path.suffix.replace(".", "") in IGNORE:
                continue
            yield path

    async def register_directory(
        self, directory: Union[pathlib.Path, str]
    ) -> None:
        """
        Register all configs found in a directory
        """
        # Get the config class for this multicomm
        config_cls: BaseCommChannelConfig = self.register_config()
        # For entering ConfigLoader contexts
        async with contextlib.AsyncExitStack() as exit_stack:
            # Configs for this multicomm
            mc_configs: Dict[Tuple, Union[Dict, BaseCommChannelConfig]] = {}
            df_configs: Dict[Tuple, DataFlow] = {}
            # Convert to pathlib object if not already
            if not isinstance(directory, pathlib.Path):
                directory = pathlib.Path(directory)
            # Load config loaders we'll need as we see their file types
            parsers: Dict[str, BaseConfigLoader] = {}
            # Grab all files containing BaseCommChannelConfigs. Each entry is a
            # BaseCommChannelConfig. However, we don't have its dataflow
            # property. Since that is stored in a separate directory
            mc_dir = pathlib.Path(directory, "mc", self.ENTRY_POINT_LABEL)
            if not mc_dir.is_dir():
                raise NoConfigsForMultiComm(f"In {mc_dir!s}")
            for path in self._iter_configs(mc_dir):
                config_path, config = await BaseConfigLoader.load_file(
                    parsers, exit_stack, path, base_dir=mc_dir
                )
                mc_configs[config_path] = config
            # Grab all files containing DataFlows
            df_dir = pathlib.Path(directory, "df")
            if not df_dir.is_dir():
                raise NoDataFlows(f"In {df_dir!s}")
            # Load all the DataFlows
            for path in self._iter_configs(df_dir):
                config_path, config = await BaseConfigLoader.load_file(
                    parsers, exit_stack, path, base_dir=df_dir
                )
                df_configs[config_path] = config
                # Now that we have all the dataflow, add it to its respective
                # multicomm config
                mc_configs[config_path]["dataflow"] = config
            # Load all overrides
            override_dir = pathlib.Path(directory, "override")
            for path in self._iter_configs(override_dir):
                config_path, config = await BaseConfigLoader.load_file(
                    parsers, exit_stack, path, base_dir=override_dir
                )
                if not config_path in df_configs:
                    self.logger.info(
                        "Overriding non-existent DataFlow: %s", config_path
                    )
                    df_configs[config_path] = config
                else:
                    merge(df_configs[config_path], config)
            # Instantiate all configs and register them
            for config_path in mc_configs.keys():
                # Assign dataflow to its respective channel config
                if not config_path in df_configs:
                    raise NoDataFlowsForConfig(config_path)
                mc_configs[config_path]["dataflow"] = df_configs[config_path]
                # Finally, turn the dict into an object and register it
                mc_configs[config_path] = config_cls._fromdict(
                    **mc_configs[config_path]
                )
                await self.register(mc_configs[config_path])


@base_entry_point("dffml.mutlicomm", "mc")
class BaseMultiComm(BaseDataFlowObject):
    """
    Abstract Base Class for mutlicomms
    """
