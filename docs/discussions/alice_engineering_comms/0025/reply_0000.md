## 2022-09-13 @pdxjohnny Engineering Logs

```console
$ dffml service dev export alice.cli:ALICE_COLLECTOR_DATAFLOW | tee alice_collector_dataflow.json
$ (date; (echo URL && sed -e 's/^.*/https:\/\/github.com\/dffml\/&/' org-repo-list | head -n 1) | dffml dataflow run records all   -no-echo   -record-def URL   -dataflow alice_collector_dataflow.json   -sources src=csv dst=mongodb   -source-src-filename /dev/stdin   -source-src-key URL   -source-dst-uri "${DATABASE_CONNECTION_STRING}"   -source-dst-tlsInsecure   -source-dst-log_collection_names   -source-dst-collection mycollection  -orchestrator kubernetes.job -orchestrator-workdir . -log debug -no-strict -orchestrator-max_ctxs 25 -orchestrator-image docker.io/intel-otc/dffml:latest 2>&1; date) | tee ~/alice-shouldi-contribute-mycollection-$(date +%4Y-%m-%d-%H-%M).txt
...
DEBUG:dffml.JobKubernetesOrchestratorContext:context_path.stat().st_size: 60876856
DEBUG:dffml.JobKubernetesOrchestratorContext:dffml_path.stat().st_size: 157628
ERROR:dffml.JobKubernetesOrchestratorContext:Traceback for <Task finished name='Task-7' coro=<JobKubernetesOrchestratorContext.run_operations_for_ctx() done, defined at /src/dffml/dffml/df/kubernetes.py:213> exception=RuntimeError('[\'kubectl\', \'--context\', \'kind-kind\', \'apply\', \'-o=json\', \'-k\', \'.\']: Error from server: error when creating ".": the server responded with the status code 413 but did not return more information (post secrets)\n')> (most recent call last):
  File "/src/dffml/dffml/df/kubernetes.py", line 780, in run_operations_for_ctx
    raise Exception(
  File "/src/dffml/dffml/util/subprocess.py", line 140, in run_command
    pass
  File "/src/dffml/dffml/util/subprocess.py", line 83, in run_command_events
    raise RuntimeError(
RuntimeError: ['kubectl', '--context', 'kind-kind', 'apply', '-o=json', '-k', '.']: Error from server: error when creating ".": the server responded with the status code 413 but did not return more information (post secrets)
Traceback (most recent call last):
  File "/home/coder/.local/bin/dffml", line 33, in <module>
    sys.exit(load_entry_point('dffml', 'console_scripts', 'dffml')())
  File "/src/dffml/dffml/util/cli/cmd.py", line 282, in main
    result = loop.run_until_complete(cls._main(*argv[1:]))
  File "/.pyenv/versions/3.9.13/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
    return future.result()
  File "/src/dffml/dffml/util/cli/cmd.py", line 248, in _main
    return await cls.cli(*args)
  File "/src/dffml/dffml/util/cli/cmd.py", line 234, in cli
    return await cmd.do_run()
  File "/src/dffml/dffml/util/cli/cmd.py", line 211, in do_run
    return [res async for res in self.run()]
  File "/src/dffml/dffml/util/cli/cmd.py", line 211, in <listcomp>
    return [res async for res in self.run()]
  File "/src/dffml/dffml/cli/dataflow.py", line 283, in run
    async for record in self.run_dataflow(
  File "/src/dffml/dffml/cli/dataflow.py", line 268, in run_dataflow
    async for ctx, results in octx.run(
  File "/src/dffml/dffml/df/memory.py", line 1721, in run
    task.result()
  File "/src/dffml/dffml/df/kubernetes.py", line 355, in run_operations_for_ctx
    await run_command(
  File "/src/dffml/dffml/util/subprocess.py", line 137, in run_command
    async for _, _ in run_command_events(
  File "/src/dffml/dffml/util/subprocess.py", line 83, in run_command_events
    raise RuntimeError(
RuntimeError: ['kubectl', '--context', 'kind-kind', 'apply', '-o=json', '-k', '.']: Error from server: error when creating ".": the server responded with the status code 413 but did not return more information (post sec
```

- TODO
  - [ ] Update Job based Kubernetes Orchestrator to add a note that sometimes a `preapply` is needed to set the limits (required to be set by the namespace?)
    - https://github.com/intel/dffml/blob/3e157b391ffc36b6073288d0fe7a21a6a82b55a4/dffml/df/kubernetes.py#L1048-L1108
```