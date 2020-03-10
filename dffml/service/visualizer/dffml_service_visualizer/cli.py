from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD
from dffml.util.entrypoint import entrypoint


class clfvisualizer(CMD):

    async def run(self):
        print("hello world")

"""
There will be four classes clfvisualizer2D, clfvisualizer3D, regvisualizer1D, regvisualizer2D, 
"""

@entrypoint('visualizer')
class VisualizerService(CMD):
    clfvisualizer = clfvisualizer
