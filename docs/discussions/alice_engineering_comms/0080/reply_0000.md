## 2022-11-08 @pdxjohnny Engineering Logs

- https://arbesman.substack.com/p/-revisiting-the-world-of-simulation
- Rewatching videos to better understand how to make `did:merkle:` cached execution + an image + caching results of `alice please summarize discussion <default to alice discusion> --after "2022-10-01 00:00+0000" --before "2022-11-01 00:00+0000"` run summarization of each day (configurability on summarization of bullet point settings using Flan (🥞 EAT Me :) )
    - Not sure what to say for October monthly progress report :P
    - Pretty soon Alice can just generate herself a video and post it for us
  - https://www.youtube.com/watch?v=u2ZyqX-9xk8&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK&t=2640
    - reference to go through the http gateway for ipfs and so this is the type of thing that we're going to have the visibility into you know we would store things yeah in ipfs or we would probably actually store things in an operation which will then yield us something
- Abandoned watching the old streams of consciousness and went to didme.me
  - Ran into https://github.com/transmute-industries/verifiable-data/tree/main/packages/jsonld-schema#related-projects again
  - Found https://w3c-ccg.github.io/traceability-vocab/#VerifiableScorecard ! Which is exactly what we want for some cases (`alice shouldi`, static analysis).
  - https://w3c-ccg.github.io/traceability-vocab/#BillOfLadingCredential Can we use this for execution + content address / `did:merkle:` of inputs as described for Zephyr use case / our 2nd Part use case?
    - > A transport document issued or signed by a carrier evidencing a contract of carriage acknowledging receipt of cargo. This term is normally reserved for carriage by vessel (marine or ocean bill of lading) or multimodal transport. All B/Ls must indicate the date of issue, name of shipper and place of shipment, place of delivery, description of goods, whether the freight charges are prepaid or collected, and the carrier's signature. A bill of lading is, therefore, both a receipt for merchandise and a contract to deliver it as freight. (source: Olegario Llamazares: Dictionary Of International Trade, Key definitions of 2000 trade terms and acronyms).
    - This sounds like something that could be a compute contract as well.
    - https://w3c-ccg.github.io/traceability-vocab/openapi/components/schemas/common/BillOfLading.yml
    - Beautiful, let's roll with this and modify it into something with less names and places and more DIDs.
- IPVM
  - Meeting invite
    - > Get up-to-date information at: https://lu.ma/event/evt-0op04xDSoAUBseQ?pk=g-JBsGh2GPRyVgKwn
      >
      > Click to join: https://lu.ma/join/g-JBsGh2GPRyVgKwn
      >
      > Event Information:
      >
      > This call is open to all, but is focused on implementers, following the IETF's rough "consensus and running code" ethos.
      > The IPVM is an effort to add content-addressed computation to IPFS. The requires specifying calling convention, distributed scheduling, session receipts, mobile computing, and auto-upgradable IPFS internals.
      > Links
      > - Community Calls 
      > - GitHub Org
      > - Discord Channel 
      > - IPFS þing '22 Slides
  - https://fission.codes/blog/ipfs-thing-breaking-down-ipvm/
  - https://twitter.com/pdxjohnny/status/1574975274663706624
    - > FISSIONCodes: You've heard of 
[@IPFS](https://mobile.twitter.com/IPFS), but what about IPVM? Fission is working on the Interplanetary Virtual Machine - a way to add content-addressed computation to IPFS. 🤯 With content-addressed computation we can work more efficiently and save time and compute power, all while operating in the decentralized web.
    - > John: With regards to bindings and interface discussion. The Open Architecture currently is looking at software definition via manifests and data flows. Dynamic context aware overlays are then used to enable deployment specific analysis, synthesis, and runtime evaluation. This allows for decoupling from the underlying execution environment (i.e. WASM). Traversing metadata graphs on code from remote sources allows for orchestration sandboxing to be dynamic, context aware configurable, and negotiable for the execution of compute contract. This methodology is work in progress. Binding generation (syscalls, etc.) should follow the same overlay enabled pattern. Calling convention here is effectively the (Credential) Manifest.
      - https://github.com/intel/dffml/blob/alice/docs/arch/0009-Open-Architecture.rst
      - https://intel.github.io/dffml/main/about.html#what-is-key-objective-of-dataflows
  - [2022-11-07 Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4073154)
    - @marc-hb Zephyr example
      - Let's say I care about, git version ,tool chain version, various .config
        - https://github.com/zephyrproject-rtos/zephyr/pull/51954#issuecomment-1302983454
      - I track those for reproducibility (and caching) information
      - DID based content addressable solution possibility
        - When I want to generate a content addressable build I take all those JSON files (which are the generic graph serialization of all the stuff you care about) you concat and checksum which for a graph of DIDs is `did:merkle:`.
          - Side note: Could do root of Open Architecture upstream could be referenced as as `did:merkle:`. So Alice's state of the art value for upstream on `Architecting Alice: An Image` would be `upstream: "did:merkle:123"`
  - [2022-11-02 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4037309)
    - Demo metric scan with SCITT receipt used to auth upload results to HTTP server (stream of consciousness / webhook server). Root trust in OIDC token similar to fulcio/sigstore github actions slsa demo.
    - Future
      - [ ] Demo demo to OpenSSF Metrics WG for collaboration on DB
      - [ ] Do this for each `Input`
      - [ ] Instead of HTTP server the context addressable registry
      - [ ] Link via DWNs
      - [ ] Hardware rooted keys
      - [ ] Kinit above together with a `I/L/R/OP/OPIMPNetwork`s for distributed compute
      - [ ] Trust anchors of other than self support
      - [ ] Caching
  - Can we build a quick demo this morning on top of
    https://github.com/imjasonh/kontain.me for discussions sake?
  - https://go.dev/learn/
    - https://go.dev/doc/install
    - https://go.dev/doc/tutorial/getting-started
    - https://go.dev/doc/modules/managing-dependencies#naming_module

```console
$ git clone https://github.com/imjasonh/kontain.me
$ cd kontain.me/
$ export GO111MODULE=on
$ export GOPROXY="${HTTPS_PROXY}"
```

- QUIC
  - https://youtu.be/Dp6FwEfkBqQ
  - https://youtu.be/wN9O1MnxIig
- MC Alice
  - https://www.youtube.com/playlist?list=PLtzAOVTpO2jYzHkgXNjeyrPFO9lDxBJqi

```console
$ youtube-dl --no-call-home --no-cache-dir -x --audio-format mp3 --add-metadata --audio-quality 0 --restrict-filenames --yes-playlist --ignore-errors "https://www.youtube.com/watch?v=Bzd3BjXHjZ0&list=PLtzAOVTpO2jYzHkgXNjeyrPFO9lDxBJqi"
```

- Aghin already got us started webhooks!
  - https://intel.github.io/dffml/main/examples/webhook/index.html
    - > Aghin, one of our GSoC 2020 students, wrote operations and tutorials which allow users to receive web hooks from GitHub and re-deploy their containerized models and operations whenever their code is updated.
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
- TODO
  - [ ] Update `Architecting Alice: Stream of of Consciousness` using webhook demo as upstream.