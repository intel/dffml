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

     - Sometime success is found in last log status which leads to failure since
       next round of test job has not really started yet.

     - When we refactor to add event types we should output init container logs
       via one of those event types or a custom event type.

     - Refactor to separate output of config files from kubectl
       apply commands. This would allow users to manually apply if they
       wanted to.

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
from .base import BaseOrchestrator, BaseContextHandle
from .memory import (
    MemoryOrchestratorConfig,
    MemoryOrchestratorContext,
    MemoryOrchestrator,
)
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


class JobKubernetesOrchestratorPreApplyDefinitions(enum.Enum):
    KUSTOMIZATION = Definition(
        name="kubernetes.job.kustomization", primitive="string"
    )
    JOB = Definition(name="kubernetes.job.job", primitive="string")
    # The BaseInputSetContext about to be applied
    CONTEXT = Definition(name="kubernetes.job.context", primitive="object")
    # The temporary directory we're creating job files in
    TEMPDIR = Definition(name="kubernetes.job.tempdir", primitive="string")


@config
class JobKubernetesOrchestratorConfig(MemoryOrchestratorConfig):
    context: str = field("kubectl context to use", default=None)
    image: str = field(
        "Container image to use", default="intelotc/dffml:latest"
    )
    workdir: pathlib.Path = field(
        "Container build context and working directory for running container",
        default=None,
    )
    no_dffml: bool = field(
        "Do not overwrite the containers version of dffml with the local version",
        default=False,
    )
    prerun: DataFlow = field(
        "DataFlow run before running each context's DataFlow", default=None,
    )
    # TODO Figure out how to make an operation a CMD. Then this object would
    # also include the orchestrator
    preapply: DataFlow = field(
        "DataFlow run on all kubernetes resources before they are applied",
        default=None,
    )
    opreapply: BaseOrchestrator = field(
        "Orchestrator for preapply dataflow", default=None,
    )


@contextlib.asynccontextmanager
async def exit_stacks():
    """
    Convenience method to help with refactoring so we don't see large code
    changes due to indentation changes when introducing an async context
    manager to an existing context manager.
    """
    with contextlib.ExitStack() as stack:
        async with contextlib.AsyncExitStack() as astack:
            yield stack, astack


