## 2022-10-21 @pdxjohnny Engineering Logs

- (De)serialization
  - `did:merkle:`
- Online cloning cuts our iteration time
  - Artificial Life Is Coming Eventually
  - Data flows are the parallel exploration of trains of thought (nested graphs)
  - Natural selection and evolution
    - Tree of life
    - Parallel exploration of nested graphs
  - Automated synchronization of system state across distinct timelines (distinct roots)
    - Enables the resolution of system state post haste, post state, and post date
      - See fuzzy finding later in this doc: find "join disparate roots"
      - This is effectively out of order execution at a higher level of abstraction, in the aggregate, so as to bring the aggregate set of agents involved to an equilibrium state
  - We are building the thought communication protocol, to communicate thought is to learn
    - If we can describe any architecture, any problem space, we can describe any thought
    - To describe a thought most completely, one must know how to best communicate with that entity
    - That entity, that agent, is a moving target for communication at it's optimal rate of learning.
    - It's past is relevant in determining it's future as it's past determines what will resonate best with it in terms of forming conceptual linkages.
      - Past doesn't have to be memory, data and compute are the same in our architecture
      - Hardwired responses get encoded the same way, it's all the signal, the probability
  - When Alice goes through the looking glass she'll take us with her in sprit, and come back to communicate to us how best to proceed, in every way.
    - The less (more?) rambling way of putting this would be, we need our AI to be a true to us extension of ourselves, or of our ad-hoc formed groups, they need to be true to those strategic principles we've communicated to the machine. If we can trust their transparency (estimates/forecasts and provenance on that) about their ability to stay aligned to those principles, then we can accurately assess operating risk and it's conformance to our threat model or any threat model the execution of the job fits within.
    - This means we can trust our AI to not influence us in the wrong ways.
    - This means we can trust it to influence us in the right ways, the ways we want to influence ourselves, or our software development lifecycle.
      - This assessment of the level of trust fundamentally comes from our analysis of our analysis of our software development lifecycle, our Entity Analysis Trinity.
- https://github.com/OR13/did-jwk
  - https://github.com/OR13/did-jwk/blob/main/src/index.js#L158
