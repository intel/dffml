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

Our reference architecture is built around a specs such as SBOM, VEX, and DIDs.

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

- Living Threat Models

  - John L Whiteman & John S Andersen, "Living Threat Models", June 11th 2022
  - https://github.com/johnlwhiteman/living-threat-models

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
