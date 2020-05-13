import asyncio
import tempfile

from dffml import op, Definition


@op(
 inputs={
     "input_file": Definition(name="input_file", primitive="bytes"),
     "resolution": Definition(name="resolution", primitive="int"),
 },
 outputs={"output_file": Definition(name="output_file", primitive="bytes")}
)
async def convert_to_gif(input_file, resolution):
    temp_input_file = tempfile.NamedTemporaryFile(prefix="ffmpeg-",)
    temp_input_file.write(input_file)
    temp_input_file.seek(0)
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
    temp_input_file.close()
    return {"output_file": out}
