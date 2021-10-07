# Documentation: https://docs.python.org/3.8/py-modindex.html
import os
import time
import socket
import base64
import pathlib
import getpass
import tempfile
import dataclasses
import urllib.request
from typing import List, Any

# Documentation: https://github.com/koalalorenzo/python-digitalocean
import digitalocean

# Documentation: https://parallel-ssh.readthedocs.io/en/latest/
import pssh.utils
import pssh.clients
import gevent

# Documentation: https://intel.github.io/dffml/
import dffml
import dffml.cli.cli
import dffml.noasync


def print_image_slugs(manager):
    """
    Call this function to have a list of image descriptions and their slug's
    printed to the terminal.
    """
    for image in manager.get_global_images():
        print(f"{image.slug}: {image.description}")


def print_region_slugs(manager):
    """
    Call this function to have a list of data centers and their slug's printed
    to the terminal.
    """
    for region in manager.get_all_regions():
        print(f"{region.slug}: {region.name}")


def print_size_slugs(manager):
    """
    Call this function to have a list of VM sizes and their slug's printed
    to the terminal.
    """
    for size in manager.get_all_sizes():
        print(f"{size.slug:<15}", end=" ")
        # Print out the following attributes from the size object
        for attr in [
            "vcpus",
            "memory",
            "disk",
            "transfer",
            "price_monthly",
            "price_hourly",
            "regions",
        ]:
            value = getattr(size, attr)
            print(f"{attr}: {value!s:<8}", end=" ")
        print()


class EnvironmentVariableNotSetError(Exception):
    pass


@dffml.op
def get_from_env_must_have(env_var: str) -> str:
    if env_var not in os.environ:
        raise EnvironmentVariableNotSetError(env_var)
    return os.environ[env_var]


@dffml.op
def base32_decode(base32_encoded: str) -> str:
    return base64.b32decode(base32_encoded).decode()


@dffml.op
def create_temp_file_and_write_to(tempfile_contents: str) -> str:
    fd, path = tempfile.mkstemp()
    os.write(
        fd,
        tempfile_contents
        if isinstance(tempfile_contents, bytes)
        else tempfile_contents.encode(),
    )
    os.lseek(fd, 0, os.SEEK_SET)
    os.close(fd)
    return path


@dffml.op(
    inputs={"file_to_cleanup": create_temp_file_and_write_to.op.outputs["result"]},
    stage=dffml.Stage.CLEANUP,
)
def temp_file_cleanup_file(file_to_cleanup: str):
    os.unlink(file_to_cleanup)


def digitalocean_ensure_ssh_key_present(
    key_name: str, manager: digitalocean.Manager, public_ssh_key_path: pathlib.Path,
):
    """
    Make sure that the SSH public key on our system is present within our
    DigitalOcean account

    We require a pathlib.Path object used to reference the file path of the
    public key file on disk. It's in our home directory which we reference
    using the `~` character. When we use that character we MUST call
    the expanduser() method on the Path object to replace that character with
    the correct path to the home directory.

    We'll be using the private key to connect to the server. It's usually the
    same file path as the public key only without the .pub suffix
    """
    # Check if the key exists already
    for ssh_key in manager.get_all_sshkeys():
        if ssh_key.name == key_name:
            return ssh_key
    # We then read the contents of the file into a variable
    public_ssh_key_contents = public_ssh_key_path.read_text()
    # Create a digitalocean.SSHKey object. Reuse the token from the manager
    public_ssh_key = digitalocean.SSHKey(
        token=manager.token, name=key_name, public_key=public_ssh_key_contents,
    )
    # Call the create() method on the key object to create the key
    public_ssh_key.create()
    # Return the key
    return public_ssh_key


