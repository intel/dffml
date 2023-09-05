## 2022-09-15 Open Architecture

- OA: SCITT for provenance (SPDX DAG for DAG?) plus overlayed (aka generic admission controller, return 0/1) policy. Use example from yesterday, psudo code release flow with checks to SCITT as if it was a BOM/database being added to as the product is built. Come up with places where policy is relevant: incoming vuln, package, sign, release (dont sign unless X, dont release unless Y, new vuln? Run policy check to determine if it effects your arch, take actions (re-roll with updated dep) acrodingly
- Relized SCITT will probably still not define the graph
  - Looking for the SPDX DAG work or antyhing like it: https://www.google.com/search?hl=en&q=spdx%20%22dag%22&tbs=qdr%3Am
- References
  - https://github.com/git-bom/gitbom-rs/issues/18
    - > There was a discussion in today's GitBOM meeting about the utility of separating generation of gitoids from the generation of a GitBOM DAG. (@)edwarnicke has implemented this split in Go (https://github.com/edwarnicke/gitoid) (WIP) and described it as being a valuable change. The idea is that by splitting this out, other uses of gitoids can be explored.
  - https://github.com/edwarnicke/gitoid
- SCITT
  - https://github.com/ietf-scitt/charter/blob/master/ietf-scitt-charter.md
  - https://github.com/ietf-scitt/use-cases/blob/main/hardware_microelectronics.md
  - https://datatracker.ietf.org/doc/html/draft-birkholz-scitt-architecture
    > ```
    >                 Artifact
    >                    |
    >                    v                      +------------------+
    >     Issuer    -> Statement    Envelope    | DID Key Manifest |
    >                    \           /          | (decentralized)  |
    >                     \         /           +------------------+
    >                      \ ______/               |     |
    >                          |                   |     |
    >                          v        signature  |     |
    >                        Claim  <--------------/     |
    >                          |                         |
    >                          |  Claim      +---------+ |
    >                          |------------>| Trans.  | |
    >    Transparency ->       +<------------| Registry| /
    >    Service               |  Receipt    +--------+ X
    >                          v                       / \
    >                     Transparent                 /   \
    >                        Claim                   /    |
    >                          |\                   /     |
    >                          | \                 /      |
    >                          |  \               /       |
    >    Verifier    ->        |    Verify Claim          |
    >                          |                          |
    >    Auditor    ->       Collect Receipts     Replay Registry
    > ```