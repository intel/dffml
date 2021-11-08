"""
Our goal is to run a dataflow where each context is running as a job in a
kubernetes cluster.

We want to make sure that local execution of a dataflow can be kicked off in the
same way we can kick it off in kubernetes.

We want to support multiple execution options in kubernetes.

- Indexed Job for Parallel Processing with Static Work Assignment
  (`IndexedJobKubernetesOrchestratorContext`)

    - https://kubernetes.io/docs/tasks/job/indexed-parallel-processing-static/

    - In this case we must know all contexts ahead of time

    - Kubernetes manages execution we just track completion of the dataflow as a
      whole with a job for each context.

- DFFML managed job based (`JobKubernetesOrchestratorContext`)

    - https://kubernetes.io/docs/concepts/workloads/controllers/job/

    - In this case an orchestrator written in Python kicks off each job and
      tracks its completion.

    - We don't care about implementing this right now. We don't currently have a
      use case where more contexts might be added dynamically. Therefore we will
      wait to implement this.

Since we don't care about the non-indexed job case right now we'll only be
fully implementing the orchestrator that executes via Kubernetes Indexed job
completion model, `IndexedJobKubernetesOrchestratorContext`.

We'll first play around with the second option,
`JobKubernetesOrchestratorContext`, but only to get our bearings in a simplified
setting.

..
    TODO

     - Add properties to dataflows to allow them to raise issues with the way
       they might be executed.

       For example, executing each context in it's own job means that each
       context has it's own operation instances, they are not isolated at the
       dataflow scope, rather they are all isolated at the context scope.

       Some dataflows may not work if their contexts cannot share operation
       instances. We must provide some data section within the serialized
       dataflow which the orchestrator checks to see if it can run the dataflow
       without issue.

    - OperationImplementationNetwork that can load Python code that doesn't
      exist on the executing machine from another machine that has that code.
      Might be able to leverage "Loaders" of https://github.com/malwaredllc/byob
"""
import os
import json
import pathlib
import tarfile
import tempfile
import textwrap
import contextlib
import asyncio.subprocess
from typing import AsyncIterator, Tuple, Dict, Any, List

from .base import BaseContextHandle
from .memory import (
    MemoryOrchestratorConfig,
    MemoryOrchestratorContext,
    MemoryOrchestrator,
)
from ..base import config, field
from ..util.crypto import secure_hash
from ..util.data import export
from ..util.os import chdir
from ..util.entrypoint import entrypoint
from ..util.subprocess import run_command, exec_subprocess, Subprocess

# TODO Use importlib.resources instead of reading via pathlib
python_code: str = pathlib.Path(__file__).parent.joinpath(
    "kubernetes_execute_pickled_dataflow_with_inputs.py"
).read_text()


# TODO Move requirements logic to own prep dataflow which get's executed before
# the real dataflow.
@config
class JobKubernetesOrchestratorConfig(MemoryOrchestratorConfig):
    image: str = field(
        "Container image to use", default="intelotc/dffml:latest"
    )
    workdir: pathlib.Path = field(
        "Container build context and working directory for running container",
        default=None,
    )
    requirements: List[str] = field(
        "Python requirements to install before execution",
        default_factory=lambda: [],
    )