@dffml.op
def start_vms(
    project_name: str,
    digitalocean_access_token: str,
    ssh_key_name: str,
    public_ssh_key_path: str,
) -> List[str]:
    return ["localhost"]
    # Create an instance of the manager object to interact with the Digital
    # Ocean API.
    manager = digitalocean.Manager(token=digitalocean_access_token)

    # A "slug" is the unique string we use to refer to a particular VM iamge
    # Use print_image_slugs(manager) to see more options
    image_slug = "docker-20-04"
    # The region is the data center we want to run the VM in
    # Use print_region_slugs(manager) to see more options
    region_slug = "sfo2"
    # The VM size is how big of a machine we are asking for
    # Use print_size_slugs(manager) to see more options
    size_slug = "s-1vcpu-1gb"

    # The template to use for the VMs names. Use f string formating to add the
    # variables we already have defined into the name
    name_template = f"{project_name}-{region_slug}-{size_slug}"
    # The str.format(*args) method will look for any {} and replace their
    # contents with whatever ever args were passed. We need to append it after
    # we have done any f string formating so that Python doesn't try to fill the
    # empty {} at time of f string formatting. We only want it filled later when
    # we call str.format()
    name_template += "-{}"

    # The number of VMs to create
    num_vms = 1

    # Make sure we have our machine's ssh key registered with Digital Ocean
    private_ssh_key_path, public_ssh_key = digitalocean_ensure_ssh_key_present(
        ssh_key_name, manager, pathlib.Path(public_ssh_key_path),
    )

    # Create a mapping of droplet names to their objects for all VMs we have
    all_vms = {vm.name: vm for vm in manager.get_all_droplets()}

    # Create a tag name using the project name to associate the droplets with
    # this project. Spaces are not allowed
    project_tag_name = f"project:{project_name}"
    # Create a digitalocean.Tag object. Reuse the token from the manager
    project_tag = digitalocean.Tag(token=manager.token, name=project_tag_name)
    # Call the create() method on the tag object to create the tag
    project_tag.create()

    # Create a VM if it doesn't already exist
    for i in range(0, num_vms):
        # The name of this VM
        name = name_template.format(i)
        # Skip creation if it exists
        if name in all_vms:
            continue
        # Create a digitalocean.Droplet object. Reuse the token from the manager
        vm = digitalocean.Droplet(
            token=manager.token,
            name=name,
            region=region_slug,
            image=image_slug,
            size_slug=size_slug,
            ssh_keys=[public_ssh_key],
            backups=False,
            tags=[project_tag_name],
        )
        # Call the create() method on the droplet object to create the droplet
        vm.create()

    # Create a mapping of all the VMs associated with this project. Do this
    # until the mapping contains the same number of VMs that should exist
    project_vms = {
        vm.name: vm for vm in manager.get_all_droplets(tag_name=project_tag_name)
    }
    print(project_vms)
    while len(project_vms) != num_vms:
        time.sleep(1)
        project_vms = {
            vm.name: vm for vm in manager.get_all_droplets(tag_name=project_tag_name)
        }
        print(project_vms)

    # Creating VMs is finished. Now we'll ssh into the project's VMs to setup
    # the software we want running on them
    return [vm.ip_address for vm in project_vms.values()]


@dffml.op
def setup_vm_over_ssh(
    vm_ip_addresses: List[str],
    private_ssh_key_path: str,
    private_ssh_key_password: str,
    github_actor: str,
    github_token: str,
    github_repository: str,
):
    # TODO ParallelSSH is not asyncio based :( need to put it in a thread
    # The user we'll be loging in as. Different images might do this differently
    ssh_user = "root"
    # The SSH client object doesn't know what to do with a pathlib.Path object
    # if it's given one as the private key (pkey). Therefore, we need to resolve
    # the private key pathlib.Path object to find it's absolute path, the path
    # from the root directory to the file. We then need to convert it from a
    # pathlib.Path object to a string by calling the str function
    private_ssh_key_path_as_string = str(pathlib.Path(private_ssh_key_path).resolve())
    # SSH private keys are typically proctected on disk by encrypting them with
    # a password. We ask the user for their password for this key here so that
    # we can unlock the key and use it to log in to the servers.
    # Create an SSH client which we'll use to access all the VMs in parallel.
    # Specify that we want to use our private key to connect.
    client = pssh.clients.ParallelSSHClient(
        vm_ip_addresses,
        user=ssh_user,
        pkey=private_ssh_key_path_as_string,
        password=private_ssh_key_password,
    )
    # Print output of commands to terminal as they run
    pssh.utils.enable_host_logger()

    # Define a list of commands we want to run on all the hosts in parallel
    cmds = [
        # Clone the git repo
        "git clone --depth=1 https://{github_actor}:{github_token}@github.com/{github_repository} infra",
        # Run the setup script
        "bash -xe infra/setup.sh",
        # Start everything
        "bash -xe infra/up.sh",
    ]
    # Run each command on all hosts
    for cmd in cmds:
        client.run_command(cmd)
        client.join(consume_output=True)


# Override the auto created definition so that auto flow links them together
setup_vm_over_ssh.op.inputs["vm_ip_addresses"] = start_vms.op.outputs["result"]

