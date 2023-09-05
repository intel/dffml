# 2022-09-14 Engineering Logs

In put networj which resolves or syntehises pipeline orchestrator specifc workflow/job to run data flow effectively using workflow/job syntax as trampoline bacj into dataflow, pull orchestrator secrets applicably

```console
$ echo -e 'if [[ "x${RUN_ME}" != "x" ]]; then\n  ${RUN_ME}\nfi' | RUN_ME='echo hi' bash
hi
```