class JobKubernetesOrchestratorContext(MemoryOrchestratorContext):
    """
    The JobKubernetesOrchestratorContext will kick off each context within a
    pod. We json the dataflow and the inputs, make them secrets, and expose
    those as files. To run the dataflow we unpickle the dataflow and inputs and
    execute with the MemoryOrchestrator.
    """

    def __init__(
        self,
        config: "MemoryOrchestratorContextConfig",
        parent: "JobKubernetesOrchestrator",
    ) -> None:
        super().__init__(config, parent)
        self.kubectl = ["kubectl", "--context", self.parent.config.context]

    async def modification_preapply(
        self,
        ctx: BaseContextHandle,
        definition: Definition,
        value: str,
        *inputs: Input,
    ):
        """
        It could be useful to implement per-context modifications to the generated YAML
        files before application to the cluster. This could be implemented by emitting a
        configuration required event to the parent dataflow. Currently only one
        dataflow to allow for modification of each context's resources may be given.
        """
        if self.parent.config.preapply is None:
            # Do no modification if there is no dataflow to run for preapply
            return value
        async for ctx, results in self.opreapply_ctx.run(
            [
                Input(
                    value=ctx,
                    definition=JobKubernetesOrchestratorPreApplyDefinitions.CONTEXT.value,
                ),
                Input(value=value, definition=definition.value),
                *inputs,
            ],
        ):
            self.logger.debug("preapply results: %r", results)
            if not results:
                return value
            # Return the value if the resulting dict is a key value mapping
            if isinstance(results, str):
                return results
            elif isinstance(results, dict):
                return [value for value in results.values()][0]
            else:
                raise NotImplementedError(
                    f"Return value of dataflow was neither dict nor str: {results!r}"
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
        job_name_components: List[str] = [
            str(uuid.uuid4()),
            secure_hash(ctx_str, "sha384"),
            secure_hash(str(self.config.dataflow.export()), "sha384"),
        ]
        job_name: str = secure_hash(".".join(job_name_components), "sha384")[
            :62
        ]
        container_name: str = job_name

        async with exit_stacks() as (stack, astack):
            # Create a temporary directory
            tempdir = stack.enter_context(tempfile.TemporaryDirectory())
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
            # Write out the Python code to execute the dataflow
            kubernetes_output_server_path = tempdir_path.joinpath(
                "kubernetes_output_server.py"
            )
            kubernetes_output_server_path.write_text(output_server)
            # Write out the prerun dataflow (secret)
            prerun_dataflow_path = tempdir_path.joinpath(
                "prerun-dataflow.json"
            )
            prerun = DataFlow()
            if self.parent.config.prerun is not None:
                prerun = self.parent.prerun
            prerun_dataflow_path.write_text(json.dumps(prerun.export()))
            # Copy the context
            context_path = tempdir_path.joinpath("context.tar.xz")
            with tarfile.open(context_path, mode="x:xz") as tarobj:
                if (
                    self.parent.config.workdir is not None
                    and self.parent.config.workdir.is_dir()
                ):
                    with chdir(self.parent.config.workdir.resolve()):
                        tarobj.add(".")
            self.logger.debug(
                "context_path.stat().st_size: %d", context_path.stat().st_size
            )
            # Copy the context
            dffml_path = tempdir_path.joinpath("dffml.tar.xz")
            with tarfile.open(dffml_path, mode="x:xz") as tarobj:
                if not self.parent.config.no_dffml:
                    with chdir(pathlib.Path(__file__).parents[2].resolve()):
                        try:
                            import importlib.metadata as importlib_metadata
                        except:
                            import importlib_metadata
                        # NOTE Need to run $ python setup.py egg_info for
                        # files()
                        for filename in importlib_metadata.files("dffml"):
                            if not str(filename).startswith("dffml"):
                                continue
                            tarobj.add(filename)
            self.logger.debug(
                "dffml_path.stat().st_size: %d", dffml_path.stat().st_size
            )
            # Format the kustomization.yaml file to create a ConfigMap for
            # the Python code and secrets for the dataflow and inputs.
            # https://kubernetes.io/docs/tutorials/configuration/configure-redis-using-configmap/
            kustomization_contents = textwrap.dedent(
                f"""
                configMapGenerator:
                - name: execute-pickled-dataflow-with-inputs-py
                  files:
                  - {execute_pickled_dataflow_with_inputs_path.relative_to(tempdir_path)}
                  - {kubernetes_output_server_path.relative_to(tempdir_path)}
                  - {dffml_path.relative_to(tempdir_path)}
                secretGenerator:
                - name: dataflow-inputs
                  files:
                  - {prerun_dataflow_path.relative_to(tempdir_path)}
                  - {dataflow_path.relative_to(tempdir_path)}
                  - {inputs_path.relative_to(tempdir_path)}
                  - {context_path.relative_to(tempdir_path)}
                """
            ).lstrip()
            # Write out the kustomization.yaml file
            tempdir_path.joinpath("kustomization.yaml").write_text(
                await self.modification_preapply(
                    ctx,
                    JobKubernetesOrchestratorPreApplyDefinitions.KUSTOMIZATION,
                    kustomization_contents,
                    Input(
                        value=tempdir,
                        definition=JobKubernetesOrchestratorPreApplyDefinitions.TEMPDIR.value,
                    ),
                )
            )
            # Create output file to parse with created objects
            kustomization_apply_path = tempdir_path.joinpath(
                "kustomization_apply"
            )
            with open(kustomization_apply_path, "wb") as stdout:
                await run_command(
                    [*self.kubectl, "apply", "-o=json", "-k", "."],
                    cwd=tempdir,
                    stdout=stdout,
                )
                astack.push_async_callback(
                    run_command,
                    [*self.kubectl, "delete", "-k", "."],
                    cwd=tempdir,
                    logger=self.logger,
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
            # The init container commands to run
            init_containers: List[str] = []
            init_container_names: Dict[str, str] = {}
            # If we have a context we need to extract it into the working
            # directory before we run the dataflow.
            if (
                self.parent.config.workdir is not None
                and self.parent.config.workdir.is_dir()
            ):
                command = [
                    "python",
                    "-m",
                    "tarfile",
                    "-ve",
                    "/usr/src/dffml-kubernetes-job-secrets/context.tar.xz",
                    ".",
                ]
                init_container_name: str = secure_hash(
                    ".".join(
                        ["initContainer", "workdir"] + job_name_components
                    ),
                    "sha384",
                )[:62]
                init_container_names["workdir"] = init_container_name
                init_containers.append(
                    textwrap.dedent(
                        f"""\
                        - name: {init_container_name}
                          image: {self.parent.config.image}
                          command: {json.dumps(command)}
                          workingDir: /usr/src/dffml-kubernetes-job-working-dir/
                          volumeMounts:
                            - name: dffml-kubernetes-job-working-dir
                              mountPath: /usr/src/dffml-kubernetes-job-working-dir
                            - name: dffml-kubernetes-job-secrets
                              mountPath: /usr/src/dffml-kubernetes-job-secrets
                        """
                    )
                )
            init_containers_text = ""
            if init_containers:
                # NOTE Build YAML manually, avoid introducing a dependency on
                # PyYAML
                # See below YAML, textwrap.dedent removes 4 4 space indents
                init_containers_indent: int = 4 * 4 + 6
                init_containers_text = "\n".join(
                    ["initContainers:"]
                    + [
                        (" " * init_containers_indent) + line
                        for line in "\n".join(init_containers).split("\n")
                    ]
                )
            # The output container is a simple server which accepts output
            # context's and results via a local address
            # TODO This only works for a single context right now
            output_container_name: str = secure_hash(
                ".".join(["outputContainer", "single"] + job_name_components),
                "sha384",
            )[:62]
            output_socket: str = "/usr/src/dffml-kubernetes-job-state/output.sock"
            output_command: List[str] = [
                "python",
                "-u",
                "/usr/src/dffml-kubernetes-job-code/kubernetes_output_server.py",
                output_socket,
            ]
            # Shell command to execute all above commands
            command: List[str] = [
                "sh",
                "-c",
                "set -x && (cd $(python -c 'import sys; print([path for path in sys.path if \"site-packages\" in path][-1])') && python -m tarfile -ve /usr/src/dffml-kubernetes-job-code/dffml.tar.xz .) && DATAFLOW=/usr/src/dffml-kubernetes-job-secrets/prerun-dataflow.json INPUTS='' OUTPUT='' python -u /usr/src/dffml-kubernetes-job-code/execute_pickled_dataflow_with_inputs.py && python -u /usr/src/dffml-kubernetes-job-code/execute_pickled_dataflow_with_inputs.py",
            ]
            self.logger.debug("command: %r", command)
            # Format the batch job
            job_contents = textwrap.dedent(
                f"""
                apiVersion: batch/v1
                kind: Job
                metadata:
                  name: {job_name}
                spec:
                  template:
                    spec:
                      automountServiceAccountToken: false
                      {init_containers_text}
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
                        - name: OUTPUT
                          value: {output_socket}
                        - name: HTTP_PROXY
                          value: {os.environ["HTTP_PROXY"]}
                        - name: HTTPS_PROXY
                          value: {os.environ["HTTPS_PROXY"]}
                      - name: {output_container_name}
                        image: {self.parent.config.image}
                        command: {json.dumps(output_command)}
                        workingDir: /usr/src/dffml-kubernetes-job-working-dir/
                        volumeMounts:
                          # name must match the volume name below
                          - name: dffml-kubernetes-job-code
                            mountPath: /usr/src/dffml-kubernetes-job-code
                          - name: dffml-kubernetes-job-state
                            mountPath: /usr/src/dffml-kubernetes-job-state
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
            # Write out the batch job
            # TODO Make configmap and secrets immutable and volume mounts read
            # only
            # TODO Change backoffLimit to more than 0. This will require
            # changing searching for pods not by label since if the job fails to
            # start right away then another pod is created, up to backoffLimit
            # more pods will be created on failure.
            tempdir_path.joinpath("job.yml").write_text(
                await self.modification_preapply(
                    ctx,
                    JobKubernetesOrchestratorPreApplyDefinitions.JOB,
                    job_contents,
                    Input(
                        value=tempdir,
                        definition=JobKubernetesOrchestratorPreApplyDefinitions.TEMPDIR.value,
                    ),
                )
            )

            with contextlib.suppress(RuntimeError):
                await run_command(
                    [*self.kubectl, "delete", "job", job_name], cwd=tempdir,
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
                    [*self.kubectl, "apply", "-f", "job.yml", "-o=json"],
                    cwd=tempdir,
                    stdout=stdout,
                )
                astack.push_async_callback(
                    run_command,
                    [*self.kubectl, "delete", "-f", "job.yml"],
                    cwd=tempdir,
                    logger=self.logger,
                )
            job_apply = json.loads(job_apply_path.read_text())
            # Grab the label which we can view the logs by querying
            label = "job-name"
            label_value = job_apply["metadata"]["labels"][label]
            # Watch the state of the job
            # NOTE When using --watch the jsonpath selector is different
            # https://github.com/kubernetes/kubectl/issues/913#issuecomment-933750138
            cmd = [
                *self.kubectl,
                "get",
                "pods",
                "--watch",
                "-o=json",
                # r'-o=jsonpath={range .items[*]}{.status.phase}{"\n"}',
                "-l",
                f"{label}={label_value}",
            ]
            get_pods = (exec_subprocess(cmd).__aiter__()).__anext__
            work = {
                asyncio.create_task(get_pods()): "get_pods",
            }
            self.logger.debug(f"get_pods: {' '.join(cmd)}")

            class _STOPPED:
                pass

            STOPPED = _STOPPED()

            async def anext(coro):
                try:
                    return await coro
                except StopAsyncIteration:
                    return STOPPED

            phase = ""
            # Launched log
            make_logger_cmd = lambda logs_container_name: [
                *self.kubectl,
                "logs",
                "-l",
                f"{label}={label_value}",
                "-c",
                logs_container_name,
                "--tail=-1",
                "-f",
            ]
            loggers_launched = set()

            @dataclasses.dataclass
            class Logger:
                name: str
                container_name: str
                cmd: List[str]
                anext: Callable = None
                restart_count: int = 0

            loggers = {
                f"log.{init_container_purpose}": Logger(
                    f"log.{init_container_purpose}",
                    init_container_name,
                    make_logger_cmd(init_container_name),
                )
                for init_container_purpose, init_container_name in init_container_names.items()
            }
            # Used to load full JSON
            get_pods_buffer = ""
            async for event, result in concurrently(work):
                if event == "get_pods":
                    if result is STOPPED:
                        continue
                    subprocess_event, result = result
                    if subprocess_event == Subprocess.STDOUT_READLINE:
                        # Update phase
                        line = result.decode().rstrip()
                        if line == "{":
                            get_pods_buffer = line
                        elif line == "}":
                            get_pods_buffer += line
                            # Check the phase and launch logs if started
                            get_pods_data = json.loads(get_pods_buffer)
                            if not isinstance(get_pods_data["status"], dict):
                                self.logger.info(
                                    f'get_pods_data["status"] was not a dict: {get_pods_data["status"]}'
                                )
                                continue
                            phase = get_pods_data["status"]["phase"]
                            phase = get_pods_data["status"]["phase"]
                            self.logger.debug(f"{event}: phase: {phase}")
                            # Make sure we are collecting logs from all places
                            # TODO Make this configurable, sometimes we may not
                            # want to collect logs from chatty containers
                            for container in get_pods_data["status"].get(
                                "containerStatuses", []
                            ):
                                if f"log.{container['name']}" in loggers:
                                    continue
                                loggers[f"log.{container['name']}"] = Logger(
                                    f"log.{container['name']}",
                                    container["name"],
                                    make_logger_cmd(container["name"]),
                                )
                            # Check for failure
                            # https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase
                            if phase != "Pending" and len(loggers) != len(
                                loggers_launched
                            ):
                                for logger in loggers.values():
                                    if logger.name in loggers_launched:
                                        continue
                                    self.logger.debug(
                                        f"{logger.name}: {' '.join(logger.cmd)}"
                                    )
                                    logger.anext = (
                                        exec_subprocess(
                                            make_logger_cmd(
                                                logger.container_name
                                            )
                                        ).__aiter__()
                                    ).__anext__
                                    work[
                                        asyncio.create_task(
                                            anext(logger.anext())
                                        )
                                    ] = logger.name
                                    loggers_launched.add(logger.name)
                            if phase == "Succeeded":
                                break
                            elif phase in ("Failed", "Unknown"):
                                raise Exception(
                                    f"pod {label}={label_value} phase {phase}: {get_pods_buffer}"
                                )
                        else:
                            get_pods_buffer += line + "\n"
                    elif subprocess_event == Subprocess.STDERR_READLINE:
                        # Log stderr line read
                        self.logger.error(
                            f"{event}: {subprocess_event}: {result.decode().rstrip()}"
                        )
                    elif (
                        subprocess_event == Subprocess.COMPLETED
                        and result != 0
                    ):
                        # Raise if anything goes wrong
                        raise RuntimeError("Failed to watch pod")
                    # Look for next line from get pods subprocess
                    task = asyncio.create_task(anext(get_pods()))
                    work[task] = event
                elif event.startswith("log."):
                    if result is STOPPED:
                        continue
                    subprocess_event, result = result
                    if subprocess_event == Subprocess.STDOUT_READLINE:
                        self.logger.debug(
                            f"{event}: {subprocess_event}: {result.decode().rstrip()}"
                        )
                    elif subprocess_event == Subprocess.STDERR_READLINE:
                        self.logger.error(
                            f"{event}: {subprocess_event}: {result.decode().rstrip()}"
                        )
                    elif (
                        subprocess_event == Subprocess.COMPLETED
                        and result != 0
                        and loggers[event].restart_count < 1
                    ):
                        loggers[event].restart_count += 1
                        loggers_launched.remove(loggers[event].name)
                        self.logger.error(
                            "Failed to read pod logs, restarting "
                            f"{logger.name}: {' '.join(loggers[event].cmd)}"
                        )
                        continue
                    elif (
                        subprocess_event == Subprocess.COMPLETED
                        and phase == "Failed"
                    ):
                        raise Exception(
                            f"pod {label}={label_value} phase {phase}"
                        )
                    # Look for next line from logs subprocess
                    task = asyncio.create_task(anext(loggers[event].anext()))
                    work[task] = event
            # Create file for output
            job_stdout_path = tempdir_path.joinpath("job_output")
            with open(job_stdout_path, "wb") as stdout:
                await run_command(
                    [
                        *self.kubectl,
                        "logs",
                        "-l",
                        f"{label}={label_value}",
                        "-c",
                        output_container_name,
                    ],
                    cwd=tempdir,
                    stdout=stdout,
                )
            job_stdout = job_stdout_path.read_text()
            try:
                return ctx, json.loads(job_stdout)
            except json.decoder.JSONDecodeError as e:
                raise Exception(
                    f"job output was not json: {job_stdout}"
                ) from e

    async def __aenter__(self):
        await super().__aenter__()
        # Enter orchestrator context context
        if self.parent.config.preapply is not None:
            self.opreapply_ctx = await self._stack.enter_async_context(
                self.parent.opreapply(self.parent.preapply)
            )
        return self


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

    Execute in kubernetes (kubectl default context will be used)

    .. code-block:: console

        $ dffml dataflow run records set \
            -log debug \
            -dataflow dataflow.json \
            -config \
                "$GITHUB_TOKEN='operations.gh:github_get_repo'.token" \
            -orchestrator kubernetes.job \
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

        orchestrator = dffml.JobKubernetesOrchestrator(
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
    ``kubectl apply``. Let's write some operations and create a dataflow.

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
                '[{"seed": ["kubernetes.job.job"]}]'=preapply_operations:add_ambassador.inputs.contents \
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
            -orchestrator kubernetes.job \
            -orchestrator-workdir . \
            -orchestrator-prerun prerun.json \
            -orchestrator-preapply preapply.yaml \
            -record-def "github.repo.url" \
            -keys \
              https://github.com/intel/dffml

    Debugging
    ---------

    Remove all resources in a namespace

    .. code-block:: console

        $ kubectl --context kind-kind delete all --all

    """
    CONFIG = JobKubernetesOrchestratorConfig
    CONTEXT = JobKubernetesOrchestratorContext

    async def __aenter__(self):
        await super().__aenter__()
        # Find default context to use if not given
        if self.config.context is None:
            with self.config.no_enforce_immutable():
                while not self.config.context:
                    cmd = ["kubectl", "config", "current-context"]
                    self.logger.debug(
                        f"kubectl context not given. running {cmd}"
                    )
                    async for event, result in run_command_events(
                        cmd,
                        events=[
                            Subprocess.STDERR_READLINE,
                            Subprocess.STDOUT_READLINE,
                        ],
                    ):
                        if event == Subprocess.STDERR_READLINE:
                            self.logger.error(
                                f"{cmd}: {result.decode().rstrip()}"
                            )
                        elif event == Subprocess.STDOUT_READLINE:
                            self.config.context = result.decode().strip()
            self.logger.debug(
                "kubectl context not given. Default context is %r",
                self.config.context,
            )
        # Load prerun dataflow
        if self.config.prerun is not None:
            self.prerun = await load_dataflow_from_configloader(
                self.config.prerun
            )
        # Load preapply dataflow
        if self.config.preapply is not None:
            # Enter orchestrator context
            self.opreapply = await self._stack.enter_async_context(
                self.config.opreapply
                if self.config.opreapply is not None
                else MemoryOrchestrator()
            )
            # Load preapply dataflow
            self.preapply = await load_dataflow_from_configloader(
                self.config.preapply
            )
        return self
