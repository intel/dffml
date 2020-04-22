import os
import re
import json
import shlex
import asyncio
import pathlib
from typing import List, Dict, Any

from dffml.df.base import op
from .definitions import *
from .exceptions import *

from dffml_feature_git.feature.operations import clone_git_repo
from dffml_feature_git.util.proc import check_output, create, stop


@op(
    inputs={"payload": git_payload},
    outputs={"url": clone_git_repo.op.inputs["URL"]},
)
def get_url_from_payload(payload: Dict[str, Any]):
    return {"url": payload["repository"]["clone_url"]}


@op(
    inputs={"payload": git_payload},
    outputs={"is_default_branch": is_default_branch},
)
def check_if_default_branch(payload):
    pushed_branch = payload["ref"].split("/")[-1]
    default_branch = payload["repository"]["default_branch"]
    return {"is_default_branch": (default_branch == pushed_branch)}


@op(inputs={"payload": git_payload}, outputs={"image_tag": docker_image_tag})
def get_image_tag(payload):
    url = payload["repository"][
        "html_url"
    ]  # eg:-"https://github.com/username/Hello-World",
    tag = url.split("/")
    tag = f"{tag[-2]}/{tag[-1]}"
    return {"image_tag": tag}


@op(
    inputs={"tag": docker_image_tag},
    outputs={"running_containers": docker_running_containers},
)
async def get_running_containers(tag):
    containers = await check_output(
        "docker", "ps", "--filter", f"ancestor={tag}", "--format", "{{.ID}}"
    )
    containers = [
        container for container in containers.strip().split("\n") if container
    ]
    return {"running_containers": containers}


@op(
    inputs={"containers": docker_running_containers},
    outputs={"status": got_running_containers},
)
def get_status_running_containes(containers):
    return {"status": True}


@op(
    inputs={
        "repo": clone_git_repo.op.outputs["repo"],
        "image_tag": docker_image_tag,
    },
    outputs={"docker_commands": docker_commands},
)
async def parse_docker_commands(repo, image_tag):
    docker_file = next(pathlib.Path(repo.directory).rglob("Dockerfile"))
    docker_build_cmd = [
        "docker",
        "build",
        "-t",
        image_tag,
        str(docker_file.parent),
    ]
    with open(docker_file, "r") as f:
        s = f.read()

    # parsing run command from Dockerfile
    # parses lines starting with "# docker run" to line ending with "# "
    x = re.findall("(?:#[ ]*docker run )(?:.|\n)*(?:#[ ]*\n)", s)
    if not x:
        # handles case were `FROM` starts immediatly after `usage` comments,
        # without blank comment in between
        x = re.findall("((?:#[ ]*docker run )(?:.|\n)*)FROM", s)
    if not x:
        raise UsageNotFound(
            f"docker run command not found in comments in {docker_file}"
        )

    x = x[0].replace("#", "").strip()
    docker_run_cmd = shlex.split(x)

    return {
        "docker_commands": {"build": docker_build_cmd, "run": docker_run_cmd}
    }


@op(
    inputs={"docker_commands": docker_commands},
    outputs={"build_status": is_image_built},
    conditions=[is_default_branch, got_running_containers],
)
async def docker_build_image(docker_commands):
    # building image
    cmd_out = await check_output(*docker_commands["build"])
    build_status = "Successfully built" in cmd_out
    return {"build_status": build_status}


@op(
    inputs={
        "docker_commands": docker_commands,
        "containers": docker_running_containers,
    },
    conditions=[is_image_built],
    outputs={"containers": docker_restarted_containers},
)
async def restart_running_containers(docker_commands, containers):
    # if no containers are running ,start a fresh one else
    # stop running containers and start it again with the new built
    new_containers = []
    if not containers:
        out = await check_output(*docker_commands["run"])
        new_containers.append(out.strip())
        return {"containers": new_containers}

    for container in containers:
        out = await check_output("docker", "rm", "-f", container)
        if not (out.strip() == container):
            raise CannotRemoveContainer(
                f"Error when force removing container {container}"
            )
        out = await check_output(*docker_commands["run"])
        new_containers.append(out.strip())
    return {"containers": new_containers}
