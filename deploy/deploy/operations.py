import os
import json
import asyncio
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
    return {
        "url": payload["repository"]["clone_url"]
    }

@op(inputs={"payload":git_payload},outputs={"is_default_branch":is_default_branch})
def check_if_default_branch(payload):
    pushed_branch = payload["ref"].split("/")[-1]
    default_branch = payload["repository"]["default_branch"]
    return {
        "is_deafault_branch":(default_branch==pushed_branch)
    }

@op(inputs={"payload":git_payload},outputs={"image_tag":docker_image_tag})
def get_image_tag(payload):
    url = payload["repository"]["html_url"] # eg:-"https://github.com/username/Hello-World",
    tag = url.split("/")
    tag = f"{tag[-2]}/{tag[-1]}"
    return {"image_tag":tag}
@op(
    inputs={
        "repo":clone_git_repo.op.outputs["repo"],
        "image_tag":docker_image_tag
        },
    outputs={"image_id":docker_image_id},
    conditions=[check_if_default_branch]
)
async def docker_build_image(repo):
    # finding top most `Dockerfile`
    docker_files = await check_output("find",".","-type","f","-name","Dockerfile",cwd=repo["directory"])
    docker_file = docker_files.split("\n")[0].replace("Dockerfile","")
    #building image
    cmd_out = await check_output("docker","build",docker_file)
    image_id = cmd_out.split("Successfully built")[-1].strip()
    return {"image_id":image_id}

@op(input{"tag":docker_image_tag})
async def restart_running_containers_by_tag(tag):
    read,write = os.pipe()
    ps = await asyncio.create_subprocess_exec("docker","ps",stdout=write)
    os.close(write)
    grep = await asyncio.create_subprocess_exec("grep",tag,stdin=read,stdout=asyncio.subprocess.PIPE)
    os.close(read)
    containers = await grep.stdout.read()
    containers = containers.decode().strip().split("\n")
    containers = [ container.split(" ")[0] for container in containers if container]

    # stop running containers and get commands used to start them
    # and start it again
    cmds=[]
    for container in containers:
        # get command used to start container
        cmd = (await check_output("runlike",container)).strip()
        out = await check_output("docker","rm","-f",container)
        if not (out.strip()==container):
            print(f"out = {out}")
            print(f"container = {container}")
            raise Exception(f"Error when stopping container {container}")
        # restart containers with newly build image
        # TODO : enforce starting in detach?
        out = await check_output(*cmd.split(" "))


