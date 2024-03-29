When your top level system context is looking at a DID to run dataflow within it. It should:

- Have an overylayed dataflow which understands the DID format, and is looking to parse it.
  - Means we should have a strategic plan in place which calls to the shim operation (make it an operation) and can be directed via flow to take any input matching specific definitions or origins and attempt to convert it to a plugin instance. This is essentially shared config.

---

- https://github.com/hyperledger/aries-rfcs/blob/main/features/0023-did-exchange/README.md
- https://identity.foundation/peer-did-method-spec/#layers-of-support
- https://github.com/hyperledger/aries-rfcs/blob/main/concepts/0003-protocols/README.md#piuri
- Found out that hyperledger has firefly project, similar to DFFML, but in go, no ML that we can see so far
- https://crates.io/crates/transact
  - DataFlows should be interoperable with hyperledger transact

---

- `join_meeting | obs youtube && youtube stream active link | tee >(tweet https://twitter.com/path/to/thread) >(gh discussion comment))`
  - We already have some shell parsing in consoletest, could we implement shell to dataflow.
  - This would allow for definition where we can use the subprocess orchestrator PR (never got merged, go grab) to run commands. We effectively implement a shell. This would also help with our fully connected development. We just are the shell. This would allow for running shell commands where daemons are just opimps that stay around and bash funtions are method on dataflows as classes
- TODO
  - Talk to Marcela about hyperledger transact and if there is any k8s integration she knows about planned
- https://www.sciencedirect.com/science/article/pii/S2096720922000136
  - Privacy preserving Supply Chain implemented on fabric
    - Extend and translate to transact to leverage new web3 concepts such as DIDs off the bat.
    - They are looking at state: https://github.com/hyperledger/transact-rfcs/pull/12
- Hyperledger Supply Chain SIG
  - Somehow engage as users or members. Cross with OpenSSF streams to work on blockchain supply chain security.
  - This is criticial because blockchains and DIDs easily translate into our open source ecosystem as a whole being a polyrepo development environment. Think grafting = forks. Central Comms = Blockchain (where do I find the chat server? is the chat server blockchain based? maybe?).
  - https://github.com/Indicio-tech/did-indy-demo
  - https://github.com/Sirius-social/didcomm-mediator
    - Mediator is 
  - https://github.com/hyperledger/aries-cloudagent-python
  - https://wiki.hyperledger.org/display/aries
  - https://hyperledger.github.io/firefly/overview/
    - Firefly using aries or transact where we plugin into their orchestrator concept
    - Then can leverage chain to chain network interoperability imminent due to recent tooling to connect us to Hyperedge Supply Chain solution - Grid, which does not yet look as if it supports DID based chains directly. Should probably look at roadmap first to see if time it takes to implement grafting/proxies/multi-network infra setup in parallel is comparable to their roadmap for direct support of DID based chains.


![image](https://user-images.githubusercontent.com/5950433/167244462-ed30727c-4951-4e3e-a4e6-3bc0cf683362.png)

- https://hyperledger.github.io/firefly/overview/data_exchange.html
  - https://github.com/hyperledger/firefly-dataexchange-https
  - Can implement data transfer over input network because data exchange supports transfer over arbitrary mechanisms.
- https://hyperledger.github.io/firefly/reference/firefly_interface_format
  - Looks like dataflow / manifest
  - https://github.com/hyperledger/firefly-dataexchange-https/releases/tag/v1.0.0
    - Release is 7 days ago, woohoo!

---

- Declare and define term: state of the art
  - State of the art = leaf node in train of thought = bleeding edge = volume 2 the most accurate GAN for creating artwork of strategic plans (i.e. artwork created from the bleeding edge system context, the state of the art)
  - Tag `STATE OF ART` will be joined with a `YYYY-MM-DD` format date via a `:` to denote what the most up to date thinking from an agent when publishing strategic plan assessments of the state of the art believes to be the state of the art as compared to publications from other nodes. When this tag is viewed on update to thought process data (comments here) other agents should detect that the original agent thinks they have advanced the state of the art and adjust their strategic plans accordingly. This is how we have a distributed network of agents utilize active learning to actively sandbox / defend themselves from undesirable (untrustworthy, errors) inputs.
- STATE OF ART: 2022-05-07
  - We will 
- Determined that if we use DIDs we'll have out of the box interoperability with hyperledger firefly and grid solutions.
  - We would like to understand the format of the data as it exists within a did/did doc on one of those chains. We want to do this because we want to take the cold storage of the chain (all the DIDs) and be able to save / load that into `Input` objects via operations calling `InputNetworkContext.add()` after being run on dataflow as class context entry, so as to watch chain for new inputs and filter for ones applicable for running contexts.
- Plan
  - Spin up example DID based chain using firefly.
  - Dump to cold storage (file).
  - Inspect all records in chain (look at the dumped data within the file).
  - Understand how each record maps to what is seen or unseen in the firefly explorer UI.
  - Attempt to generate inputs using execution of dataflow with values matching what existing in data stored on chain from firefly example chain data.
  - Write operation which runs on output which grabs all inputs within inputs network and serializes them to the format that they dumped example is in.
    - Build on what we found with peerdid
    - https://github.com/pdxjohnny/dffml/blob/0404b6dc449658ea4ecb324c8f4f5522b1a438a7/operations/peerid/dffml_operations_peerid.py
  - Attempt to import chain from newly created dump.
    - Confirm via firefly UI that we are looking at equivalent data with different keys having signed.
- Down the line maybe kcp running something with https://hyperledger.github.io/firefly/tutorials/custom_contracts.html#create-a-blockchain-event-listener to use that instead of HTTPS to accept incoming specs for CRDs.
  - Listener within / alongside kcp acts as web2/web3 proxy where web2 is the kubernetes API server.
    - This proxy service on start will kick off DFFML to either
      - kick off operation to deploy firefly supernode (or blockchain node? on kcp cluster? configurable with dataflow)
      - start listening itself for DIDs incoming converts them into k8s specs to call job subclass CRDs which we define via templates created from operation type information given via input/output defintitions and config as dataclass with soon to be unified python typing and defintion approach. alternate transport mechanisams could be dataflow which triggers k8s api triggered via non did proxy)
      - some hybrid thereof