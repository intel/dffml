import asyncio
import pathlib
from dffml_feature_git.util.proc import check_output

async def restart_running_containers_by_tag(tag):
    containers = await check_output("docker","ps","--filter",f"ancestor={tag}", "--format","{{.ID}}" )
    containers = containers.strip().split("\n")

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
asyncio.run(restart_running_containers_by_tag("deploy/test"))