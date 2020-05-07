import asyncio
import tempfile

from dffml.df.base import op
from .definitions import *


@op(
    inputs={
        "input_file": Input_file,
        "resolution": Resolution
    },
    outputs={"output_file":Output_file},
)
async def convert_to_gif(input_file,resolution):
    print("\n\n\n\n Running cvt gif\n\n\n")
    temp_input_file = tempfile.NamedTemporaryFile()
    temp_input_file.write(input_file)
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-ss",
        "0.3",
        "-t",
        "10",
        "-i",
        temp_input_file.name,
        "-y",
        "-vf",
        f"fps=10,scale={resolution}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "-loop",
        "0",
        "-f",
        "gif",
        "pipe:1",
        stdout=asyncio.subprocess.PIPE,
    )
    out, error = await proc.communicate()

    return{
        "output_file":out
    }

