## 2022-10-11 @pdxjohnny Engineering Logs

- https://docs.github.com/en/actions/security-guides/automatic-token-authentication
- source data flow as class
  - update
    - record to mongo doc operation
      - overlay/ride for custom (camel case feature keys for example)
    - mongo doc upsert operation
- https://mobile.twitter.com/kpcyrd/status/1579617445824040960
  - > I don't think there's anything that can be used as an unlink(2) primitive, the Docker Image Spec has something vaguely similar by special-casing files that start with `.wh.`, putting `RUN touch /etc/.wh.os-release` in your Dockerfile deletes /etc/os-release in the final image. 🥷
- https://www.civo.com/learn/kubernetes-power-for-virtual-machines-using-kubevirt
- https://github.com/kubevirt/kubevirt
- https://github.com/dffml/dffml-pre-image-removal/commits/shouldi_dep_tree
- https://github.com/chainguard-dev/melange/pull/128/files
  - Golang CLI library Cobra has docs generation
- https://github.com/intel/dffml/actions/runs/3228504774/jobs/5284698480
  - Manifest consumption worked
  - https://github.com/intel/dffml/commit/0ba6357165cfd69583a7564edf8ec6d77157fcfa

```
Error response from daemon: failed to create shim: OCI runtime create failed: runc create failed: unable to start container process: exec: "tail": executable file not found in $PATH: unknown
```

[Build: Images: Containers: .github#L1](https://github.com/intel/dffml/commit/74f80dd25577b4047429b00a880f06aaa74829bc#annotation_4889996315)
```
Error when evaluating 'strategy' for job 'build'. intel/dffml/.github/workflows/build_images_containers.yml@74f80dd25577b4047429b00a880f06aaa74829bc (Line: 64, Col: 19): Error parsing fromJson,intel/dffml/.github/workflows/build_images_containers.yml@74f80dd25577b4047429b00a880f06aaa74829bc (Line: 64, Col: 19): Invalid property identifier character: \. Path '[0]', line 1, position 2.,intel/dffml/.github/workflows/build_images_containers.yml@74f80dd25577b4047429b00a880f06aaa74829bc (Line: 64, Col: 19): Unexpected type of value '', expected type: Sequence.
```