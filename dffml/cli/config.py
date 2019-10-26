import sys
import pathlib

from ..config.config import BaseConfigLoader
from ..config.json import JSONConfigLoader
from ..util.cli.cmd import CMD
from ..util.cli.cmd import Arg


class Convert(CMD):

    arg_original = Arg("original", help="Config to convert")
    arg_config_in = Arg(
        "-config-in",
        dest="config_in",
        help="ConfigLoader to use for importing",
        type=BaseConfigLoader.load,
        default=None,
    )
    arg_config_out = Arg(
        "-config-out",
        dest="config_out",
        help="ConfigLoader to use for exporting",
        type=BaseConfigLoader.load,
        default=JSONConfigLoader,
    )

    async def run(self):
        original_path = pathlib.Path(self.original)
        config_out = self.config_out.withconfig(self.extra_config)
        # Load input configloader
        config_in = self.config_in
        if config_in is None:
            config_type = original_path.suffix.replace(".", "")
            config_in = BaseConfigLoader.load(config_type)
        config_in = config_in.withconfig(self.extra_config)
        async with config_in as cl_in, config_out as cl_out:
            async with cl_in() as loader_in, cl_out() as loader_out:
                imported = await loader_in.loadb(original_path.read_bytes())
                sys.stdout.buffer.write(await loader_out.dumpb(imported))


class Config(CMD):

    convert = Convert
