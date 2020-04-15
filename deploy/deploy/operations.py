import json
from typing import List,Dict,Any

from dffml.df.base import op
from .definitions import *

from dffml_feature_git.feature.operations import clone_git_repo
from dffml_feature_git.util.proc import check_output, create, stop



@op(
    inputs = {"payload_str":git_payload_string},
    outputs= {"payload":git_payload}
)
def get_payload(payload_str:str)->Dict[str,Any]:
    payload = json.loads(payload_str)
    return {"payload":payload}

@op(
    inputs={"payload":git_payload},
    outputs={"url":clone_git_repo.op.inputs["URL"]}
)
def get_url_from_payload(payload:Dict[str,Any]):
    return {
        "url": payload["repository"]["clone_url"]
    }

@op(
    inputs={"repo":clone_git_repo.op.outputs["repo"]},
    outputs={"image_id":docker_image_id}
)
async def docker_build_image(repo):
    # finding top most `Dockerfile`
    docker_files = await check_output("find",".","-type","f","-name","Dockerfile",cwd=repo["directory"])
    docker_file = docker_files.split("\n")[0].replace("Dockerfile","")
    #building image
    cmd_out = await check_output("docker","build",docker_file)
    image_id = cmd_out.split("Successfully built")[-1].strip()
    return {"image_id":image_id}


