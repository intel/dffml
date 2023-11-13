## 2023-11-10 @pdxjohnny Engineering Logs

- Cristy: Don't make me thumbprint a machine for door access
  - Moral: Make sure we don't introduce any security or privacy issues at large along our quest for transparency
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/79#issuecomment-1797016940
    - It could be interesting for SCITT services to declare federation protocols they support via exported service parameters. Different instances my have different threat models and require different levels of assurance around CIA properties of federation protocols.
- Let's get the decentralized event loop running across the poly repo space
  - https://docs.dagster.io/_apidocs/
    - https://docs.dagster.io/_apidocs/libraries/dagster-pipes
    - https://docs.dagster.io/deployment/run-coordinator
      - https://docs.dagster.io/_apidocs/internals#dagster._core.run_coordinator.QueuedRunCoordinator
    - https://docs.dagster.io/_apidocs/internals#executors-experimental
    - https://docs.dagster.io/_apidocs/assets
- Initial update of SCITT API Emulator `scitt.create_claim` to match arch PR merge https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/commit/a4645e4bc3e78ad5cfd9f8347c7e0ac8267c1079
  - https://github.com/scitt-community/scitt-api-emulator/commit/61bcf5dd74dc802d1c0df2719c48756a464c715a

[![asciicast-scitt-api-emulator-cwt-update](https://asciinema.org/a/620307.svg)](https://asciinema.org/a/620307)

- https://pages.nist.gov/metaschema/specification/overview/
  - A.J. and Dave’s method for world domination, plus SWID BOM
- TODO
  - [ ] Need SCITT alignment items before end of IETF 118
    - [ ] https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/79#issuecomment-1797016940
      - [ ] We need to have an open line of discussion around how to ensure we have side-channelless channels where possible for federation. We don't want the same type of issue Chris Lemmons was talking about with WIMSE composite claims
    - [ ] https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/96
      - [ ] We need to figure out what service parameters are exported and how
    - [ ] SCITT API Emulator updates
      - [ ] SD-CWT
        - https://or13.github.io/draft-steele-cose-hash-envelope/draft-steele-cose-hash-envelope.html
        - https://github.com/OR13/draft-steele-cose-hash-envelope
        - https://datatracker.ietf.org/doc/html/draft-birkholz-cose-cometre-ccf-profile-00
        - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/pull/123/files?short_path=585fb42#diff-585fb424519b79cf000445f3425fa56d328cbaca5d2a622740ddc4e5ca91dbe1
        - https://ietf-wg-scitt.github.io/draft-ietf-scitt-architecture/draft-ietf-scitt-architecture.html
        - https://github.com/ietf-scitt/draft-birkholz-scitt-scrapi
        - https://github.com/dajiaji/python-cwt
        - https://python-cwt.readthedocs.io/en/stable/claims.html
        - https://github.com/TimothyClaeys/pycose/blob/master/pycose/headers.py
        - https://github.com/scitt-community/scitt-api-emulator/pull/39
  - [ ] Scripted spin up of emulator
    - https://github.com/digitalocean/do-agent/issues/305