class JobKubernetesOrchestratorContext(MemoryOrchestratorContext):
    """
    The JobKubernetesOrchestratorContext will kick off each context within a
    pod. We json the dataflow and the inputs, make them secrets, and expose
    those as files. To run the dataflow we unpickle the dataflow and inputs and
    execute with the MemoryOrchestrator.
    """

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
        # Collect all initial inputs into a list to pass to kubernetes job
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
        # The kubernetes job
        job_name: str = secure_hash(
            ".".join(
                [
                    secure_hash(ctx_str, "sha384"),
                    secure_hash(str(self.config.dataflow.export()), "sha384"),
                ]
            ),
            "sha384",
        )[:62]
        container_name: str = job_name

        with tempfile.TemporaryDirectory() as tempdir:
            # Create temporary directory pathlib object
            tempdir_path = pathlib.Path(tempdir)
            # Create secrets for DATAFLOW and INPUTS environment variables
            # which will be json serialized respectively.
            # https://kubernetes.io/docs/tasks/configmap-secret/managing-secret-using-kustomize/
            # Write out the dataflow (secret)
            dataflow_path = tempdir_path.joinpath("dataflow.json")
            dataflow_path.write_text(json.dumps(self.config.dataflow.export()))
            # Write out the inputs (secret)
            inputs_path = tempdir_path.joinpath("inputs.json")
            inputs_path.write_text(json.dumps(inputs))
            # Write out the Python code to execute the dataflow
            execute_pickled_dataflow_with_inputs_path = tempdir_path.joinpath(
                "execute_pickled_dataflow_with_inputs.py"
            )
            execute_pickled_dataflow_with_inputs_path.write_text(python_code)
            # Write out the requirements
            requirements_path = tempdir_path.joinpath("requirements.txt")
            requirements_path.write_text(
                "\n".join(self.parent.config.requirements)
            )
            # Copy the context
            context_path = tempdir_path.joinpath("context.tar.gz")
            with tarfile.open(context_path, mode="x:gz") as tarobj:
                if (
                    self.parent.config.workdir is not None
                    and self.parent.config.workdir.is_dir()
                ):
                    with chdir(self.parent.config.workdir.resolve()):
                        tarobj.add(".")
            # Write out the kustomization.yaml file to create a ConfigMap for
            # the Python code and secrets for the dataflow and inputs.
            # https://kubernetes.io/docs/tutorials/configuration/configure-redis-using-configmap/
            tempdir_path.joinpath("kustomization.yaml").write_text(
                textwrap.dedent(
                    f"""
                    configMapGenerator:
                    - name: execute-pickled-dataflow-with-inputs-py
                      files:
                      - {execute_pickled_dataflow_with_inputs_path.relative_to(tempdir_path)}
                    secretGenerator:
                    - name: dataflow-inputs
                      files:
                      - {dataflow_path.relative_to(tempdir_path)}
                      - {inputs_path.relative_to(tempdir_path)}
                      - {requirements_path.relative_to(tempdir_path)}
                      - {context_path.relative_to(tempdir_path)}
                    """
                ).lstrip()
            )
            # Create output file to parse with created objects
            kustomization_apply_path = tempdir_path.joinpath(
                "kustomization_apply"
            )
            with open(kustomization_apply_path, "wb") as stdout:
                await run_command(
                    ["kubectl", "apply", "-o=json", "-k", "."],
                    cwd=tempdir,
                    stdout=stdout,
                )
            kustomization_apply = json.loads(
                kustomization_apply_path.read_text()
            )
            # Grab named of created ConfigMap and Secret
            configmap_name = [
                item
                for item in kustomization_apply["items"]
                if item["kind"] == "ConfigMap"
            ][0]["metadata"]["name"]
            secret_name = [
                item
                for item in kustomization_apply["items"]
                if item["kind"] == "Secret"
            ][0]["metadata"]["name"]
            # The commands to run
            commands: List[List[str]] = [
                [
                    "python",
                    "-u",
                    "/usr/src/dffml-kubernetes-job-code/execute_pickled_dataflow_with_inputs.py",
                ],
            ]
            # If we have a context we need to extract it into the working
            # directory before we run the dataflow.
            if self.parent.config.requirements:
                commands.insert(
                    0,
                    [
                        "python",
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        '"${REQUIREMENTS}"',
                        '2>"${PIP_LOG_FILE}"',
                        "1>&2",
                    ],
                )
            # If we have a requirements file then we need to install from that
            # before we run the dataflow (if we haven't built a new container
            # and are doing this at runtime).
            if (
                self.parent.config.workdir is not None
                and self.parent.config.workdir.is_dir()
            ):
                commands.insert(
                    0,
                    [
                        "tar",
                        "-xvzf",
                        '"${CONTEXT}"',
                        '2>"${CONTEXT_LOG_FILE}"',
                        "1>&2",
                    ],
                )
            # Shell command to execute all above commands
            command: List[str] = [
                "sh",
                "-c",
                " && ".join([" ".join(cmd) for cmd in commands]),
            ]
            self.logger.debug("command: %r", command)
            # Write out the batch job
            # TODO Make configmap and secrets immutable and volume mounts read
            # only
            # TODO Change backoffLimit to more than 0. This will require
            # changing searching for pods not by label since if the job fails to
            # start right away then another pod is created, up to backoffLimit
            # more pods will be created on failure.
            tempdir_path.joinpath("job.yml").write_text(
                textwrap.dedent(
                    f"""
                    apiVersion: batch/v1
                    kind: Job
                    metadata:
                      name: {job_name}
                    spec:
                      template:
                        spec:
                          automountServiceAccountToken: false

                          containers:
                          - name: {container_name}
                            image: {self.parent.config.image}
                            command: {json.dumps(command)}
                            workingDir: /usr/src/dffml-kubernetes-job-working-dir/
                            volumeMounts:
                              # name must match the volume name below
                              - name: dffml-kubernetes-job-code
                                mountPath: /usr/src/dffml-kubernetes-job-code
                              - name: dffml-kubernetes-job-secrets
                                mountPath: /usr/src/dffml-kubernetes-job-secrets
                              - name: dffml-kubernetes-job-state
                                mountPath: /usr/src/dffml-kubernetes-job-state
                              - name: dffml-kubernetes-job-working-dir
                                mountPath: /usr/src/dffml-kubernetes-job-working-dir
                            env:
                            - name: DATAFLOW
                              value: /usr/src/dffml-kubernetes-job-secrets/dataflow.json
                            - name: INPUTS
                              value: /usr/src/dffml-kubernetes-job-secrets/inputs.json
                            - name: CONTEXT_LOG_FILE
                              value: /usr/src/dffml-kubernetes-job-state/context-log.txt
                            - name: PIP_LOG_FILE
                              value: /usr/src/dffml-kubernetes-job-state/pip-logs.txt
                            - name: LOG_FILE
                              value: /usr/src/dffml-kubernetes-job-state/logs.txt
                            - name: REQUIREMENTS
                              value: /usr/src/dffml-kubernetes-job-secrets/requirements.txt
                            - name: CONTEXT
                              value: /usr/src/dffml-kubernetes-job-secrets/context.tar.gz
                            - name: HTTP_PROXY
                              value: {os.environ["HTTP_PROXY"]}
                            - name: HTTPS_PROXY
                              value: {os.environ["HTTPS_PROXY"]}
                          # The secret data is exposed to Containers in the Pod through a Volume.
                          volumes:
                            - name: dffml-kubernetes-job-code
                              configMap:
                                # Provide the name of the ConfigMap you want to mount.
                                name: {configmap_name}
                            - name: dffml-kubernetes-job-secrets
                              secret:
                                secretName: {secret_name}
                            - name: dffml-kubernetes-job-state
                              emptyDir: {{}}
                            - name: dffml-kubernetes-job-working-dir
                              emptyDir: {{}}
                          restartPolicy: Never
                      backoffLimit: 0
                    """
                ).lstrip()
            )

            with contextlib.suppress(RuntimeError):
                await run_command(
                    ["kubectl", "delete", "job", job_name], cwd=tempdir,
                )
            # NOTE kind is not setup to pull with docker's credentials. It hits
            # the rate limit right away.
            #   $ kind load docker-image docker.io/intelotc/dffml:latest
            # NOTE All the rest of Intel's containers moved to intel/ on docker
            # hub. We should investigate GitHub Continer Registry.
            # Create output file to parse with created job
            job_apply_path = tempdir_path.joinpath("job_apply")
            with open(job_apply_path, "wb") as stdout:
                await run_command(
                    ["kubectl", "apply", "-f", "job.yml", "-o=json"],
                    cwd=tempdir,
                    stdout=stdout,
                )
            job_apply = json.loads(job_apply_path.read_text())
            # Grab the label which we can view the logs by querying
            label = "job-name"
            label_value = job_apply["metadata"]["labels"][label]
            # Watch the state of the job
            # NOTE When using --watch the jsonpath selector is different
            # https://github.com/kubernetes/kubectl/issues/913#issuecomment-933750138

            cmd = [
                "kubectl",
                "get",
                "pods",
                "--watch",
                r'-o=jsonpath={range .items[*]}{.status.phase}{"\n"}',
                "-l",
                f"{label}={label_value}",
            ]
            async for event, result in exec_subprocess(cmd):
                if event == Subprocess.STDOUT_READLINE:
                    # Update phase
                    phase = result.decode().rstrip()
                    self.logger.debug(f"{cmd}: {event}: {phase}")
                    # Check for failure
                    # https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
                    if phase == "Succeeded":
                        break
                    elif phase == "Failed":
                        # Create log file for output
                        job_output_path = tempdir_path.joinpath("job_output")
                        with open(job_output_path, "wb") as stdout:
                            await run_command(
                                [
                                    "kubectl",
                                    "logs",
                                    "-l",
                                    f"{label}={label_value}",
                                ],
                                cwd=tempdir,
                                stdout=stdout,
                            )
                        raise Exception(
                            f"pod {label}={label_value} phase {phase}. logs: {job_output_path.read_text()}"
                        )
                    elif phase == "Unknown":
                        raise Exception(
                            f"pod {label}={label_value} phase {phase}"
                        )
                elif event == Subprocess.STDERR_READLINE:
                    # Log stderr line read
                    self.logger.error(
                        f"{cmd}: {event}: {result.decode().rstrip()}"
                    )
                elif event == Subprocess.COMPLETED and result != 0:
                    # Raise if anything goes wrong
                    raise RuntimeError("Failed to watch pod")
            # Create file for output
            job_stdout_path = tempdir_path.joinpath("job_stdout")
            with open(job_stdout_path, "wb") as stdout:
                await run_command(
                    ["kubectl", "logs", "-l", f"{label}={label_value}"],
                    cwd=tempdir,
                    stdout=stdout,
                )
            return ctx, json.loads(job_stdout_path.read_text())


@entrypoint("kubernetes.job")
class JobKubernetesOrchestrator(MemoryOrchestrator):
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

    We can run the dataflow using the DFFML command line interface rather than
    running the Python file.

    Execute in kubernetes (kubectl default context will be used)

    .. code-block:: console
        :test:

        $ dffml dataflow run records set \
            -log debug \
            -dataflow dataflow.json \
            -config \
                "$GITHUB_TOKEN='operations.gh:github_get_repo'.token" \
            -orchestrator kubernetes.job \
            -orchestrator-workdir . \
            -orchestrator-requirements PyGithub \
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

        orchestrator = dffml.JobKubernetesOrchestrator(
            workdir=os.getcwd(),
            requirements=[
                "PyGithub",
            ],
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
        :test:

        $ python dataflow.py

    """
    CONFIG = JobKubernetesOrchestratorConfig
    CONTEXT = JobKubernetesOrchestratorContext
