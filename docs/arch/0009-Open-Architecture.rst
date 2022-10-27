Open Architecture
#################

Version: 0.0.1
Date: 2022-04-17

Status
******

Proposed - https://github.com/intel/dffml/pull/1401

Description
***********

The Open Architecture is a methodology for interpreting directed graphs as
any system architecture.

Context
*******

This document describes the Open Architecture; a proxy to domain
specific representations of architecture.

The Open Architecture is a methodology for intepretation of exisitng
well established, formats, protocols, and other domain specific
representations of architecture. We define a methodology for interpreting
a directed graph representing a system architecture.

We provide implementations which interpret graphs as software and hardware
architectures.

The Open Architecture also enables hybrid on/off chain smart contacts.
It does this by incorporating risk management into architecture definition /
smart contract. Smart contracts with understanding of risk are effectively
entities making decisions based on models. This allows for mutation in
implementation while maintaining principles.

The smart contract is able to make its own decisions based on learned
experience so as to continue to operate until its strategic goals are meet.
As measured by oracle data ordained from trusted parties as is
applicable to context. Where chains of trust are established via DIDs
between entities and data for provenance. Leveraging verifiable credentials
for review system to measure risk in absence of attestation.

Our reference architecture is built around a specs such as SBOM, VDR, and DIDs.
We leverage the concept of a Manifest to talk about a node within the graph.
A manifest is any document which is aligned with the guidelines within the
`Manifest ADR <https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md>`_.
A DID doc is an example of an instance of a manifest.

Intent
******

- ``upstream`` MUST be treated as the document itself if the document is a
  domain sepcific architecture or manifest already.

- ``overlay`` MUST be applied to upstream following overlay application process
  describied in **TODO** `Overlay <https://github.com/intel/dffml/blob/alice/Overlay>`_ if given

- ``orchestrator`` SHOULD be loaded and inspected for compliance with top level
  system context's policy (sandbox) before execution.

References
**********

- Manifests

  - https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md
  
- Overlays

  - https://oca.colossi.network/guide/introduction.html#what-is-decentralised-semantics
  
    - ``In the domain of decentralised semantics, task-specific objects are called "Overlays". They provide layers of definitional or contextual information to a stable base object called a "Capture Base".``
    
    - The DFFML project equivalent vocabulary term for "Capture Base" would probably be "upstream".

- Living Threat Models

  - John L Whiteman & John S Andersen, "Living Threat Models", June 11th 2022
  - https://github.com/johnlwhiteman/living-threat-models

- An Architecture for Trustworthy and Transparent Digital Supply Chains (IETF/SCITT)

  - https://datatracker.ietf.org/doc/charter-ietf-scitt/
  - https://datatracker.ietf.org/doc/html/draft-birkholz-scitt-architecture
  - https://github.com/intel/dffml/discussions/1406#discussioncomment-3223361
  - https://docs.google.com/document/d/1vf-EliXByhg5HZfgVbTqZhfaJFCmvMdQuZ4tC-Eq6wg/edit?pli=1#
  - https://github.com/ietf-scitt/use-cases/blob/main/hardware_microelectronics.md
  - https://github.com/ietf-scitt/use-cases/issues/14

- GUAC: Graph for Understanding Artifact Composition

  - https://docs.google.com/presentation/d/1WF4dsJiwR6URWPgn1aiHAE3iLVl-oGP4SJRWFpcOlao/edit#slide=id.g14078b5bab0_0_517
  - https://github.com/guacsec/guac

- DIDs
  
  - https://github.com/pdxjohnny/pdxjohnny.github.io/blob/dev/content/posts/2022-03-02-did-twitter-space.md

  - https://github.com/WebOfTrustInfo/rwot5-boston/blob/master/topics-and-advance-readings/did-primer.md
  
  - https://github.com/SmithSamuelM/Papers/blob/master/whitepapers/A_DID_for_everything.pdf

- TODO

  - Add content from discussion thread

    - `docs/arch/alice/discussion/0004/reply_0005.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0004/reply_0005.md>`_
    - `docs/arch/alice/discussion/0023/reply_0020.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0020.md>`_
    - `docs/arch/alice/discussion/0023/reply_0022.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0022.md>`_
    - `docs/arch/alice/discussion/0023/reply_0028.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0028.md>`_
    - `docs/arch/alice/discussion/0023/reply_0037.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0037.md>`_
    - `docs/arch/alice/discussion/0023/reply_0040.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0040.md>`_
    - `docs/arch/alice/discussion/0023/reply_0055.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0055.md>`_
    - `docs/arch/alice/discussion/0036/reply_0022.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0036/reply_0022.md>`_
    - `docs/arch/alice/discussion/0036/reply_0045.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0036/reply_0045.md>`_
    - `docs/arch/alice/discussion/0036/reply_0062.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0036/reply_0062.md>`_
    - `docs/arch/alice/discussion/0036/reply_0066.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0036/reply_0066.md>`_
    - `docs/arch/alice/discussion/0036/reply_0067.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0036/reply_0067.md>`_
    - `docs/arch/alice/discussion/0039/index.md <https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0039/index.md>`_
    - `docs/tutorials/rolling_alice/0000_architecting_alice/README.md <https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/README.md>`_
    - `docs/tutorials/rolling_alice/0000_forward.md <https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_forward.md>`_
    - `docs/tutorials/rolling_alice/0000_preface.md <https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_preface.md>`_
    - `docs/tutorials/rolling_alice/README.md <https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/README.md>`_
