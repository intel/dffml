from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD
from dffml.util.entrypoint import entry_point


@entry_point("misc")
class MiscService(CMD):
    """
    Description of the DFFML related command
    """

    arg_integer = Arg(
        "-integer",
        type=int,
        help=f"Port to do nothing with",
        default=0,
        required=True,
    )

    async def run(self):
        print(f"Your integer was: {self.integer}")
