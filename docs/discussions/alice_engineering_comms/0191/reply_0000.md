## 2023-02-27 @pdxjohnny Engineering Logs

- Where are we
  - Event
  - ActivityPub
  - Query (jq + cypher)
  - Validation (schema enum)
  - Alice or other for extra data mining if not in graph. DFFML is just a Python onramp/offramp helper.
    - Event
- https://github.com/probot/probot/blob/master/docs/deployment.md
  - This watches the ActivityPub group
  - This enables misc bots within the org to provide real time cross-repo feedback
    - Bot that knows a lot about one repo can provide upgrade path help as users work through issues updating in downstream repos
    - Bot is just the policy as code within the upstream, which says, how to help downstream in these situations
      - Example:
        - Upstream
          - https://github.com/behaviorbot/request-info
        - Overlay
          - If issue created by `alice please log todos`
        - Orchestrator
          - GitHub Actions
            - Trigger flow
              - Tertiary OSS -> activitypub extensions for security.txt -> ActivityPub Actor -> ActivityPub Follow ActivityPub Actor Watcher
- https://github.com/probot/smee-client
  - Same as wait for message, only more similar to our setup, we want to make the protocol between this and it's server ActivityPub, so that it's a defined spec and we can traverse and import export from the graph
    - We want data security to be handled at the graph level
    - Data propagation can also be handled at that level
      - Ref SCITT use case
      - Policy as code, who my why this message should be propagated
- We're adding the extra layer of ActivityPub so that we can stay loosly coupled
  - Focus is on modifying (adding more links / layers) and querying data in graph
  - On/ramp off ramp to web2 land
    - GitHub Accounts/Apps which watch the graph event stream and decide if they want to take data given as `Input(value=graph_node_content_resolved_from_registry, definition=manifest schema link from content field of node this input is inReplyTo)` and turn it into a pull request
      - An operation
  - opt-in, heterogeneous, poly repo
- https://github.com/ietf-scitt/statements-by-reference/pull/1/files
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/12
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/11
- https://github.com/in-toto/demo/blob/main/owner_alice/create_layout.py
- https://techcommunity.microsoft.com/t5/azure-confidential-computing/developers-guide-to-gramine-open-source-lib-os-for-running/ba-p/3645841
- https://gramine.readthedocs.io/en/stable/quickstart.html
- https://gramine.readthedocs.io/projects/gsc/en/latest/#configuration
  - Distro of `ubuntu:20.04` to mono base image for actions runner?
  - https://hub.docker.com/_/mono/
- `print(user.__pydantic_model__.schema())`
  - For auto schema creation from data model
  - https://docs.pydantic.dev/usage/dataclasses/
- For our rolling stages we could just take all the output operations,
  copy the dataflow with just them, make them processing stage, and run
  them as a subflow. Right now we only iterate once, aka one execution
  loop for the output operations, they aren't chainable.
  - With this rolling stage approach we can easily cypher query over the previous stage
    - We could also explore within stage (operation) cypher query over the
      JSONLD/manifest synthesis to the graph from cache save/load, or it's in memory form.
  - #1388
    - Related: Gatekeeper/Prirotizer

https://github.com/intel/dffml/blob/1d071ea82af93a15b6559639f223c64b7f356bf6/dffml/df/memory.py#L1976-L1979

- Fundamentally Alice is helping us with dependency review, that promotion, cross of trust boundary, from 3rd to 2nd party
  - She helps us decide if they are up to the level of requirements we have for running within the 2nd party https://en.wikipedia.org/wiki/Protection_ring, but since we're and open source project, the ring we are protecting is related to the downstream threat model
    - Tie back in with our recent CVE Bin Tool meeting
    - The protection rings in this context are a level of riskyness this system context (the distro, ML distro in DFFML case) exposes you to
      - Cartographer extrodinare
- https://github.com/intel/dffml/issues/1418
  - Updated with reference to activitypub security.txt
- Dataflows produce clean deltas (commits)
  - Beyond the unit of the line as granularity for change
  - Application of overlay tells you the code change on upstream (like for backporting)
- TODO
  - [ ] Read Roy and Steve's doc
  - [x] Schedule meeting with Sam
    - KERI Watchers as SCITT