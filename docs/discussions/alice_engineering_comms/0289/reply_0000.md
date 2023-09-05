- https://github.com/project-oak/transparent-release
- https://github.com/OFS/
- https://gist.github.com/7876a0de6e2b318ffbfa7eabaacf172b
- https://github.com/docker/docker-bench-security/blob/master/.github/workflows/slsa.yml
- https://github.com/PyO3/maturin
  - https://www.maturin.rs/metadata.html

```console
$ cat valid.json | jq -r .untagged[].features.group_by.RepoURL[]
https://github.com/intel/dffml
```