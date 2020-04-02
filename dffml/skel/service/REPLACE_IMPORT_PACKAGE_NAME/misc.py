from dffml.util.cli.plugin import Plugin
from dffml.util.cli.cmd import CMD
from dffml.util.entrypoint import entrypoint


@entrypoint("misc")
class MiscService(CMD):
    """
    Description of the DFFML related command
    """

    plugin_integer = Plugin(
        "-integer",
        type=int,
        help=f"Port to do nothing with",
        default=0,
        required=True,
    )

    async def run(self):
        print(f"Your integer was: {self.integer}")
