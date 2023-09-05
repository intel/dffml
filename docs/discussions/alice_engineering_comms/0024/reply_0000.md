## 2022-09-12 @pdxjohnny Engineering Logs

- https://github.com/kubernetes-sigs/image-builder
  - https://github.com/imjasonh/kontain.me
  - https://github.com/imjasonh/kontain.me/blob/main/pkg/serve/serve.go
  - secrets in last layer for k8s orch
- https://twitter.com/pchaigno/status/1439965320056344577?s=20&t=snDh0RTRB1FYmv2AEeIuWQ
- TOOD
  - [ ] DataFlow execution within linux loader to do attestation to secret service and set in env before execing `__start`
  - configure NFS then mount as volume via preapply. Use this to cache cloned repos and execute pull instead of clone to resolve deltas for iterative scanning over time.
    - subflow reuse ictx output operation grab inputs with definitions who are decents of STATIC and CACHED and NFS (eventually NFS and kubernetes stuff should be overlays)
  - Threaded execution of sets of contexts