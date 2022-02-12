"""
Our goal is to run a dataflow where each context is run via an ssh command.

TODO
****

- Change approach to the following

    - https://docs.python.org/3/library/zipapp.html#creating-standalone-applications-with-zipapp

.. code-block:: console

    $ dffml service dev create blank myapp

Put all the code in myapp. Also cache it's creation in
``~/.cache/dffml/df/ssh/myapp``.

We'd want to install dffml in there.

.. code-block:: console

    $ python -m pip install -r requirements.txt --target myapp
    $ rm myapp/*.dist-info

For Linux

.. code-block:: console

    $ python -m zipapp -p '/usr/bin/env python' myapp

For Windows

.. code-block:: console

    $ python -m zipapp -p 'C:\Python36\python.exe' myapp

Running

.. code-block:: console

    $ cat myapp.pyz | ssh "$USER@$HOST" python -c "os,sys,tempfile,atexit,functools,shutil,subprocess,pathlib=list(map(__import__,'os,sys,tempfile,atexit,functools,shutil,subprocess,pathlib'.split(',')));tempdir=tempfile.mkdtemp();atexit.register(functools.partial(shutil.rmtree,tempdir));target_path=pathlib.Path(tempdir,'dffml-remote-exec.pyz');target_path.write_bytes(sys.stdin.buffer.read());subprocess.check_call([sys.executable,target_path.name],cwd=tempdir)"

Workaround for issue with importlib.resources.open_binary and ``.pyz`` files.

.. code-block:: console

    $ tar -C ~/.cache/dffml/df/ssh/myapp/ -c --sort=name --mtime="2015-10-21 00:00Z" --owner=0 --group=0 --numeric-owner --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime . | ssh "$USER@$HOST" python -uc "io,os,sys,json,tempfile,atexit,functools,shutil,subprocess,pathlib,tarfile,operator=list(map(__import__,'io,os,sys,json,tempfile,atexit,functools,shutil,subprocess,pathlib,tarfile,operator'.split(',')));tempdir=tempfile.mkdtemp();atexit.register(functools.partial(shutil.rmtree,tempdir));tarfile_obj=tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r');env_tarinfo=tarfile_obj.getmember('./env.json');env=json.loads(tarfile_obj.extractfile(env_tarinfo).read().decode());members=list(filter(functools.partial(operator.ne,env_tarinfo),tarfile_obj.getmembers()));tarfile_obj.extractall(path=tempdir,members=members);subprocess.check_call([sys.executable,'-u','-m','myapp'],cwd=tempdir,env={**os.environ,**env})"
"""
import os
import sys
import enum
import json
import uuid
import pathlib
import tarfile
import tempfile
import textwrap
import contextlib
import dataclasses
import asyncio.subprocess
from typing import AsyncIterator, Tuple, Dict, Any, List, Callable

from ..high_level.dataflow import run
from .types import DataFlow, Definition, Input
from .base import (
    BaseOrchestrator,
    BaseContextHandle,
    BaseInputNetwork,
    BaseOperationNetwork,
    BaseLockNetwork,
    BaseOperationImplementationNetwork,
    BaseRedundancyChecker,
)
from .memory import (
    MemoryOrchestratorConfig,
    MemoryOrchestratorContext,
    MemoryOrchestrator,
    MemoryInputNetwork,
    MemoryOperationNetwork,
    MemoryLockNetwork,
    MemoryOperationImplementationNetwork,
    MemoryRedundancyChecker,
    MEMORYORCHESTRATORCONFIG_MAX_CTXS,
)
from .kubernetes_output_server import server_socket_unix_stream, read_messages
from ..operation.output import GetSingle, get_single_spec
from ..base import config, field
from ..util.crypto import secure_hash
from ..util.data import export
from ..util.os import chdir
from ..util.entrypoint import entrypoint
from ..util.asynchelper import concurrently
from ..util.subprocess import (
    run_command,
    run_command_events,
    exec_subprocess,
    Subprocess,
)
from ..util.internal import load_dataflow_from_configloader

# TODO Use importlib.resources instead of reading via pathlib
python_code: str = pathlib.Path(__file__).parent.joinpath(
    "kubernetes_execute_pickled_dataflow_with_inputs.py"
).read_text()
output_server: str = pathlib.Path(__file__).parent.joinpath(
    "kubernetes_output_server.py"
).read_text()


