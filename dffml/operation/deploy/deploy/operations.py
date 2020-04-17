import os
import json
import asyncio
import pathlib
from typing import List,Dict,Any

from dffml.df.base import op
from .definitions import *
from .exceptions import CannotRemoveContainer

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
    print(f" \n\n get_url_from_payload {payload} ")
    return {
        "url": payload["repository"]["clone_url"]
    }

@op(inputs={"payload":git_payload},outputs={"is_default_branch":is_default_branch})
def check_if_default_branch(payload):
    pushed_branch = payload["ref"].split("/")[-1]
    default_branch = payload["repository"]["default_branch"]
    print(f" is_default_branch:{default_branch==pushed_branch} ")
    return {
        "is_default_branch":(default_branch==pushed_branch)
    }

@op(inputs={"payload":git_payload},outputs={"image_tag":docker_image_tag})
def get_image_tag(payload):
    url = payload["repository"]["html_url"] # eg:-"https://github.com/username/Hello-World",
    tag = url.split("/")
    tag = f"{tag[-2]}/{tag[-1]}"
    print(f"image_tag:{tag} ")
    return {"image_tag":tag}

@op(
    inputs={"tag":docker_image_tag},
    outputs={"running_containers":docker_running_containers}
)
async def get_running_containers(tag):
    containers = await check_output("docker","ps","--filter",f"ancestor={tag}", "--format","{{.ID}}" )
    containers =[container for container in containers.strip().split("\n") if container ]
    print(f"running containers : {containers}\n")
    return {
        "running_containers":containers
            }

@op(inputs={"containers":docker_running_containers},outputs={"status":got_running_containers})
def get_status_running_containes(containers):
    print(f"Got running containers : {containers} : returning true")
    return{
        "status":True
    }

@op(
    inputs={
        "repo":clone_git_repo.op.outputs["repo"],
        "image_tag":docker_image_tag
        },
    outputs={"build_status":is_image_built},
    conditions=[is_default_branch,got_running_containers]
)
async def docker_build_image(repo,image_tag):
    print(f"running docker build image")
    # finding top most `Dockerfile`
    print(f"\n\n repo : {repo}\n\n")
    docker_file = next(pathlib.Path(repo.directory).rglob("Dockerfile"))
    docker_file = str(docker_file.parents[0])
    #building image
    cmd_out = await check_output("docker","build","-t",image_tag,docker_file)
    build_status = "Successfully built" in cmd_out
    print(f"cmd _out : {cmd_out}")
    return {"build_status":build_status}

@op(
    inputs={"tag":docker_image_tag,"containers":docker_running_containers},
    conditions = [is_image_built],
    outputs={}
    )
async def restart_running_containers_by_tag(tag,containers):
    # stop running containers and get commands used to start them
    # and start it again
    cmds=[]
    for container in containers:
        # get command used to start container
        cmd = (await check_output("runlike",container)).strip()
        print(f"Running : {cmd}")
        out = await check_output("docker","rm","-f",container)
        if not (out.strip()==container):
            print(f"out = {out}")
            print(f"container = {container}")
            raise Exception(f"Error when stopping container {container}")
        # restart containers with newly build image
        # TODO : enforce starting in detach?
        out = await check_output(*cmd.split(" "))
        print(f"Out : {out}")