# GitHub related environment variables
GITHUB_ENV_VARS = [
    "GITHUB_ACTOR",
    "GITHUB_TOKEN",
    "GITHUB_REPOSITORY",
]
# The environment variables we care about
ENV_VARS = [
    "DIGITALOCEAN_ACCESS_TOKEN",
    "DO_SSH_KEY_NAME",
    "DO_SSH_KEY_PASSWORD",
    "DO_SSH_KEY_PRIVATE",
    "DO_SSH_KEY_PUBLIC",
] + GITHUB_ENV_VARS
# The DataFlow
DATAFLOW = dffml.DataFlow(
    # GetMulti,
    operations={
        "get_from_env_must_have": get_from_env_must_have,
        "base32_decode": base32_decode,
        "create_temp_file_and_write_to": create_temp_file_and_write_to,
        "temp_file_cleanup_file": temp_file_cleanup_file,
        "start_vms": start_vms,
        "setup_vm_over_ssh": setup_vm_over_ssh,
    },
    seed=(
        [
            dffml.Input(
                value=env_var,
                definition=get_from_env_must_have.op.inputs["env_var"],
                origin=f"seed.env_var.{env_var}",
            )
            for env_var in ENV_VARS
        ]
    ),
)
# For each environment variable we are getting we have assigned it's own seed.
# This will allow us to choose inputs for subsequent operations based on which
# environment variable was retrieved from the environment.
DATAFLOW.flow["get_from_env_must_have"].inputs["env_var"] = [
    f"seed.env_var.{env_var}" for env_var in ENV_VARS
]
# Base32 decode the value of the DO_SSH_KEY_PRIVATE environment variable
DATAFLOW.flow["base32_decode"].inputs["base32_encoded"] = [
    [{"get_from_env_must_have": "result"}, "seed.env_var.DO_SSH_KEY_PRIVATE"]
]
# Create temporary files with keys
DATAFLOW.flow["create_temp_file_and_write_to"].inputs["tempfile_contents"] = [
    # Write the public key to the tempfile
    [{"get_from_env_must_have": "result"}, "seed.env_var.DO_SSH_KEY_PUBLIC"],
    # Write the base32 decoded private key to the tempfile
    {"base32_decode": "result"},
]
# Start the VM set the digitalocean_access_token
DATAFLOW.flow["start_vms"].inputs["digitalocean_access_token"] = [
    [{"get_from_env_must_have": "result"}, "seed.env_var.DIGITALOCEAN_ACCESS_TOKEN"]
]
# Start the VM set the ssh_key_name to the environment variable contents
DATAFLOW.flow["start_vms"].inputs["ssh_key_name"] = [
    [{"get_from_env_must_have": "result"}, "seed.env_var.DO_SSH_KEY_NAME",]
]
# Start the VM set the public_ssh_key_path to the tempfile that was not decoded
DATAFLOW.flow["start_vms"].inputs["public_ssh_key_path"] = [
    [
        {"create_temp_file_and_write_to": "result"},
        {"get_from_env_must_have": "result"},
        "seed.env_var.DO_SSH_KEY_PUBLIC",
    ]
]
# Setup the VM set the private_ssh_key_password to the env var
DATAFLOW.flow["setup_vm_over_ssh"].inputs["private_ssh_key_password"] = [
    [{"get_from_env_must_have": "result"}, "seed.env_var.DO_SSH_KEY_PASSWORD"]
]
# Setup the VM set the private_ssh_key_path to the tempfile that was base32
# decoded
DATAFLOW.flow["setup_vm_over_ssh"].inputs["private_ssh_key_path"] = [
    [{"create_temp_file_and_write_to": "result"}, {"base32_decode": "result"}]
]
# When setting up the VM use the GitHub related environment variables
for env_var in GITHUB_ENV_VARS:
    DATAFLOW.flow["setup_vm_over_ssh"].inputs[env_var.lower()] = [
        [{"get_from_env_must_have": "result"}, f"seed.env_var.{env_var}"]
    ]
# Update the dataflow
DATAFLOW.update(auto_flow=False)


def main():
    import logging

    logging.basicConfig(level=logging.DEBUG)

    for ctx, results in dffml.noasync.run(
        DATAFLOW,
        [dffml.Input(value="chadig", definition=start_vms.op.inputs["project_name"])],
    ):
        print(ctx, results)


if __name__ == "__main__":
    main()
