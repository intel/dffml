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
import json
import pathlib
import tempfile
import textwrap
import contextlib
import asyncio.subprocess
from typing import AsyncIterator, Tuple, Dict, Any

from .base import BaseContextHandle
from .memory import MemoryOrchestratorContext, MemoryOrchestrator
from ..util.crypto import secure_hash
from ..util.data import export
from ..util.entrypoint import entrypoint
from ..util.subprocess import run_command, exec_subprocess, Subprocess

# TODO Use importlib.resources instead of reading via pathlib
python_code: str = pathlib.Path(__file__).parent.joinpath(
    "kubernetes_execute_pickled_dataflow_with_inputs.py"
).read_text()


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
        container_image: str = "intelotc/dffml"

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
                            image: {container_image}
                            command: ["python", "-u", "/usr/src/dffml-kubernetes-job-code/execute_pickled_dataflow_with_inputs.py"]
                            volumeMounts:
                              # name must match the volume name below
                              - name: dffml-kubernetes-job-code
                                mountPath: /usr/src/dffml-kubernetes-job-code
                              - name: dffml-kubernetes-job-secrets
                                mountPath: /usr/src/dffml-kubernetes-job-secrets
                              - name: dffml-kubernetes-job-state
                                mountPath: /usr/src/dffml-kubernetes-job-state
                            env:
                            - name: DATAFLOW
                              value: /usr/src/dffml-kubernetes-job-secrets/dataflow.json
                            - name: INPUTS
                              value: /usr/src/dffml-kubernetes-job-secrets/inputs.json
                            - name: LOG_FILE
                              value: /usr/src/dffml-kubernetes-job-state/logs.txt
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

    Create a dataflow

    .. code-block:: console

        $ dffml dataflow create \
            -inputs \
              '["product"]'=get_single_spec \
            -- \
              multiply \
              get_single \
            | tee dataflow.json

    Execute (kubectl default context will be used)

    .. code-block:: console

        $ dffml dataflow run single \
            -dataflow dataflow.json \
            -orchestrator kubernetes.job \
            -inputs \
              4=multiplier_def \
              4=multiplicand_def

    The same example using Python

    .. code-block:: python

        import asyncio
        from dffml import *

        dataflow = DataFlow(multiply, GetSingle)
        dataflow.seed.append(
            Input(
                value=[multiply.op.outputs["product"].name],
                definition=GetSingle.op.inputs["spec"],
            )
        )

        orchestrator = JobKubernetesOrchestrator()

        async def main():
           async for ctx, results in run(
               dataflow,
               {
                   "18": [
                       Input(value=3, definition=multiply.op.inputs["multiplier"],),
                       Input(value=6, definition=multiply.op.inputs["multiplicand"],),
                   ],
               },
               orchestrator=orchestrator,
           ):
               print(results["product"])

        asyncio.run(main())
    """
    CONTEXT = JobKubernetesOrchestratorContext
