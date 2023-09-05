# 2022-09-28 Engineering Logs

- Self-Sovereign Identity Service
  - https://github.com/TBD54566975/ssi-service/tree/main/sip
- https://lu.ma/ipvm
  - Tuesday, October 11, 2022 9:00 AM-10:00 AM
  - > ​This call is open to all, but is focused on implementers, following the IETF's rough "consensus and running code" ethos.
    >
    > ​The IPVM is an effort to add content-addressed computation to IPFS. The requires specifying calling convention, distributed scheduling, session receipts, mobile computing, and auto-upgradable IPFS internals.
    >
    > - ​Links
    >   - ​[Community Calls](https://github.com/ipvm-wg/spec/discussions/categories/community-call)
    >   - ​[GitHub Org](https://github.com/ipvm-wg)
    >   - ​[Discord Channel](https://discord.gg/eudkhw9NQJ)
    >   - ​[IPFS þing '22 Slides](https://noti.st/expede/oq0ULd/ipvm-interplanetary-vm)
    >
    > > ​Wasm modules, their arguments, intermediate states, their outputs, and managed effects can be described as IPLD graphs. IPVM is a strategy to support generalized deterministic computation in a serverless style on top of IPFS with optional side-channel matchmaking on Filecoin, and extend the same benefits of shared data blocks to computation.
- GitHub Actions for downstream validation of 2nd party plugins.
  - Issue: Need container images running for some (`dffml-source-mysql` integration tests).
  - Use DERP to join running actions jobs.
  - Use privilege separation of two user accounts.
    - Credit to Matt for this idea came up with trying to make API token permission delegation more granular than what is currently supported, same role based copy user scheme.
  - Everything is terraform templates (coder, k8s), dockerfiles and actions workflows (coder setup-ssh and then do port forwarding, now you can spin up anything).
    - Those can all be described as dataflows and synthesized to
      - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_forward.md#supply-chain-security