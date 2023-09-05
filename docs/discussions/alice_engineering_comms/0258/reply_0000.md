## 2023-05-04 @pdxjohnny Engineering Logs

- https://github.com/in-toto/demo/pull/49
  - COSE2
- Use the DFFML/OA (later CycloneDX DAG) and sign with with COSE2
  - https://github.com/in-toto/layout-web-tool/blob/3ec3f9dc7668b831f29b9fb1103b245bb6965dc7/wizard.py#L974-L1056

```console
cd $(mktemp -d)  \
  && in-toto-run --key alice --materials . --products . --step-name vcs-1 -- git clone --depth=1 https://github.com/pdxjohnny/httptest .  \
  && in-toto-run --key alice --materials . --products . --step-name qa-1 -- python -m unittest discover -v  \
  && in-toto-run --key alice --materials . --products . --step-name package-1 -- python -m build . \
  && tar czf in_toto_link_files.tar.gz vcs-1*.link qa-1*.link package-1*.link
```

- https://gist.github.com/79807b9e20e920c5aad6ab01b447c418

![image](https://user-images.githubusercontent.com/5950433/236342187-b65e7336-9c0a-4080-8a0b-b485604e9e62.png)

- https://github.com/intel/dffml/blob/0c188d6dce3a8b953df32bd6fc8560323b89633e/.github/workflows/pin_downstream.yml
- https://git.juici.ly/consensual/federated-auth-network/src/branch/master/SPEC.md
  - Cross ref next SCITT meeting topic on DIDs
- TODO
  - [ ] Basic allowlist in workflow cross repo pinning
    - https://github.com/dffml/dffml-model-transformers/pull/2
    - https://github.com/intel/dffml/pull/1453
    - 