@config
class SSHOrchestratorConfig:
    hostname: str
    workdir: pathlib.Path = field(
        "Container build context and working directory for running container",
        default=None,
    )
    no_venv: bool = field(
        "Do not create venv on the target", default=False,
    )
    no_dffml: bool = field(
        "Do not add local version of dffml to created virtual environment",
        default=False,
    )
    python: str = field(
        "Remote version of python to use",
        default=f"python{sys.version_info.major}.{sys.version_info.minor}",
    )
    keep_tempdirs: bool = field(
        "Do not remove the temporary directory created", default=False,
    )
    prerun: DataFlow = field(
        "DataFlow run before running each context's DataFlow", default=None,
    )
    binary: str = field(
        "ssh binary to use (path or name of binary)", default="ssh",
    )
    args: bool = field(
        "Arguments to ssh binary", default_factory=lambda: [],
    )
    # Avoid "non default argument followed default argument" exception on
    # hostname having no default
    input_network: BaseInputNetwork = field(
        "Input network to use", default_factory=lambda: MemoryInputNetwork()
    )
    operation_network: BaseOperationNetwork = field(
        "Operation network to use",
        default_factory=lambda: MemoryOperationNetwork(),
    )
    lock_network: BaseLockNetwork = field(
        "Lock network to use", default_factory=lambda: MemoryLockNetwork()
    )
    opimp_network: BaseOperationImplementationNetwork = field(
        "Operation implementation network to use",
        default_factory=lambda: MemoryOperationImplementationNetwork(),
    )
    rchecker: BaseRedundancyChecker = field(
        "Redundancy checker to use",
        default_factory=lambda: MemoryRedundancyChecker(),
    )
    # Maximum number of contexts to run concurrently
    max_ctxs: int = MEMORYORCHESTRATORCONFIG_MAX_CTXS


