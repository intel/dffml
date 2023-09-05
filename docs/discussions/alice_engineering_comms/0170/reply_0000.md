## 2023-02-06 @pdxjohnny Engineering Logs

- https://huggingface.co/BridgeTower/bridgetower-base
- https://github.com/isl-org/generalized-smoothing
- https://open.substack.com/pub/cameronrwolfe/p/imap-modeling-3d-scenes-in-real-time
  - Streaming code/recent context-to-context transitions -> Alice Vol 1/2 Cartography
    - Tick/tock context equilibrium for strategic principles for all active strategic plans / subcontexts of top level system context (strategic plan good/bad, go/nogo)
    - A Shell for A Ghost
      - Stream of consciousness inference
        - Avoiding bad paths by preemptive subliminal good path recommendations
          - Example: Type ahead text completion which validates intent in a dynamic context aware way. Could end up rewriting back as it learns more intent with each word. Intent requires context to capture. Execution of hypothesised paths via our shared CI/CD and AI comms unification (#569 but as infra used for streaming, SSI/DWN, infra as protocol)
            - whisper | grep engineeringlogstreams 'Context aware communication'
- https://social.treehouse.systems/@ariadne/109808644259234008
  - > an exciting idea would be to provide a mapping interface between cryptographic identifier (DID) and petname using something akin to bittorrent DHT.  i see no reason why kademlia could not support that. [...] conceptually, you can think of rapunzel's ring logs in a lot of the same ways as you might think of git.  they are heavily inspired by git.
    - How do we get these approaches to be interoperable? How similar are they? Can we just go right to that, is it still worth doing to provide a path to that migration from Fediverse to OS DecentrAlice? If we can do everything as DID and VC then SSI service +/ DWN should be enough for streaming the knowledge graph.
    - Our plan was to hybridize endor with activitypubsecuritytxt
      - This seems like the right plan still
      - Let's do this as the follow on the the 2nd party split out
      - Ariadne is at chainguard so perhaps will have a sigstore/rekor based implementation, our goal is to drive interoperability between that and the SCITT model. Being able to jump from rekor (centralized) to SCITT (decentralized) enables simplified dev/test/ci/cd setups between entities and orgs due to the ability to graph trust chains into respective environments (think cert pinning).
        - This allows for the creation of per system context trust chains
          - #1400
- #1315
  - Alice is fundamentally about closing the feedback loop within a decentralized supply chain.
    - Ensuring that it's a secure feedback loop
    - [2020-12-08: examples: swportal: Add example (in 0.4.0)](https://github.com/intel/dffml/commit/2e42032e0a0872ef75a0920578746d0880b9cb70)
      - This frontend effectively becomes feed by the same graphs that feed Alice's Analysis which happens at the center of the Entity Analysis Trinity
        - This is our mental model, our UI
          - This UI becomes integrated as needed
          - Context aware communication based on inference intent
          - On demand supply chain fulfilment to that intent
- Versioned learning checkpoints via graph query plus schema validation pass (or open policy agent for policy manifest ADRs)
- https://slsa.dev/spec/v0.1/threats
- For registry of PyPi packages across 2nd party plugins for PR builds we need to have container build manifests running builds with alternate PYPI registries applicable to the graphed contexts relevant to downstream flows.

**registry_manifest_build_args.json**

```json
[
    [
        "PYPI_REGISTRY",
        "https://localhost.run/temp/"
    ]
]
```

```console
$ BUILD_ARGS=$(jq .inputs.build_args < "${GITHUB_EVENT_PATH}" | jq -r | jq -r '.[] | ("--build-arg " + .[0] + "=" + .[1])')
$ BUILD_ARGS=$(jq -r '.[] | ("--build-arg " + .[0] + "=" + .[1])' < registry_manifest_build_args.json)
$ python -c 'import sys; print(sys.argv)' $BUILD_ARGS
['-c', '--build-arg', 'PYPI_REGISTRY=https://localhost.run/temp/']
```

- TODO
  - [ ] **TODAY** https://blogs.python-gsoc.org/accounts/login/?next=/en/suborg/application/new/
  - [ ] https://github.com/pdxjohnny/activitypubsecuritytxt based CD
  - [ ] https://botsin.space/@agora
    - Agora to view instead of openlineage
    - https://github.com/flancian/agora-server
    - https://github.com/flancian/agora#welcome-to-the-agora-v05
    - https://github.com/flancian/agora-bridge
      - https://github.com/flancian/agora-bridge/tree/main/bots/mastodon
- Future
  - [ ] https://time.crystals.prophecy.chadig.com
    - Respond to Orie https://twitter.com/OR13b/status/1621907110572310528
      - Actor `acquire`
        - `attachments` `Link` to `activitypubextensions` thread
        - `content: "activitypubextensions"` thread
          - `inReplyTo: "$activitypubextensions_thread", content: "https://time.crystals.prophecy.chadig.com/bulk.1.0.0.schema.json"` thread
            - This becomes analogous to shared stream of consciousness uniform API for submitting across contexts (Manifests).
              - CI/CD across projects with different orchestrators for downstream validation of the 2nd and 3rd party plugin ecosystem.
                - This facilitates communication across pipelines across repos across PRs so we can use versioned learning to promote across trust boundaries (3rd party to 2nd party or support level 2 to 1)
                - #1207
                - #1315
                - Alice helps us see risk over time, this is where we see Coach Alice, cartography used applied to dev branches, we grow closer to distributed compute with this, as iteration time is on dev branches rather than release or main
                  - This will probably be part of Alice and the Health of the Ecosystem
      - Ask him to reply to `@acquire@time.crystals.prophecy.chadig.com`
        - Thoughts OR13b?
    - ActivityPub Actor watches for messages replying to certain threads
      - https://github.com/pdxjohnny/activitypubsecuritytxt
    - Actor creates pull request to https://github.com/OR13/endor style repo
      - Actor creates didme.me and gets VC SCITT receipt for associated `did:pwk:` (committed into Endor fork, he'd used git as database)
        - This could also be our content address of something in oras.land
        - In the AI training data/human case we see the input data (meme) validated via SCITT
          - We want to enable application of policy to data set ingestion, because this will happen in MLOps aka CI/CD
           - Workstream: AI Ethics
        - In the CI/CD use case, we see the input data (manifest referenced content, images, packages, metrics data output `FROM scratch` OpenSSF metrics use case) validated via SCITT.
        - Later we build up the threat modeling for the dynamic analysis portion of Alice which plays with input data as changes to repos and connects more of our Data, Analysis, Control for the software development process.
      - Actor replies to Orie's reply with his receipt for his time crystals.
    - For k8s style or OS DecentAlice style deployments (OSS scanning feeding OpenSSF metrics) we could run the graphed trust / event chain to a sidecar ActivityPub Actor / root of trust.