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