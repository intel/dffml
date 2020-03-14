from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD
from dffml.util.entrypoint import entrypoint
from dffml.cli.ml import MLCMD


class Reg1D(MLCMD):
    async def run(self):
        pass

class Reg2D(MLCMD):
    async def run(self):
        pass

class Clf2D(MLCMD):
    async def run(self):
        pass

class Clf3D(MLCMD):
    async def run(self):
        pass


@entrypoint("visualizer")
class Visualizer(CMD):
    """
    Description of the DFFML related command
    """

    reg2D = Reg2D
    reg1D = Reg1D
    clf2D = Clf2D
    clf3D = Clf3D
