## 2023-11-20 @pdxjohnny Engineering Logs

- https://github.com/abi/screenshot-to-code
  - Screenshots as a universal API
- Where are we
  - We’re ready to introduce the foundation of our decentralized trusted event driven architecture for Alice into the SCITT architecture.
  - We have prototyped and demo’d successfully use of an existing well adopted Federation protocol (W3C ActivityPub) to ensure SCITT instances have the opportunity to accept statements into other logs.
    - As Jon G mentioned, SCITT allows us to define our own (aka any) reality. Alice of course is interested in this.
    - Definition of ones own reality is how we’ll get each instance of AI (Alice Intelligence) to declare what is it’s understanding of its operational context, aka system context.
    - As we know the truth is in you and the truth is in me but the truth maybe be a little bit different between us. Both truths are valid. Truth is context dependent.
- What do we want
  - We seek to enable N agents to effectively collaborate in a poly repo environment where agents have distinct roles and permissions.
- What are we doing
  - It is now time to turn our attention back to the bits and bytes of the software supply chain.
  - We will provide blueprints (Quart) which turn hosted VCS webhook events into SCITT statements and subsequently receipts.
    - Why do we need SCITT for this? Why can’t we just use ActivityPub or some other event stream?
      - We must ensure events are independently verifiable offline at a later date. We will likely purge old events from the federated outbox and need to be able to verify their authenticity at a later date. The creator of the event may not care to save it. But a downstream consumer might.
  - We will hook each 2nd party repos webhook events and our first party repo DFFML to those event receivers.
  - We will instantiate instances of Alice who will iterate on their pull requests across the poly repo environment, using the new data events provided by SCITT.
  - We’ll publish new SBOMs on commit.
  - We’ll use vulntology and VEX to create ad hoc issues and resolutions across the federated event space.
- Where are we going
  - Towards a generic method for escaping the sandbox ;)
- https://github.com/securefederatedai/openfl/pull/892
- https://github.com/pyt-team/TopoModelX/blob/9586e2dd15057504f6bc669265b3a6621f6c6d65/tutorials/hypergraph/hnhn_train.ipynb#L4
- https://github.com/iMoonLab/DeepHypergraph
- https://github.com/scitt-community/scitt-api-emulator/blob/1360f3658a697ce8a013f28721a298fca9915dc8/scitt_software_supply_chain_middleware/github_webhook_notary.py

![hash-values-everywhere](https://user-images.githubusercontent.com/5950433/230648803-c0765d60-bf9a-474a-b67e-4b4177dcb15c.png)

[![asciicast-federation-as-firewall-1](https://asciinema.org/a/622103.svg)](https://asciinema.org/a/622103)

- TODO
  - [x] Get federation test cases working
    - https://github.com/scitt-community/scitt-api-emulator/pull/37
  - [ ] Train Alice America on JFK
  - [x] Ensure federation signaling can run policy engine
  - [x] Confirm GitHub Webhook Notary creates accurate SHA384 in-toto SLSA evidence on new commit push events
  - [x] Demo for GitHub Webhook Notary without policy engine
  - [ ] Demo for GitHub Webhook Notary with policy engine
    - Focus is on ING-4, triggering what is effectively a mirror update
    - Repo configured to send push events to `GitHubWebhookNotaryMiddleware` endpoint of Bob
    - Bob has insert policy `*`
    - Alice follows Bob
    - Alice has insert policy whose engine only triggers when it has determined there are no known vulns. sbom from github plus cve bin tool scan to do so. or shouldi dataflow
    - Eve follows Alice. Eve executes a repository dispatch event to trigger a fetch and push to the mirror.
    - Do this on example upstream repo `tree` and mirror repo `apple`
    - Later do this for the DFFML repo into the DFFML org
    - This demo forms the basis for what is our generic architecture for context awake trust