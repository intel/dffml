from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD, CMDConfig
from dffml.util.entrypoint import entrypoint
from dffml.base import config, field


@config
class MiscServicesConfig(CMDConfig):
    integer: int = field(
        f"Port to do nothing with", default=0, required=True,
    )


@entrypoint("misc")
class MiscService(CMD):
    """
    Description of the DFFML related command
    """

    CONFIG = MiscServicesConfig

    async def run(self):
        print(f"Your integer was: {self.integer}")
