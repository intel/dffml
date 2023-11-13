## 2023-11-13 @pdxjohnny Engineering Logs

- https://github.com/transmute-industries/dune
- TODO
  - [ ] Demo using SBOMs and VEX on SCITT, ideally with threat model, by 12:00 PST, 15:00 EST for OpenVEX call
    - https://github.com/openvex/spec/issues/9
  - [ ] SCITT ActivityPub Actor registration could be allowlisted based on OIDC protected endpoint
    - Allowlist of reusable workflows could be maintained as JSON/YAML/TOML within secrets
  - [ ] Connect with A.J. this week about getting federated events of NIST NVD data
    - Current plan is leverage `cve-bin-tool.cvedb` to turn polling NIST NVD into statements, federated statements become our polling -> eventing bridge
      - https://github.com/intel/cve-bin-tool/blob/5f87bd4863936c7a44f06bf2bd171d94d02b7f55/cve_bin_tool/cvedb.py
      - https://docs.joinmastodon.org/methods/push/#create