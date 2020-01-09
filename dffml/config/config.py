import abc
import os
import pathlib
import json
import contextlib
from typing import Dict, Any, Optional,Union

from ..util.entrypoint import base_entry_point
from ..util.asynchelper import AsyncContextManagerList
from ..base import (
    BaseConfig,
    BaseDataFlowFacilitatorObjectContext,
    BaseDataFlowFacilitatorObject,
)
from dffml.util.data import explore_directories,nested_apply


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
        # TODO If `path` has multiple extentions, for example:
        # the_config_name.dirconf.json
        # Then use the final exention as we have been above. Check the second to
        # last extention and see if it is "dirconf" if it is, then look in the
        # directory named `the_config_name` (for this example). Treat subsequent
        # directories and filenames as keys in the loaded dict value.
        # In dffml.util.data there is a `traverse_get` function, you'll need to
        # create the opisite of that function, `traverse_set` (there is already
        # a simliar function in that file).
        # Example:
        # $ tree
        # .
        # ├── the_config_name
        # │   ├── deadbeef.json
        # │   └── feed
        # │       └── face.json
        # └── the_config_name.dirconf.json
        # If load_file is passed the_config_name.dirconf.json as `path`.
        # And it's contents are
        #
        # {"hello": "there"}
        #
        # And the contents of deadbeef.json are
        #
        # {"massive": "hax"}
        #
        # And the contents of face.json are
        #
        # {"so": "secure"}
        #
        # The resulting loaded dict for a `path` of the_config_name.dirconf.json
        # should be
        #
        # {
        #   "hello": "there",
        #   "deadbeef": {
        #     "massive": "hax"
        #   },
        #   "feed": {
        #     "face": {
        #       "so": "secure"
        #     }
        #   }
        # }
        #
        # So don't worry about creating a new configloader, just make a testcase
        # which writes out that file structre to a tempdir, then calls this
        # load_file method (which you modify) and make sure that it equals the
        # example I gave above. Thanks!


class ConfigLoaders(AsyncContextManagerList):
    """
    A class similar to Sources in that it will hold all the config
    loaders that get loaded as needed (based on filetype).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parsers: Dict[str, "BaseConfigLoader"] = {}

    async def load_file(
        self,
        filepath: Union[str, pathlib.Path],
        *,
        base_dir: Optional[pathlib.Path] = None,
    ) -> Dict:

        async def _get_config(temp_filepath):
            if not isinstance(temp_filepath, pathlib.Path):
                temp_filepath = pathlib.Path(temp_filepath)
            _,loaded = await BaseConfigLoader.load_file(
                self.parsers, self.async_exit_stack,temp_filepath, base_dir=base_dir
                )
            return loaded

        if not isinstance(filepath, pathlib.Path):
            filepath = pathlib.Path(filepath)

        if( len(filepath.suffixes)>=2 and filepath.suffixes[-2]==".dirconf") :
            dir_name = filepath.parts[-1].split('.')[0]
            dir_path=os.path.join(*(filepath.parts[:-1]+(dir_name,)))

            temp_conf_dict={dir_name:dir_path}
            conf_dict = await _get_config(filepath)
            explored = explore_directories(temp_conf_dict)
            explored = await nested_apply(explored,_get_config)
            conf_dict.update(explored[dir_name])

        else:
            conf_dict =await _get_config(filepath)
        return conf_dict