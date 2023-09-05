## 2023-03-05 @pdxjohnny Engineering Logs

- Vol 6: Time Travel with Us: Plotting Jumps
  - https://www.theguardian.com/science/2020/jan/11/how-astrology-paved-way-predictive-analytics
  - TODO grep here for source of following video of the graphs ends finding each other. Validate wardly paths
    - https://user-images.githubusercontent.com/5950433/222974908-2f6f1a39-e868-45f3-8460-db13d22bb7d0.mp4
- https://github.com/intel/dffml/issues/1287#issuecomment-1455147140
- [Collaboration Hub: A place for starting SC projects SocialCoding/sc-guild#2](https://codeberg.org/SocialCoding/sc-guild/issues/2)
  - `ALIGNMENT.md`
  - A guild as a type of ad-hoc organization which might be relevant during overlay application
  - Guilds, much like working groups, might have documentation they all agree on about what it alignment to their values means
    - We can then have Alice help guild members ensure their contributions stay aligned
- https://delightful.club/delightful-linked-data/#fediverse-specifications
- https://www.w3.org/TR/activitystreams-core/#extension-round-trip
- https://github.com/go-gitea/gitea/issues/18240
  - https://gitea.com/xy/gitea/issues/3
- grep Online Cloning Cuts Our Iteration Time
  - Federated repos are Online Cloning
  - As we add federated CI/CD we'll enable online overlay application
    - This lays the foundations for the automation of the vendoring process and tracking of upstream
- https://textbook.sfsd.io/overview
  - `ALIGNMENT.md`
  - https://youtu.be/hZpKdfbrd6o?t=601
    - Haven't listened to this just skimmed transcript but looks like touching on accelerating timelines
- https://community.humanetech.com/t/be-a-builder-help-improve-wellbeing-freedom-and-society/3322
- Updated thread title from [Alice Engineering Comms](https://github.com/intel/dffml/discussions/1406?sort=new#top) to [Alice Engineering Comms 🪬](https://github.com/intel/dffml/discussions/1406?sort=new#top)
- https://codeberg.org/forgejo-contrib/discussions/issues/12

![thus-begins-the-software-trade-federation](https://user-images.githubusercontent.com/5950433/222979438-19d7ef05-afc2-43f8-a7f5-6bc2240c5f11.png)

- Align DFFML CI on everything as manifest based container builds

![oci-all-the-things](https://user-images.githubusercontent.com/5950433/222979759-0dd374b2-ee5f-4cbc-92d1-5cb8de078ee8.png)

- https://codeberg.org/forgejo/forgejo/src/branch/forgejo/CONTRIBUTING/WORKFLOW.md#federation-https-codeberg-org-forgejo-forgejo-issues-labels-79349
- https://codeberg.org/forgejo/forgejo
  - > ActivityPub-based forge federation protocol https://forgefed.org/
[woodpecker-ci](https://codeberg.org/explore/repos?q=woodpecker-ci&topic=1)
[activitypub](https://codeberg.org/explore/repos?q=activitypub&topic=1)
[federation](https://codeberg.org/explore/repos?q=federation&topic=1)
[specification](https://codeberg.org/explore/repos?q=specification&topic=1)
[specs](https://codeberg.org/explore/repos?q=specs&topic=1)
[forgefed](https://codeberg.org/explore/repos?q=forgefed&topic=1)
- https://woodpecker-ci.org/docs/intro
  - > Woodpecker is a simple CI engine with great extensibility. It runs your pipelines inside [Docker](https://www.docker.com/) containers, so if you are already using them in your daily workflow, you'll love Woodpecker for sure.
- https://woodpecker-ci.org/docs/development/architecture
- https://github.com/woodpecker-ci/woodpecker
  - YAY!!!! DRONE IS BACK!!!!!!
- https://github.com/woodpecker-ci/woodpecker/pull/1543

![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg)

- Now we need to find where the woodpecker telemetry is, and figure out what needs to be aligned across that and the ForgeFed `context.jsonld`
  - https://codeberg.org/ForgeFed/ForgeFed/src/commit/467dfe84670750a61992c5c1da3841e9453c1d36/rdf/context.jsonld
- https://github.com/woodpecker-ci/woodpecker/search?q=telemetry&type=issues
  - https://github.com/woodpecker-ci/woodpecker/issues/198
  - https://github.com/woodpecker-ci/woodpecker/issues/751
- Open Telemetry -> federated event space

![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png)

- https://opentelemetry.io/ecosystem/registry/?s=activitypub&component=&language=
  - No items found
- Then we onramp into the federated ML space. Then we align training with guilds. Then we work to organize work item prioritization across entities to maximize rate of learning. Once we max out that rate of learning given all the entities working on trains of thought, that's when we've hit critical velocity.
- https://codeberg.org/forgejo/forgejo/pulls/485
  - Chaos for the Chaos God again!
    - > 26 minutes ago
  - They have two branches we need right now and this pull request aligns them
  - https://codeberg.org/forgejo/forgejo/src/commit/3caec9d9ebde243b7e4a8ee03e05b6a89aaf337e/CONTRIBUTING/WORKFLOW.md#federation-https-codeberg-org-forgejo-forgejo-issues-labels-79349
    - > [forgejo-ci](https://codeberg.org/forgejo/forgejo/src/branch/forgejo-ci) based on [main](https://codeberg.org/forgejo/forgejo/src/branch/main) Woodpecker CI configuration, including the release process.
      >
      > [forgejo-federation](https://codeberg.org/forgejo/forgejo/src/branch/forgejo-federation) based on [forgejo-development](https://codeberg.org/forgejo/forgejo/src/branch/forgejo-development) Federation support for Forgejo
- What are the existing CI events?
  - Let's see what events we get from both the webhook events rebroadcast from ForgeJo are
  - And what they would include if we also rebroadcast the events from the runner
- https://codeberg.org/forgejo/runner/issues/5
  - I was spining this this weekend as well. I see you've rebased in [forgejo/forgejo#485](https://codeberg.org/forgejo/forgejo/pulls/485)
  - Related: [forgejo-contrib/discussions#12](https://codeberg.org/forgejo-contrib/discussions/issues/12)
  - How can I help with this? My plans are currently to figure out what events are being sent from the runner that could be sent in the format of the other events using context.jsonld and update that file as needed if there are more data types that become relevant. Please let me know if this sounds aligned with your thoughts in this space or if you have any other thoughts on how best to proceed.
- We are currently in the example setup for beyond live at HEAD discussed with Andy recently at Drew's Linux Kernel meetup
  - We have an at least three branches at play just to start working on this. Trunk based development is great but we have to facilitate the enherant lack thereof across these in progress branches via virtual branches.
    - The PR which rebases `development` into `ci`
    - The wookpecker PR which adds support for forgejo
    - A new one we'll be activly working on, our virtual branch
      - Upstream
        - forgejo:federation
      - Overlays
        - forgejo:ci
          - Overlays
            - Any patches needed to rebase ci onto federation
- https://codeberg.org/pdxjohnny/runner/src/branch/federation-cd/
- https://socialhub.activitypub.rocks/t/anybody-knows-a-fediversed-market-place-software/2995
  - #1207
  - #1061
- Sic semper tyrannis
  - https://en.wikipedia.org/wiki/March_5
- TODO
  - [ ] Alice tests for please log todos
    - [ ] Split issue creation into issue body creation, create single issue
    - [ ] For test, operation to check issue body, input as static render, mock issue creation call
      - [ ] Mention in docs to update static form if need be, or switch to custom validation operation
  - [ ] Spin Federated Forge
  - [ ] Align DFFML CI on everything as container builds
  - [x] Start discussion thread on federation of CI/CD events
    - https://codeberg.org/forgejo-contrib/discussions/issues/12
  - [ ] Python Package to SBOM to Dataflow to wookpecker synthesis 
    - https://codeberg.org/ForgeFed/ForgeFed/src/commit/467dfe84670750a61992c5c1da3841e9453c1d36/.woodpecker/deploy.yml
    - https://github.com/intel/dffml/issues/1421
  - [ ] Open Telemetry -> Federated Event space
    - Analysis for addition to forge federation context.jsonld
      - Similar to gamified threat modeling, can we `alice please contribute` via PR possible transformation from the open telemetry event space. So we essentailly incrementally learn how to transform telemetry events (data flow events as telemetry events) into activitypub events. Now everything can talk directly to everything
        - GraphQL-LD over LDF
        - Cypher import of KERIVC
  - [ ] Online mirror translation into git vendor with sha384 patches as overlays
  - [ ] Federate events into traceability-interop space
    - [ ] KERIVC for protection ring -2 transport for duplicity checking