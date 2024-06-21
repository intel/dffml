## 2024-06-18 @pdxjohnny Engineering Logs

- Poly repo virtual branches: https://github.com/intel/dffml/blob/main/docs/discussions/alice_engineering_comms/0090/reply_0001.md
- https://security.apple.com/blog/private-cloud-compute/
  - https://www.rfc-editor.org/rfc/rfc9474.html
    - > This document specifies an RSA-based blind signature protocol. RSA blind signatures were first introduced by Chaum for untraceable payments. A signature that is output from this protocol can be verified as an RSA-PSS signature.
- https://machinelearning.apple.com/research/introducing-apple-foundation-models
- https://github.com/gramineproject/examples/tree/master/pytorch
- https://github.com/confidential-containers/enclave-cc/
- https://git-scm.com/docs/git-bundle
- https://github.com/intel/dffml/issues/1287
  - Upstream First Development in Federated Software Forges
- https://github.com/danny-avila/LibreChat
- Why decentralized CI/CD?
  - Want to be able to volunteer up units of compute for priority in orchestrator dispatch queue.
- TODO
  - [ ] Rebase request as a function of forgejo, functions to request a rebase of a branch from an active PR. The rebase request shows up against that PR, it might have rebased in upstream or remotes tracked via a virtual branch. This will help with 2nd party poly repo validation covered in #106
  - [ ] `cve-bin-tool-parsers-ossf` see if OpenSSF WGs define a set of scanners for open source projects anywhere and make that metapackage install the 2nd party set of packages maintained by openssf or trusted
  - [ ] Send bengo ActivityPub event on scitt entry