## 2022-07-19 @pdxjohnny Engineering Logs

- TODO
  - [x] Kick off OSS scans
    - Targeting collaboration with CRob on metrics insertion to OpenSSF DB
  - [ ] Finish Q3 plans (Gantt chart, meeting templates, etc.)
    - Generate template for auto creation to fill every meeting / fillable pre-meeting
  - [ ] Follow up with OneAPI folks
  - [ ] Overlay to `alice shouldi contribute` to create git repos when found from forks of PyPi packages
    - [ ] Associated tutorial
      - [ ] Linked from `README`
  - [ ] Finish out `alice please contribute recommended community standards`
        dynamic opimp for meta issue body creation
    - [ ] Associated tutorial
      - [ ] Linked from `README` and `CONTRIBUTING`
- Some good spdx DAG stuff on how we turn source into build SBOM wise
  - https://lists.spdx.org/g/Spdx-tech/message/4659
- References
  - https://github.com/nsmith5/rekor-sidekick
    - > Rekor transparency log monitoring and alerting
    - Leverages Open Policy Agent
    - Found while looking at Open Policy Agent to see if we can serialize to JSON.
    - Possibly use to facilitate our downstream validation
      - https://github.com/intel/dffml/issues/1315
  - https://mermaid-js.github.io/mermaid/#/c4c
    - Mermaid is working on native https://c4model.com support!
  - W3C approves DIDs!
    - https://blog.avast.com/dids-approved-w3c
    - https://www.w3.org/blog/news/archives/9618
    - https://www.w3.org/2022/07/pressrelease-did-rec.html.en
    - https://twitter.com/w3c/status/1549368259878723585/retweets/with_comments

> "Intel Corporation congratulates the DID Working Group on Decentralized Identifier (DID) 1.0 reaching W3C Recommendation status.
>
> DID provides a framework to unify and consolidate multiple evolving identity systems. Consolidating identity systems within a single framework is useful for validating the authenticity of information and preserving its integrity as it is moved and processed among cloud, edge, and client systems. This potentially increases the capabilities of the Web to connect and unify multiple sources of information.
>
> The continuing evolution of this work will be key to the development of new technologies in the fields of supply chain management and Internet of Things (IoT) devices and services. For example, a Birds of a Feather (BOF) discussion group at IETF [Supply Chain Integrity, Transparency, and Trust (SCITT)](https://datatracker.ietf.org/doc/bofreq-birkholz-supply-chain-integrity-transparency-and-trust-scitt/) has already highlighted DID as a useful approach in providing much needed structure for exchanging information through the supply chain, and the Web of Things (WoT) WG is planning to support DID for identifying and discovering IoT devices and metadata.
>
> Intel Corporation supports this work and encourages the DID Working Group to continue working towards the convergence of widely implemented and adopted standardized best practices for identity in its next charter."
>
> Eric Siow, Web Standards and Ecosystem Strategies Director, Intel Corporation




- https://blog.devgenius.io/top-10-architecture-characteristics-non-functional-requirements-with-cheatsheat-7ad14bbb0a9b

> ![image](https://user-images.githubusercontent.com/5950433/179842612-5fb02fb5-1f26-4cb4-af0d-d375b1134ace.png)

- For Vol 3, on mind control
  - https://bigthink.com/the-present/sophists/

---

Unsent to Mike Scovetta: michael.scovetta (at) microsoft.com

Hi Mike,

Hope you’ve been well. It’s John from Intel. Thanks again to you and the team for welcoming me to the Identifying Security Threats working group meeting [2021-02-18](https://docs.google.com/document/d/1AfI0S6VjBCO0ZkULCYZGHuzzW8TPqO3zYxRjzmKvUB4/edit#heading=h.mfw2bj5svu9u) last year. We talked a bit about how Intel had a similar effort. I then changed roles hoping to get more involved with OpenSSF but then ended up getting told to be uninvolved. Now I switched roles again and involvement is in scope! Sorry for the lapse in communications.

I periodically check the minutes so I joined today and asked about the "Alpha-Omega" project from last week’s minutes which I then did some research on. We just started what looks to me to be an aligned project, coincidentally named Alice Omega Alpha: https://github.com/intel/dffml/tree/alice/entities/alice

It looks to me like Alice's mission to proactively enable developers and organizations to deliver organizationally context aware, adaptive secure by default best practices to teams aligns with project Alpha-Omega’s goals.

Alice is the nickname for both the entity and the architecture, the Open Architecture, which is a methodology for interpretation of existing well established, formats, protocols, and other domain specific representations of architecture. What we end up with is some JSON, YAML, or other blob of structured data that we can use to build cross language tooling focused more on policy and intent, incorporating data from arbitrary sources to create a holistic picture of software across dependency boundaries by focusing on threat models.

Alice will be doing scans of open source projects and we’d still love to collaborate to contribute metrics to the OpenSSF metrics database, we can easily have her shoot applicable metrics off to that DB. We’ve also been looking at fusing VEX and DIDs to facilitate distributed vulnerability disclosure and patch distribution.

---

Unset to Jun Takei: jun.takei (at) intel.com

The W3C today issued the recommendation on DIDs. Jun I saw from Eric's
comment on the press release that the SCITT working group has an SCITT
Architecture which DID's might be suitable for.

The DFFML community is working on a project called Alice
https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice
she is intended to be a developer helper. She's also the way we data mine
source repositories (etc.).

She’s open source with a plugin system ("overlays") so we can write open source code
and then just add our internal integrations. This system relies on an abstraction of
architecture known as the Open Architecture. The Open Architecture, also known as
Alice, is a methodology for interpreting directed graphs of domain specific architectures.
Alice is the name we give both the entity and the architecture. We are hoping to
have Alice store and process information backed by directed graphs of DIDs, SBOMs, and
VEX info primarily. This sounds very similar to the SCITT Architecture. We would love to
collaborate with you both to help make SCITT a success. Alice is focused on analysis of
our software supply chain so as to ensure we conform to best practices. We would like
the analysis to serialize directly to an industry best practice format for that as well,
which SCITT looks to be.

To increase the level of trust in our supply chain we would like to ensure interoperability
up and down the stack. Ned is involved in the DICE space and communicated to me
that 

Please let us  know where things are at with your involvement with DIDs and SCITT so we
can be in sync with Intel's involvement and direction in this space. Please also let us know
how we could best establish an ongoing line of communication so as to build off and
contribute to where possible the work you're involved in.

References:
- https://datatracker.ietf.org/doc/html/draft-birkholz-scitt-architecture
- https://www.w3.org/2022/07/pressrelease-did-rec.html.en
- https://docs.microsoft.com/en-us/azure/confidential-ledger/architecture

---

Unsent

To: Jun and Mike and Dan lorenc.d (at) gmail.com

I commented on the OpenSFF Stream 8 doc recommending that DIDs be looked at
as a way to exchange vulnerability information.

We've been looking potentially at a hybrid DID plus rekor
architecture (DIDs eventually as a proxy to) 

References:
- https://github.com/sigstore/rekor
