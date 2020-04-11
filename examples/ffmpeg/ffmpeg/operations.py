import asyncio

from dffml.df.base import op
from .definitions import input_file,output_file


@op(
    inputs = {
        "input_file" : input_file,
        "output_file" : output_file
    },
    outputs = {
    }
)
async def convert_to_gif(input_file,output_file):
    # TODO
    # add start and end times in second version and rebuild using webhook
    # cleanup
    proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-ss",
            "0.3",
            "-t",
            "10",
            "-i",
            input_file,
            "-y",
            "-vf",
            "fps=10,scale=1920:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            "-loop",
            "0",
             output_file,
            stdout=asyncio.subprocess.PIPE
        )
    out, error = await proc.communicate()
    print(f'out : {out.decode("utf8")}')
    if error is not None:
        print(f'error : {error.decode("utf8")}')
