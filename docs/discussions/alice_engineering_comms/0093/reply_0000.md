## 2022-11-21 @pdxjohnny Engineering Logs

- https://github.com/CrunchyData/pg_eventserv
  - `FROM` rebuild chain pdxjohnny/dffml-operations-dockerhub@a738c35199afe82d8a35d97ce16711c6f19785c5
- Going through old repos to look for logcat server
  - Found a bunch of code I forgot I wrote and is referenced in Alice thread as deps
  - https://github.com/pdxjohnny/webrtcvpn
  - https://github.com/pdxjohnny/diffstream
  - https://github.com/pdxjohnny/telem/blob/8676810086c732e1a738ce58a6296993f7a87661/client/c/encrypt.c
  - https://github.com/pdxjohnny/hack
    - Looks like this packs shellcode for `exec` system calls on linux
      - [![hack-the-planet](https://img.shields.io/badge/hack%20the-planet-blue)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#hack-the-planet-)
    - Ref shim
  - https://github.com/pdxjohnny/freeze-tool/tree/master/logger
    - Stream logging / cross this with telemetry one
  - https://github.com/pdxjohnny/video_chat/blob/master/image_video.js#L95
    - This comes in handy with VNC over PNG/JPEG etc. when massive hax are required
  - https://github.com/pdxjohnny/pysync/blob/master/sync.py
    - :grimacing: (cve-bin-tool vlcn-io/cr-sqlite bellow in TODO, been at this a while too)
- https://github.com/oras-project/oras-py
  - https://github.com/opencontainers/distribution-spec
    - Inventory?
      - https://github.com/opencontainers/distribution-spec/blob/main/spec.md#enabling-the-referrers-api
        - https://github.com/intel/dffml/pull/1207#discussion_r1026981623
    - Stream of Consciousness?
      - Might already have websub or equivalent, implementation / ratification status was unclear, dig more investigate Open Architecture encoded (autocodec, multiformat, shim, custom basic, unencoded json, etc.) callback enabling.
  - OCI distribution spec all the things
    - Python packages
    - SBOM
    - VEX
    - SCITT

![OCI distribution spec all the things meme](https://user-images.githubusercontent.com/5950433/203143783-b7f9e731-80bd-42c7-b97d-410d62676758.png)

- Last Friday pushed alice: threats: vulns: serve: nvdstyle: Fix serving of v2 style CVEs - 9f0a41ad55bdc7f295c435ebd51db77e3343b915
  - We can now start serving threats!
  - Need to finish out the contribution to CVE Binary Tool first
    - https://github.com/intel/cve-bin-tool/issues/2334#issuecomment-1315643093
- Found Distributed Android Testing pre-squash real initial webhook commit
  - Jul 27, 2015 - 7130e89473f12353f19afb935802b065759be571
    - > A webserver to receive json web hooks from gitlab_webhooks
      > The hooks are dealt with by calling the corresponding function in
      > hooks.py. For example a push is received so the function push in
      > hook.py is called and passed the hook data.
  - Well friends, it's only been 2,674 days since our first commit down CI lane.
    - Next step is we enable offline, offline CI that is, we'll knit together our
      Data, Analysis, Control (DAC, aka Digital Analog Converter ;) loop that will
      get our software lifecycle analysis going. We're going to look at the supply
      chain of the thoughts (adding / using a dependency is a thought, it might also
      be a thought you took action on). You are what you EAT and same goes for software!
      Our analysis of the supply chains to our trains of thought seen within the
      software lifecycle are analogous to the software project as the entity and our
      analysis of what it's EATing is an analysis of it's digestion of those thoughts.
      Okay I think I wrote this somewhere else and I'm not having success explaining
      right now. It's also not so much offline CI as parity across environments, enabling
      context (process, workflow, DX) aware application of policy / config / logic.
      Aka the intermediate representation and the analysis pattern allow for translation.
      As we get more advanced we'll be leveraging (and implementing) our cross domain
      conceptual mapping (grep thread) techniques to translate these applications ad-hoc
      as feasibility and need allows.
      and our EAT wheel will start turning.
      - [WIP: Rolling Alice: Coach Alice: You are what you EAT!](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-3885559)
      - This offline digestion is important to enable us to give Alice to developers
        and help her sit side by side to help them. Today we focus on vulns, and
        security patches (version bumps?, `safety` check? - https://intel.github.io/dffml/main/shouldi.html#use-command). Tomorrow might be linting
        (`yamllint` for GitHub Actions).
      - Using the NIST NVD style API we now have we can begin to issue events over that
        stream.
        - These events will be the communication of Alice's thoughts and actions, her
          development activity. We'll of course incrementally introduce overlays which
          increase sophistication of activities and intricacy of communications and
          triggers.
- TODO
  - [ ] For the meeting recording to markdown / rST we need to also screenshot if there is a deck presented
  - [ ] Contribute NVDStyle pieces to cve-bin-tool as needed for https://github.com/intel/cve-bin-tool/issues/2334#issuecomment-1315643093
    - [ ] SCITT receipts for each CVE (attached as separate record? attached within? wrapped?)
  - [ ] [download_nvd](https://github.com/pdxjohnny/download_nvd) but somehow hybridized with https://github.com/vlcn-io/cr-sqlite for conflict free resolution deltas on the CVE Binary Database.
    - Or maybe go the bzdiff route
  - [ ] Finish scorecard demo and intergate into shouldi
    - Put this in down the dependency rabbit hole again as one of the things we put in `THREATS.md`
  - [ ] `alice threats cicd` (`-keys https://github.com/intel/dffml`)
    - [ ] GitHub Actions workflow analysis overlays
      - [ ] Look for `runs-on:` and anything not GitHub hosted, then
            check `on:` triggers to ensure pull requests aren't being run.
        -  https://github.com/intel/dffml/issues/1422
    - [ ] Output to JSON source (so long as we derive from `RunRecordSet` we'll be done with this)\
    - [ ] Have NVDStyle server take source as input/config so that we can point it at the discovered vulns
  - [ ] Track https://github.com/intel/cve-bin-tool/issues/2320#issuecomment-1303174689
        in relation to `policy.yml`
    - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#what-is-alice
  - [ ] `alice please log todos -source static=json dynamic=nvdstyle`
    - [ ] Implement source for reading from NVDSytle API (op source for single function prototype?)
    - [ ] Enable creation of TODOs by overlaying operations which take the feature data as inputs (use dfpreprocess?)