class SSHOrchestratorContext(MemoryOrchestratorContext):
    """
    The SSHOrchestratorContext will kick off each context within a
    pod. We json the dataflow and the inputs, make them secrets, and expose
    those as files. To run the dataflow we unpickle the dataflow and inputs and
    execute with the MemoryOrchestrator.
    """

    def __init__(
        self,
        config: "MemoryOrchestratorContextConfig",
        parent: "SSHOrchestrator",
    ) -> None:
        super().__init__(config, parent)
        self.ssh = [
            self.parent.config.binary,
            *self.parent.config.args,
            self.parent.config.hostname,
        ]

    @contextlib.asynccontextmanager
    async def create_temporary_directory_on_target(self):
        with tempfile.NamedTemporaryFile() as fileobj:
            # TODO(security) Aduit default security settings of mktemp -d
            await run_command(
                [
                    *self.ssh,
                    "mktemp",
                    "-d",
                    "--tmpdir",
                    "tmp.dffml.ssh.XXXXXXXXXX",
                ],
                stdout=fileobj,
                logger=self.logger,
            )
            fileobj.seek(0)
            target_tempdir = fileobj.read().decode().strip()
        try:
            yield target_tempdir
        finally:
            if not self.parent.config.keep_tempdirs:
                await run_command(
                    [*self.ssh, "rm", "-rf", target_tempdir],
                    logger=self.logger,
                )

    async def tar_scp(self, src: str, dst: str, root: str = None):
        """
        Copy a file to the target using tar
        """
        with tempfile.TemporaryDirectory() as tempdir:
            # Path object for tempdir
            tempdir_path = pathlib.Path(tempdir)
            # Create an archive to hold the data from the source
            source_archive_path = tempdir_path.joinpath("source.tar.gz")
            with tarfile.open(source_archive_path, mode="x:gz") as tarobj:
                sources = [src]
                if isinstance(src, list):
                    sources = src
                for source in sources:
                    source_path = pathlib.Path(source)
                    if source_path.is_dir():
                        with chdir(source_path):
                            tarobj.add(".")
                    else:
                        tarobj.add(source_path)
            # Create a new empty temporary directory on the target
            async with self.create_temporary_directory_on_target() as target_tempdir:
                # stdin= requires file object with valid .fileno()
                with open(source_archive_path, "rb") as source_fileobj:
                    await run_command(
                        self.ssh + [f"cat > {target_tempdir}/source.tar.gz"],
                        stdin=source_fileobj,
                        logger=self.logger,
                    )
                # Run extraction
                await run_command(
                    [
                        *self.ssh,
                        self.parent.config.python,
                        "-m",
                        "tarfile",
                        "-ve",
                        f"{target_tempdir}/source.tar.gz",
                        str(dst),
                    ],
                    logger=self.logger,
                )

    async def run_operations_for_ctx(
        self, ctx: BaseContextHandle, *, strict: bool = True
    ) -> AsyncIterator[Tuple[BaseContextHandle, Dict[str, Any]]]:
        """
        We want to take all inputs until there are no more and start the
        dataflow as a job.

        In the future we could potentially use InputNetworks to continue
        forwarding inputs to the dataflow running in the pod.
        """
        # String representing the context we are executing operations for
        ctx_str = (await ctx.handle()).as_string()
        # Collect all initial inputs into a list to pass to ssh
        # TODO Do not collect initial inputs if we have the ability create a job
        # that can talk to this orchestrator via an InputNetwork.
        inputs: List[Input] = []
        # Track if there are more inputs
        more = True
        while more:
            more, new_input_sets = await self.ictx.added(ctx)
            for (unvalidated_input_set, new_input_set,) in new_input_sets:
                inputs.extend(
                    [x async for x in unvalidated_input_set.inputs()]
                )
                inputs.extend([x async for x in new_input_set.inputs()])
        inputs = export(inputs)
        self.logger.debug(
            "[%s]: collected initial input set: %s", ctx_str, inputs,
        )
        self.logger.debug(
            "[%s]: dataflow: %s", ctx_str, self.config.dataflow.export(),
        )

        async with self.create_temporary_directory_on_target() as target_tempdir:
            with tempfile.TemporaryDirectory() as tempdir:
                # Create temporary directory pathlib object
                tempdir_path = pathlib.Path(tempdir)
                # Write out the dataflow
                dataflow_path = tempdir_path.joinpath("dataflow.json")
                dataflow_path.write_text(
                    json.dumps(self.config.dataflow.export())
                )
                # Write out the inputs
                inputs_path = tempdir_path.joinpath("inputs.json")
                inputs_path.write_text(json.dumps(inputs))
                # Write out the Python code to execute the dataflow
                execute_pickled_dataflow_with_inputs_path = tempdir_path.joinpath(
                    "execute_pickled_dataflow_with_inputs.py"
                )
                execute_pickled_dataflow_with_inputs_path.write_text(
                    python_code
                )
                # Write out the Python code to execute the dataflow
                kubernetes_output_server_path = tempdir_path.joinpath(
                    "kubernetes_output_server.py"
                )
                kubernetes_output_server_path.write_text(output_server)
                # Write out the prerun dataflow
                prerun_dataflow_path = tempdir_path.joinpath(
                    "prerun-dataflow.json"
                )
                prerun = DataFlow()
                if self.parent.config.prerun is not None:
                    prerun = self.parent.prerun
                prerun_dataflow_path.write_text(json.dumps(prerun.export()))
                # Copy over the tempdir
                await self.tar_scp(tempdir, target_tempdir)
                if (
                    self.parent.config.workdir is not None
                    and self.parent.config.workdir.is_dir()
                ):
                    # Copy over the workdir
                    await self.tar_scp(
                        self.parent.config.workdir.resolve(),
                        f"{target_tempdir}/workdir",
                    )
                else:
                    await run_command(
                        [*self.ssh, "mkdir", f"{target_tempdir}/workdir"],
                        logger=self.logger,
                    )
                # Create the venv
                venv_env_var = ""
                if not self.parent.config.no_venv:
                    target_venv = f"{target_tempdir}/.venv"
                    venv_env_vars = f"VIRTUALENV={target_tempdir}/.venv PATH={target_tempdir}/.venv/bin/:$PATH"
                    await run_command(
                        self.ssh
                        + [
                            f"{self.parent.config.python} -m venv {target_venv}"
                        ],
                        logger=self.logger,
                    )
                    # Copy dffml
                    if not self.parent.config.no_dffml:
                        async for _event, result in run_command_events(
                            [
                                *self.ssh,
                                self.parent.config.python,
                                "-c",
                                "'import sys; print(str(sys.version_info.major) + \".\" + str(sys.version_info.minor))'",
                            ],
                            logger=self.logger,
                            events=[Subprocess.STDOUT],
                        ):
                            remote_python_major_minor = result.decode().strip()
                        with chdir(
                            pathlib.Path(__file__).parents[2].resolve()
                        ):
                            try:
                                import importlib.metadata as importlib_metadata
                            except:
                                import importlib_metadata
                            # NOTE Need to run $ python setup.py egg_info for
                            # files()
                            dffml_files = [
                                filename
                                for filename in importlib_metadata.files(
                                    "dffml"
                                )
                                if str(filename).startswith("dffml")
                            ]
                            await self.tar_scp(
                                dffml_files,
                                f"{target_venv}/lib/python{remote_python_major_minor }/site-packages/",
                            )
                # Local UNIX socket receiving output
                # Start output server
                output_socket = tempdir_path.joinpath("output.sock")
                target_output_socket = f"{target_tempdir}/output.sock"
                # Event used to stop listening UNIX server collecting output
                stop = asyncio.Event()
                # Execute the dataflow
                command: List[str] = [
                    *self.ssh,
                    "-R",
                    f"{target_output_socket}:{output_socket}",
                    f"cd {target_tempdir}/workdir && {venv_env_vars} DATAFLOW={target_tempdir}/prerun-dataflow.json INPUTS='' OUTPUT='' {self.parent.config.python} -u {target_tempdir}/execute_pickled_dataflow_with_inputs.py && {venv_env_vars} DATAFLOW={target_tempdir}/dataflow.json INPUTS={target_tempdir}/inputs.json OUTPUT={target_output_socket} {self.parent.config.python} -u {target_tempdir}/execute_pickled_dataflow_with_inputs.py",
                ]
                self.logger.debug("command: %r", command)
                # Wait for both the server to accept a new connection and for
                # the dataflow to finish running. If we don't wait on both at
                # the same time we risk not catching the exception if something
                # goes wrong
                accept_unix = (
                    server_socket_unix_stream(
                        str(output_socket), stop
                    ).__aiter__()
                ).__anext__
                work = {
                    asyncio.create_task(
                        run_command(
                            command, logger=self.logger, log_cmd_event=False
                        )
                    ): "dataflow",
                    asyncio.create_task(accept_unix()): "accept_unix",
                }

                async for event, result in concurrently(work):
                    # We don't need to handle the dataflow event, which is the
                    # completion of the running dataflow via the ssh command.
                    # The client flushes the write, and closes the socket, then
                    # the process exits. The connection to the client will be
                    # then lost as the ssh connection dies. Hopefully the UNIX
                    # server reads all the data that was sent without raising
                    # that the connection was dropped. We don't handle the
                    # dataflow event because it has no output, we only include
                    # it so that if it raises an exception we aren't ignoring it
                    if event == "accept_unix":
                        reader, writer = result
                        async for message in read_messages(reader, writer):
                            # Read one message for now
                            # TODO We need to think about when there are
                            # multiple contexts this orchestrator will need to
                            # keep this output open until the rest have
                            # completed.
                            stop.set()
                            try:
                                # Parse output data
                                results = json.loads(message)
                            except json.decoder.JSONDecodeError as e:
                                raise Exception(
                                    f"output server message JSON decode failed: {message}"
                                ) from e
                            # Return results for this context
                            return ctx, results


