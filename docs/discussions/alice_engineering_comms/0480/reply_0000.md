## 2023-12-13 @pdxjohnny Engineering Logs

![image](https://github.com/intel/dffml/assets/5950433/0db2ba1b-776d-4ab5-8f5b-95e56c363da5)

- TODO
  - [x] DFFML testing CI build job submit SBOM to SCITT
    - public-keys branch for notary keys
    - https://github.com/intel/dffml/actions/runs/7198235389/job/19607199178
    - https://github.com/intel/dffml/blob/409880c54eb85bae5b79debaa23957008427c5a9/.github/workflows/testing.yml#L15-L135
  - [ ] Docker service for job running SCITT
    - [ ] SCITT private key in GitHub Actions secrets
    - [ ] Commit workspace storage to branch
    - [ ] Federate to unstable instance
  - [x] UI to browse SCITT entries
    - https://github.com/scitt-community/scitt-api-emulator/tree/2f499670e5d815b543444cb1eecb9305b11872b4
    - https://view.scitt.unstable.chadig.com/entry/sha384:2a939b4f24fc10aff623e5727e71f48093feef35b48583eff34058eed76cc28703494a31f40b2ef239af3c009aa1bd9b/