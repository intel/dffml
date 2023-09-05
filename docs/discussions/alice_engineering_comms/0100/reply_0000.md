## 2022-11-28 @pdxjohnny Engineering Logs

- https://github.com/pdxjohnny/use-cases/commit/36b4578a8ae7978f55c10e4e0a2eabd88788da27
- Reminder (on/off chain smart contracts! ref: https://github.com/intel/dffml/blob/alice/docs/arch/0009-Open-Architecture.rst it sounds block chainy but it's just a cyptographiclly linked list created ad-hoc with your neighbors! [grand scale speaking ;])
  - https://github.com/intel/dffml/blob/c7dc8985fdde61459017d3fb39cb19de1f7ece2b/docs/arch/0009-Open-Architecture.rst#L32-L36
- From 2022-11-17 Mark Foster on Twitter https://twitter.com/mfosterio/status/1593094082838290433
  - > Proof of Trust On The Internet (https://futureinternet.io)
    >
    > We are seeing repeats of behavior on centralized false ledger systems.
    >
    > I’ve had so many people calling me and asking about verification of decentralized ledgers ever since the fiasco of FTX and how to create systems to prevent Fraud.
    >
    > We should utilize cryptographic Merkle data structure proofs with open vocabularies to verify ownership, control of data and the internet of value (IOV)
    >
    > - Presentation Exchange DIF Foundation
    >   - https://identity.foundation/presentation-exchange/
    > - Linked Open Vocabularies
    >   - https://schema.org/InvestmentOrDeposit
    > - Web Authentication binded to a Human Input Device (HID) like a finger print scanner on your phone
    >   - w3.org/TR/webauthn-2/
    > - Verifiable Credential W3C Recommendation
    >   - https://www.w3.org/TR/vc-data-model
    > - Merkle Tree DAG CIDs
    >   - https://docs.ipfs.tech/concepts/merkle-dag/
    >     - > A Merkle DAG is a DAG where each node has an identifier, and this is the result of hashing the node's contents - any opaque payload carried by the node and the list of identifiers of its children - using a cryptographic hash function like SHA256. This brings some important considerations:
    >       >   - Merkle DAGs can only be constructed from the leaves, that is, from nodes without children. Parents are added after children because the children's identifiers must be computed in advance to be able to link them.
    >       >   - Every node in a Merkle DAG is the root of a (sub)Merkle DAG itself, and this subgraph is contained in the parent DAG.
    >       >   - Merkle DAG nodes are immutable. Any change in a node would alter its identifier and thus affect all the ascendants in the DAG, essentially creating a different DAG. Take a look at this helpful illustration using bananas (opens new window)from our friends at Consensys.
    >       >
    >       > Merkle DAGs are similar to Merkle trees, but there are no balance requirements, and every node can carry a payload. In DAGs, several branches can re-converge or, in other words, a node can have several parents.
    >       >
    >       > Identifying a data object (like a Merkle DAG node) by the value of its hash is referred to as content addressing. Thus, we name the node identifier as Content Identifier, or CID. (John: Or DID! [Alice Engineering Comms: 2022-11-08 Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4083171))
    >     - https://proto.school/merkle-dags
    > - Decentralized IDs (DID) W3C Recommendation
    >   - https://www.w3.org/TR/did-core/
    > - Secure Interoperable Wallets
    >   - https://w3c-ccg.github.io/universal-wallet-interop-spec/
    >   - https://openwallet.foundation
    > - There are many moving parts but the methodology research has been done. let’s build on top of the ecosystem of the future.
- TODO
  - [ ] Play with them there context aware Markov chains! (etc.)
    - Maybe useful https://github.com/karpathy/minGPT/blob/master/mingpt/model.py
  - [ ] https://github.com/intel/cve-bin-tool/pull/2384
    - CD and cross plugin/project analysis is dependent on this as a dependency of our
      standard interface / documentation aka manifests. Also the vuln updating (goes with
      the teritory, this is what we are using to ride on top of as comms channel).
      - https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md
  - [ ] UCAN/IPVM need to review :eyes:
    - [ ] https://github.com/ipvm-wg/spec/pull/8#issuecomment-1328355077
      - https://github.com/ipvm-wg/spec/blob/initial-job-spec/README.md
    - [ ] https://github.com/ucan-wg/invocation/pull/1#issuecomment-1327979869
      - [ ] https://github.com/fission-codes/spec/tree/main/dialog
    - [ ] https://github.com/ucan-wg/spec/issues/30#issuecomment-1321511824
      - > Brooklyn: In principle, if you're willing to deterministically encode the CWT, then you should be able to use the canonicalization spec and/or ucan-ipld to convert to/from CWT. Does that meet your CWT needs?
      - [ ] Ping Marc about Zephyr stuff (POC? :)
    - [ ] We should move DFFML flows to the IPVM style once available, or a configloader loadb/dumpb or something (dataflow?) for the time being
  - [ ] https://github.com/intel/dffml/issues/1425
  - [ ] Really need to do the chains of contexts stuff which will also double as
        the `alice shouldi contribute`. There is likely an issue with the current
        `source.update()` just merging over the old data, which means if something
        is no longer "qualified" or similar, that won't get overwritten, we want to
        have a `source.update()` mode which serializes the train of thought / pre updates.
        This likely also requires updates to `record.evaluated()` to create new instances
        of record data. Might be useful for when `record.data.key` needs changing such
        as when a `GitHubRepoID` is the key and it should be `record.feature("repo_url")`
        or something similar.
    - https://github.com/intel/dffml/blob/alice/entities/alice/alice/shouldi/contribute/cicd.py
      - 90d5c52f4dd64f046a2e2469d001e32ec2d53966
      - The instructions unfortunately I don't think work from this commit message, because it's the same main package, we need to setup the lightweight package stuff as was done here
        - https://github.com/intel/dffml/blob/1513484a4bf829b86675dfb654408674495687d3/dffml/operation/stackstorm.py#L306-L368
    - https://github.com/intel/dffml/issues/1418
  - [ ] `Record` feature data should retain dataflow `Input` type data if possible.
    - Ideally we enable graph traversal, once again only need one link deep if data
      is available offline. Try resolution via DID, CID, OA, etc.
    - We should also support serialization of only the latest system context /
      the state of the art for a train of thought / chain of system context.
      - State of the art could be defined by any set of strategic plans.
    - :bulb: Unification of Record / DataFlow / once working system context
      infra plus UCANs/DIDs/DIDs/IPVM/OA on chain should allow for cohesive / cleaner
      and more consistent context capture / unbroken chains for both data and compute.
     - And this is why we've started planning before implementing folks, woohoo!
     - Measure twice cut once.

---

Thank you expede! I'm hoping to dive in this week to look at all your recent developments.

Pining marc-hb, Brooklyn is the brains behind the correct implementation of the `sort_keys=True` -> CBOR situation

- References
  - [Alice Engineering Comms: 2022-11-08 Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4083171)
  - [Alice Engineering Comms: 2022-11-28 Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4250447)