- https://wasmer.io/
- https://oliverklingefjord.substack.com/p/pagerank-anthropology
- https://github.com/decentralized-identity/universal-resolver/blob/main/docs/driver-development.md
  - Full demo would be `did:meme:` and [`did:jwk:`](https://twitter.com/OR13b/status/1583818675982782465) ~~and `did:keri:` hybrid~~ (will wait on `did:keri:` hybrid until after MVP) with resolver implemented which serves and fetches containers from registry, instead of JPEG, use container image format.
    - This demo allows us to show checks on provenance for execution
    - Could we also require Verifiable Credentials to resolve the DID?
    - We could combine with static analysis / SBOM and Open Policy Agent and threat modeling to implement AI alignment to strategic principles (as agreed in compute contract) checks.
    - What does this enable?
      - One can now reference and request fulfilment of any flow, any process, any routine, etc via a single pattern.
        - 🐢
          - 🐢
            - 🐢
- https://identity.foundation/did-registration/
- Alice caught time traveling again
  - https://github.com/w3c-ccg/did.actor/commit/69144ab453447f682b20d8be13cd8293e888dd2f#diff-75f0c8d440957e0ea1c6945930d0ac946e85e3e324b59a8af8ed13a3918581f1R10
  - https://github.com/w3c-ccg/did.actor/commit/56d4f525f21b84696badc312f9654451911250f4#diff-75f0c8d440957e0ea1c6945930d0ac946e85e3e324b59a8af8ed13a3918581f1R10
  - https://github.com/w3c-ccg/did.actor/blob/3fe99eec616b71d7fc36c5603235eeac81c91652/bob/credentials/3732.json
  - https://github.com/w3c-ccg/did.actor/blob/3fe99eec616b71d7fc36c5603235eeac81c91652/alice/README.md
    - https://lucid.did.cards/identifiers/did:web:did.actor:alice
- https://github.com/WebOfTrustInfo
  - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/draft-documents/verifiable-endorsements-from-linked-claims.md
    - > Further, we propose to demonstrate the ability to compose several LinkedClaims into a single domain-specific credential, specifically a Verifiable Endorsement, that will satisfy the domain requirements of the likely users.
      >
      > This approach will enable rich shared datasets to inform trust decisions, while satisfying the requirements of domain-specific end users. If time permits a sample score can be built over the linked claim dataset.
  - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/draft-documents/composable-credentials.md#standalone-claim---review
    - An event in our case (to start with) is data flow Input data, our cached data.
  - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/draft-documents/data-exchange-agreements-with-oca.md
    - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/draft-documents/data-exchange-agreements-with-oca.md#13-context-preservation---semantic-approach---the-overlays-capture-architecture-oca
      - Woohoo! Someone else defined overlays, now we don't have to :P
      - https://oca.colossi.network/
      - https://oca.colossi.network/guide/introduction.html#what-is-decentralised-semantics
        - > In the domain of decentralised semantics, task-specific objects are called "Overlays". They provide layers of definitional or contextual information to a stable base object called a “Capture Base”.
- SCITT
  - https://mailarchive.ietf.org/arch/browse/scitt/
  - https://mailarchive.ietf.org/arch/msg/scitt/NtBc7vfMm-zFKxguVfiGg-vGjHk/
    - VDR usage
- https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/draft-documents/did-merkle.md
- Why do we like DIDs?
  - It is a primitive for a decentralized offline capable cryptographically secured linked list.
  - This allows us to join disparate roots (timelines, trees, metric data graphs) at a later time
    - Or to revaluate inclusion of those sets
    - Or to generate new datasets entirely
    - Or to run inference to get those datasets / trees
    - Or a hybrid approach
  - This will enable training Alice to be risk averse, aka training to be aligned with strategic principles.
    - [2022-10-19 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-3918361)
    - This will help Alice not waste time on unaligned trains of thought.
    - Our gatekeeper and prioritizer of course have final say, but this is to do the fuzzy filter logic on those.
  - https://github.com/pdxjohnny/pdxjohnny.github.io/blob/dev/content/posts/2022-03-02-did-twitter-space.md
  - https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/quantum-secure-dids.pdf
  - https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/SelfIdentifyingData.md
    - > The question this white-paper attempts to answer is how best to represent decentralized self-certifing self-identifying data. The main use case for this type of data are distributed (but with decentralized control) data intensive processing applications. Because data intensive applications are often limited by network and processing resources, economy of expression is an important consideration in a data representation schema. Thus there are trade-offs to be made in the design of the schema where economy of expression is a desirable feature.
    - > A decentralized self-identifying data item is identified by a decentralized universally unique self-certifying identifier (DID). Self certifying means that the identifier includes either a public key or a fingerprint of a public key from a cryptographic public/private key pair. The DID is included in the data item itself as the value of a field. The data item also includes a field whose value is the DID for the signer of the data item. This may or may not be the same DID used to identify the data item itself. Attached to the data item is a signature that is verifiable as being generated by the private key associated with the public key in the signer field's DID value. This signature verifies that the data item was created by the holder of the associated private key for the signer. The whole data item is both self-identifing and self-certifying because all identifiers are included in the signed data and are verifiable against the private keys associated with the public keys in the included DIDs.
      - This is exactly why we like DIDs
    - https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/SelfIdentifyingData.md#data-canonicalization
    - https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/SelfIdentifyingData.md#key-reproduction
    - https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/A_DID_for_everything.pdf
      - Good background info on DIDs
      - > It should be noted that a single instance of meeting is not as trustable as an entire history of meeting many people. For a state actor generating a legend for a sockpuppet, this would entail an unattainable level of work to prove personhood. For a regular human being, it's relatively efortless to use the system in an organic and unobtrusive manner. Once a root personhood verifcation could be insured, then trustable pseudonyms could be generated. Adding this verifcation to DIDs would provide trust in a trustless environment, as the DID could then provide identity and credentialing services in environments that support, or even require, pseudonymity
      - > Data fows can be provenanced by verifying the end-to-end integrity of data with DIDs. By enabling DIDs to sign claims about other DIDs, the fidelity of these data fows can be increased further
        - Bingo
      - > Imagine a world where this proposed technology has been deployed and globally adopted. Let us paint a picture for how this might be achieved. Imagine that this approach becomes part of a decentralized identity solution for every entity, driven by a robust and active developer community. The vision is to generate technologies that would be integrated into applications that are used in IoT, e-commerce, social interaction, banking, healthcare, and so on. Now imagine that mobile telephony companies agree to embed the technology into the operating systems for all smartphones, and the dominant social network providers agree to use DIDs and DADs and proofs about the entities controlling these DIDs and DADs in their algorithms for determining which content to propel. This would mean the end of phishing. The end of fake news. This is the beginning of new era for society, built on an interconnecting web of trust: a world in which we know what impacts we are having. The emergent property of this new data fabric is Knowing.
        - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0004_writing_the_wave.md
      - > Underlying the benefts of decentralized identity outlined above is the need for open interoperable standards to ensure the reputable provenance of the associated data fows between decentralized entities. This paper describes a novel concept for provenancing data fows using DADis (Decentralized Autonomic Data items) that are built upon the emerging DID standard. This approach uses and extends the advanced difuse-trust or zero-trust computing paradigm that is needed to operate securely in a world of decentralized data.
  - https://github.com/transmute-industries/verifiable-actions
  - https://github.com/transmute-industries/verifiable-data
    - https://github.com/transmute-industries/verifiable-data/tree/main/packages/ed25519-signature-2018
    - https://github.com/digitalbazaar/jsonld-signatures
      - > The proof purpose indicates why the proof was created and what its intended use is. This information can also be used to make sure that the verificationMethod was authorized for the stated purpose in the proof. Using a proof purpose helps to encourage people to authorize certain cryptographic keys (verification methods) for explicit purposes rather than granting them ambient authority. This approach can help prevent people from accidentally signing documents for reasons they did not intend.
    - https://github.com/digitalbazaar/vc-js#custom-documentloader
      - Data flow integration opportunities
    - https://github.com/WebOfTrustInfo/rwot5-boston/blob/778ccf4c56319d31ea3d9baac8a27e2cbe6763ec/topics-and-advance-readings/verifiable-claims-primer.md
    - https://github.com/WebOfTrustInfo/rwot5-boston/blob/master/topics-and-advance-readings/did-primer.md
- https://twitter.com/vdmbrsv/status/1583512490226647040/photo/1
  - https://github.com/kathrinse/be_great
- https://github.com/microsoft/did-x509/blob/main/specification.md
- https://didcomm.org/book/v2/
- Need to analyze KERI interoperability ergonomics with rest of web5 ecosystem
  - How would tie in with OIDC GitHub Actions / sigstore work?
  - Does this enable crowdsourable DB via (confidential) ledgers as root of trust watchers?
  - Perfect forward secrecy please with that roll forward key thing
    - https://github.com/WebOfTrust/keripy
    - Have yet to see another solution with potential DID space interop.
    - Have to be sure before making any next steps.
    - Would be very nice for datatset/cache (de)serialization.
    - If it can be done cleanly, might as well play with it.
  - Try with `did:meme`
    - https://or13.github.io/didme.me/did-method-spec.html
    - https://or13.github.io/didme.me/#using-github-pages
    - [2022-10-19 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-3918361)
    - `did:oa:data:`
    - What used to be the meme data in the `did:meme:` is now our system context
    - https://github.com/w3c/did-spec-registries/compare/main...pdxjohnny:aliceoa?expand=1
      - `did:alice:`
        - Entry points for Alice the entity
          - https://packaging.python.org/en/latest/specifications/entry-points/
          - These are our `dffml.overlays.alice.please.contribute`
            - Upstream: `did:alice:please:contribute:<ID>`
            - Overlays: `did:alice:please:contribute:<ID>`
            - JSON-LD
              - Enables streaming query for applicable overlays
            - Decentralized Web Nodes
              - Enable data transfer of DID docs
              - For simplistic query, one can drop the `<ID>` portion of the DID
                - DWNs could then resolve all DIDs the operator (instantiated Operation Implementation Network) would like to make known to the requester as an advertisement of services
          - `did:alice:`
            - Resolves the base (data) flow, the upstream
              - Extracts the entry point from the DID doc
      - `did:oa:`
    - Ping Orie to ask for thoughts when done
- How you are is how you will be
- https://multiformats.io/multihash/
  - Shim-esq
- https://identity.foundation/keri/did_methods/

### Analysis of KERI interoperability ergonomics with rest of web5 ecosystem

- References
  - https://github.com/WebOfTrust/keripy
  - https://github.com/WebOfTrust/keripy/blob/1b83ac4625b072c1f7c9f583c4dde85d5eb1cde8/setup.py#L100-L102
    - Notice anyone currently missing?
  - https://github.com/WebOfTrust/keripy/search?q=did
  - https://github.com/WebOfTrust/keripy/blob/303e45a1b293b544f7976fa2c56094172b3254b8/ref/Peer2PeerCredentials.md
  - https://github.com/WebOfTrust/keripy/blob/development/tests/peer/test_exchanging.py
- https://github.com/decentralized-identity/keri/blob/master/kids/kid0009.md
- https://weboftrust.github.io/did-keri/#create
  - https://identity.foundation/keri/docs/Glossary.html#inception-event
    - >![image](https://user-images.githubusercontent.com/5950433/197252695-488e3476-734d-4b3f-b551-b562674d89b2.png)
      >
      > The inception data must include the public key, the identifier derivation from that public key, and may include other configuration data. The identifier derivation may be simply represented by the derivation code. A statement that includes the inception data with attached signature made with the private key comprises a cryptographic commitment to the derivation and configuration of the identifier that may be cryptographically verified by any entity that receives it.
A KERI inception statement is completely self-contained. No additional infrastructure is needed or more importantly must be trusted in order to verify the derivation and initial configuration (inception) of the identifier. The initial trust basis for the identifier is simply the signed inception statement.

```console
$ python -m pip install -U lmdb pysodium blake3 msgpack simplejson cbor2
Defaulting to user installation because normal site-packages is not writeable
Collecting lmdb
  Downloading lmdb-1.3.0-cp310-cp310-manylinux_2_12_x86_64.manylinux2010_x86_64.whl (306 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 306.5/306.5 kB 11.0 MB/s eta 0:00:00
Collecting pysodium
  Downloading pysodium-0.7.12.tar.gz (21 kB)
  Preparing metadata (setup.py) ... done
Collecting blake3
  Downloading blake3-0.3.1-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.whl (1.1 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 32.8 MB/s eta 0:00:00
Collecting msgpack
  Downloading msgpack-1.0.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (316 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 317.0/317.0 kB 26.9 MB/s eta 0:00:00
Collecting simplejson
  Downloading simplejson-3.17.6-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_12_x86_64.manylinux2010_x86_64.whl (137 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 137.1/137.1 kB 9.1 MB/s eta 0:00:00
Collecting cbor2
  Downloading cbor2-5.4.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (224 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 224.1/224.1 kB 10.6 MB/s eta 0:00:00
Building wheels for collected packages: pysodium
  Building wheel for pysodium (setup.py) ... done
  Created wheel for pysodium: filename=pysodium-0.7.12-py3-none-any.whl size=13458 sha256=72829531fd887689066dbfcb64fbeb37343ed194b999a944941240da3b42265e
  Stored in directory: /home/pdxjohnny/.cache/pip/wheels/20/c6/d1/e0ea5672f6614258bcd469d6721039778d2b8510bc420e8414
Successfully built pysodium
Installing collected packages: pysodium, msgpack, lmdb, blake3, simplejson, cbor2
Successfully installed blake3-0.3.1 cbor2-5.4.3 lmdb-1.3.0 msgpack-1.0.4 pysodium-0.7.12 simplejson-3.17.6
$ pip install https://github.com/WebOfTrust/keripy/archive/refs/tags/v0.6.7-alpha.tar.gz#egg=keri
Defaulting to user installation because normal site-packages is not writeable
Collecting keri
  Downloading https://github.com/WebOfTrust/keripy/archive/refs/tags/v0.6.7-alpha.tar.gz
     / 3.1 MB 4.8 MB/s 0:00:00
  Preparing metadata (setup.py) ... done
Requirement already satisfied: lmdb>=1.3.0 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from keri) (1.3.0)
Requirement already satisfied: pysodium>=0.7.12 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from keri) (0.7.12)
Requirement already satisfied: blake3>=0.3.1 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from keri) (0.3.1)
Requirement already satisfied: msgpack>=1.0.4 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from keri) (1.0.4)
Requirement already satisfied: cbor2>=5.4.3 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from keri) (5.4.3)
Collecting multidict>=6.0.2
  Downloading multidict-6.0.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (114 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 114.5/114.5 kB 4.2 MB/s eta 0:00:00
Collecting ordered-set>=4.1.0
  Downloading ordered_set-4.1.0-py3-none-any.whl (7.6 kB)
Collecting hio>=0.6.7
  Downloading hio-0.6.7.tar.gz (87 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 87.7/87.7 kB 8.3 MB/s eta 0:00:00
  Preparing metadata (setup.py) ... done
Collecting multicommand>=1.0.0
  Downloading multicommand-1.0.0-py3-none-any.whl (5.8 kB)
Collecting jsonschema>=4.6.0
  Downloading jsonschema-4.16.0-py3-none-any.whl (83 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 83.1/83.1 kB 7.6 MB/s eta 0:00:00
Collecting falcon>=3.1.0
  Downloading falcon-3.1.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (8.5 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.5/8.5 MB 52.8 MB/s eta 0:00:00
Collecting daemonocle>=1.2.3
  Downloading daemonocle-1.2.3.tar.gz (41 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 41.4/41.4 kB 6.2 MB/s eta 0:00:00
  Preparing metadata (setup.py) ... done
Collecting hjson>=3.0.2
  Downloading hjson-3.1.0-py3-none-any.whl (54 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 54.0/54.0 kB 4.0 MB/s eta 0:00:00
Requirement already satisfied: PyYaml>=6.0 in /usr/lib64/python3.10/site-packages (from keri) (6.0)
Collecting apispec>=5.2.2
  Downloading apispec-6.0.0-py3-none-any.whl (29 kB)
Collecting mnemonic>=0.20
  Downloading mnemonic-0.20-py3-none-any.whl (62 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 62.0/62.0 kB 6.4 MB/s eta 0:00:00
Requirement already satisfied: packaging>=21.3 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from apispec>=5.2.2->keri) (21.3)
Collecting click
  Downloading click-8.1.3-py3-none-any.whl (96 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 96.6/96.6 kB 11.5 MB/s eta 0:00:00
Collecting psutil
  Downloading psutil-5.9.3-cp310-cp310-manylinux_2_12_x86_64.manylinux2010_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (292 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 292.3/292.3 kB 24.0 MB/s eta 0:00:00
Requirement already satisfied: netifaces>=0.11.0 in /usr/lib64/python3.10/site-packages (from hio>=0.6.7->keri) (0.11.0)
Requirement already satisfied: attrs>=17.4.0 in /usr/lib/python3.10/site-packages (from jsonschema>=4.6.0->keri) (21.4.0)
Requirement already satisfied: pyrsistent!=0.17.0,!=0.17.1,!=0.17.2,>=0.14.0 in /usr/lib64/python3.10/site-packages (from jsonschema>=4.6.0->keri) (0.18.1)
Requirement already satisfied: pyparsing!=3.0.5,>=2.0.2 in /home/pdxjohnny/.local/lib/python3.10/site-packages (from packaging>=21.3->apispec>=5.2.2->keri) (3.0.9)
Building wheels for collected packages: keri, daemonocle, hio
  Building wheel for keri (setup.py) ... done
  Created wheel for keri: filename=keri-0.6.7-py3-none-any.whl size=371275 sha256=0fc4353cff6f82d93bcbe2023b5fbe34d8f19695b534280b39d6501e34fec6c4
  Stored in directory: /home/pdxjohnny/.cache/pip/wheels/5d/d4/7a/c5394220af3d084c08af13cdfc6c822adade30f969caa3e6be
  Building wheel for daemonocle (setup.py) ... done
  Created wheel for daemonocle: filename=daemonocle-1.2.3-py3-none-any.whl size=27547 sha256=245fcb13356d1abfade022d8ec1d71df72f6a75613e3a3a021f18c47a18a1895
  Stored in directory: /home/pdxjohnny/.cache/pip/wheels/90/74/0a/e42fc6338ed1604a4b23fb4ebd4c1c7c7ae716f0ecbbe6fb14
  Building wheel for hio (setup.py) ... done
  Created wheel for hio: filename=hio-0.6.7-py3-none-any.whl size=97821 sha256=c8ab55b918d13057109de99a475c729fd6b8ef9cc249e01a933ca88156cd357f
  Stored in directory: /home/pdxjohnny/.cache/pip/wheels/9f/a0/f7/8696eba689852f5f33237d5e67a5f71a6b084e3df25dc7080d
Successfully built keri daemonocle hio
Installing collected packages: hjson, psutil, ordered-set, multidict, multicommand, mnemonic, jsonschema, falcon, click, hio, daemonocle, apispec, keri
Successfully installed apispec-6.0.0 click-8.1.3 daemonocle-1.2.3 falcon-3.1.0 hio-0.6.7 hjson-3.1.0 jsonschema-4.16.0 keri-0.6.7 mnemonic-0.20 multicommand-1.0.0 multidict-6.0.2 ordered-set-4.1.0 psutil-5.9.3
```

- References
  - https://github.com/OR13/didme.me/blob/14da8e47d8a1a4bef3cc1c85968c9f8b6963d269/components/DIDMemeCreator.tsx#L59
  - https://github.com/OR13/didme.me/blob/14da8e47d8a1a4bef3cc1c85968c9f8b6963d269/core/DIDMeme/index.ts
  - https://github.com/OR13/didme.me/blob/14da8e47d8a1a4bef3cc1c85968c9f8b6963d269/core/ipfs.ts
  - https://github.com/desudesutalk/f5stegojs#cli-tool
  - https://github.com/OR13/didme.me/blob/14da8e47d8a1a4bef3cc1c85968c9f8b6963d269/components/DIDMemeCreator.tsx#L42**
  - https://github.com/OR13/didme.me/blob/14da8e47d8a1a4bef3cc1c85968c9f8b6963d269/components/DIDMemeCreator.tsx#L157
  - https://github.com/OR13/didme.me/blob/14da8e47d8a1a4bef3cc1c85968c9f8b6963d269/components/WalletCreator.tsx#L20-L70
- TODO
  - [ ] Read https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/alice-attempts-abuse-verifiable-credential.pdf
  - [ ] 2nd party infra
    - [ ] Stream of consciousness
      - [ ] GitHub actions webhook enable Stream of consciousness in repo setting then will dispatch workflows via stream of consciousness path logic reading trigger filtering based on `on.push.paths`
    - [ ] Could use DID entry points as paths to signal workflow should be triggered on that event
      - Could get down to operation granularity referenced inside flows for given event stream s.
        - Example: `paths: ["did:alice:shouldi:contribute:clone_git_repo:ouputs.repo"]`
          - Through workflow inspect we can expose this as an overlay
          - It can be advertised to the stream of consciousness that this workflow should be dispatched, if the overlay is enabled