@entrypoint("ssh")
class SSHOrchestrator(MemoryOrchestrator):
    r"""
    Run each context within a Kubernetes job

    Examples
    --------

    You'll need a Personal Access Token to be able to make calls to GitHub's
    API. You can create one by following their documentation.

    - https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

    When it presents you with a bunch of checkboxes for different "scopes" you
    don't have to check any of them, unless you want to access your own private
    repos, then check the repos box.

    .. code-block:: console

        $ export GITHUB_TOKEN=<paste your personal access token here>

    You've just pasted your token into your terminal so it will likely show up
    in your shell's history. You might want to either remove it from your
    history, or just delete the token on GitHub's settings page after you're
    done with this example.

    Create a directory where we'll store all of the operations (Python functions)
    we'll use to gather project data / metrics.

    .. code-block:: console
        :test:

        $ mkdir operations/

    Make it a Python module by creating a blank ``__init__.py`` file in it.

    .. code-block:: console
        :test:

        $ touch operations/__init__.py

    Write a Python function which returns an object representing a GitHub repo.
    For simplicity of this tutorial, the function will take the token from the
    environment variable we just set.

    **operations/gh.py**

    .. literalinclude:: /../examples/innersource/swportal/operations/gh.py
        :test:
        :filepath: operations/gh.py

    You'll notice that we wrote a function, and then put an ``if`` statement. The
    ``if`` block let's us only run the code within the block when the script is run
    directly (rather than when included via ``import``).

    If we run Python on the script, and pass an org name followed by a repo name,
    our ``if`` block will run the function and print the raw data of the repsonse
    received from GitHub, containing a bunch of information about the repo.

    You'll notice that the data being output here is a superset of the data we'd see
    for the repo in the ``repos.json`` file. Meaning we have all the required data
    and more.

    .. code-block:: console
        :test:

        $ python operations/gh.py intel dffml
        {'allow_auto_merge': False,
         <... output clipped ...>
         'full_name': 'intel/dffml',
         <... output clipped ...>
         'html_url': 'https://github.com/intel/dffml',
         <... output clipped ...>
         'watchers_count': 135}

    We're going to create a Python script which will use all the operations we've
    written.

    We need to download the ``repos.json`` file from the previous example so
    that we know what fields our DataFlow should output.

    .. code-block:: console
        :test:

        $ curl -fLo repos.json.bak https://github.com/SAP/project-portal-for-innersource/raw/main/repos.json

    First we declare imports of other packages.

    **dataflow.py**

    .. literalinclude:: /../examples/innersource/swportal/dataflow.py
        :test:
        :filepath: dataflow.py
        :lines: 1-6

    Then we import our operations.

    **dataflow.py**

    .. literalinclude:: /../examples/innersource/swportal/dataflow.py
        :test:
        :filepath: dataflow.py
        :lines: 12-13

    Finally we define our dataflow.

    **dataflow.py**

    .. literalinclude:: /../examples/innersource/swportal/dataflow.py
        :test:
        :filepath: dataflow.py
        :lines: 15-81

    We export the dataflow for use with the CLI, HTTP service, etc.

    .. code-block:: console
        :test:

        $ dffml service dev export dataflow:dataflow | tee dataflow.json

    You'll need a Personal Access Token to be able to make calls to GitHub's
    API. You can create one by following their documentation.

    - https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

    When it presents you with a bunch of checkboxes for different "scopes" you
    don't have to check any of them, unless you want to access your own private
    repos, then check the repos box.

    .. code-block:: console

        $ export GITHUB_TOKEN=<paste your personal access token here>

    You've just pasted your token into your terminal so it will likely show up
    in your shell's history. You might want to either remove it from your
    history, or just delete the token on GitHub's settings page after you're
    done with this example.

    We can pass a dataflow with ``prerun`` to be executed before the dataflow is
    run for each context in a seperate OS process.

    We need to install PyGithub which is not in the container image we are using
    by default. Therefore it needs to run within the container which will run
    the dataflow before the dataflow is executed.

    **prerun_operations.py**

    .. code-block:: console
        :test:
        :filepath: prerun_operations.py

        import sys
        import asyncio
        import subprocess
        from typing import List


        async def pip_install(self, packages: List[str]) -> List[str]:
            # await (await asyncio.create_subprocess_exec(
            #     sys.executable, "-m", "pip", "install", *packages,
            # )).wait()
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *packages]
            )
            return packages

    .. code-block:: console
        :test:

        $ dffml dataflow create \
            -inputs \
                PyGithub,=prerun_operations:pip_install.inputs.packages \
                prerun_operations:pip_install.outputs.result,=get_single_spec \
            -- \
                prerun_operations:pip_install \
                get_single \
            | tee prerun.json
        $ dffml dataflow diagram -stage processing -- prerun.json

    We can run the dataflow using the DFFML command line interface rather than
    running the Python file.

    Execute in kubernetes (ssh default context will be used)

    .. code-block:: console

        $ dffml dataflow run records set \
            -log debug \
            -dataflow dataflow.json \
            -config \
                "$GITHUB_TOKEN='operations.gh:github_get_repo'.token" \
            -orchestrator ssh \
            -orchestrator-hostname localhost \
            -orchestrator-workdir . \
            -orchestrator-prerun prerun.json \
            -record-def "github.repo.url" \
            -keys \
              https://github.com/intel/dffml

    We can execute dataflow the from Python too

    **dataflow.py**

    .. code-block:: python
        :test:
        :filepath: dataflow.py

        import os
        import pprint
        import logging

        logging.basicConfig(level=logging.DEBUG)

        dataflow.configs[github_get_repo.op.name] = GitHubGetRepoConfig(
            token=os.environ["GITHUB_TOKEN"],
        )

        orchestrator = dffml.SSHOrchestrator(
            hostname="localhost",
            workdir=os.getcwd(),
            prerun="prerun.json",
        )

        async def main():
           async for ctx, results in dffml.run(
               dataflow,
               {
                   "dffml": [
                       dffml.Input(
                           value="https://github.com/intel/dffml",
                           definition=dataflow.definitions["github.repo.url"],
                       ),
                   ],
               },
               orchestrator=orchestrator,
           ):
               pprint.pprint(results)

        asyncio.run(main())

    The same execution using Python

    .. code-block:: console

        $ python dataflow.py

    We may wish to modify the contents of the YAML files the orchestrator
    applies to the cluster to launch jobs before they are applied.

    We can pass a dataflow with ``preapply`` to be executed before each
    ``ssh apply``. Let's write some operations and create a dataflow.

    **TODO** Make preapply a nested dataflow where the operation is the running
    of the CGI server. Nest it in another dataflow which modifies the yaml to
    add the ambassador which then runs the inner dataflow for the server.

    **preapply_operations.py**

    .. code-block:: console
        :test:
        :filepath: preapply_operations.py

        import yaml

        def add_ambassador(contents: str) -> str:
            doc = yaml.safe_load(contents)
            doc["spec"]["template"]["spec"]["containers"].append({
                "name": "ambassador",
                "image": "intelotc/dffml:latest",
                "command": [
                    "echo", "Hello Ambassador",
                ],
                "env": [
                    {"name": "DIRECTORY", "value": "/mount"},
                ],
                "ports": [
                    {"containerPort": 8080},
                ],
            })
            return yaml.dump(doc)

    **TODO** Remove the usage of ``get_single.nostrict`` and instead check if
    the definition to be modified is referenced within the dataflow. Do not run
    the dataflow if the definition to modify is not referenced in the flow.

    .. code-block:: console
        :test:

        $ dffml dataflow create \
            -configloader yaml \
            -config \
                '["preapply_operations:add_ambassador.outputs.result"]'=get_single.nostrict \
            -flow \
                '[{"seed": ["ssh.job"]}]'=preapply_operations:add_ambassador.inputs.contents \
            -inputs \
                preapply_operations:add_ambassador.outputs.result,=get_single_spec \
            -- \
                preapply_operations:add_ambassador \
                get_single \
            | tee preapply.yaml
        $ dffml dataflow diagram -stage processing -- preapply.yaml

    .. code-block:: console
        :test:

        $ dffml dataflow run records set \
            -log debug \
            -dataflow dataflow.json \
            -config \
                "$GITHUB_TOKEN='operations.gh:github_get_repo'.token" \
            -orchestrator ssh \
            -orchestrator-keep_tempdirs \
            -orchestrator-hostname localhost \
            -orchestrator-workdir . \
            -orchestrator-prerun prerun.json \
            -record-def "github.repo.url" \
            -keys \
              https://github.com/intel/dffml

    """
    CONFIG = SSHOrchestratorConfig
    CONTEXT = SSHOrchestratorContext

    async def __aenter__(self):
        await super().__aenter__()
        # Create myapp in the cache
        # import dffml.service.dev
        # cache_path = pathlib.Path('~', ".cache", "dffml", "df", "ssh", "myapp")
        # if not cache_path.is_dir():
        #     cache_path.mkdir(parents=True)
        # with chdir(cache_path.parent):
        #     await dffml.service.dev.Develop.create.blank._main("myapp")
        # Load prerun dataflow
        if self.config.prerun is not None:
            self.prerun = await load_dataflow_from_configloader(
                self.config.prerun
            )
        return self
