## 2022-10-13 IETF SCITT Technical Meeting

- WG Chartered!
  - https://mailarchive.ietf.org/arch/msg/scitt/OsUTPGEUUVQGxcU1J8UostNs1iM/
  - https://datatracker.ietf.org/doc/charter-ietf-scitt/
  - https://vocabulary.transmute.industries/
- Semantic Versioning
  - Ray would like to see this included in software use case.
  - Policy around update
    - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice
- Facilitate post instance creation labeling
  - Notary adds to transparency infrastructure at a later point, how do we ensure others have access to that?
    - They should go query those notaries or require up to date receipts from them.
- We don't care so much about what's in the SBOM, it's just data
- There may be many SBOMs for a single release of software, they could be insert by multiple notaries using different scanner implementations.
- Trust graphs constricuted at a later date
  - Orie Steele (Transmute):
    - 'In our world, these are “graph queries”... the graphs are built from the registry data. joined with other data. I don't see SCITT as solving for graph queries… it just provides a data set that is projected into the graph'
- Can't we just always use a recpit to auth?

Source: https://github.com/ietf-scitt/scitt-web/blob/main/content/what-is-scitt.md

![scii-persistance](https://github.com/ietf-scitt/scitt-web/raw/main/content/media/scitt-persistence.png)