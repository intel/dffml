## 2023-06-15 GUAC Community Call

- Proposal to contribute GUAC to OpenSSF
  - Looking to fall under Supply Chain Integrity WG
  - Project itself
  - As a public service
- Persistent backends
  - Licensing issues with neo4j
  - https://github.com/guacsec/guac/issues/851
  - https://docs.google.com/document/d/1wk7N9zggygz1Xx7qgx1aEt3niPpAEkRpdQi5i7k0Cj8/edit#
    - Minimum capabilities
    - Artifact injection and query
      - Dependency and occurrence to facilitate SBOM
  - Parth Patel: Demo with ArangoDB
    - https://www.arangodb.com/
    - Able to ingest documents
    - Show the database
    - GUAC still exposes as GraphQL
    - Currently looking at optimization
    - Marcela: What are the numbers?
      - 1 sbom in demo around ~4000 graph nodes added for various aspects, packages, artifacts, etc.
  - Jeff Mendoza: Demo with Ent ORM - SQL (Postgress, Sqlite, etc.)
    - https://entgo.io/
  - Dejan Bosanac
    - S3 bucket
    - Also tried to build GUAC component in Rust
- https://github.com/search?q=repo%3Aguacsec%2Fguac%20subscriber&type=code
  - Michael Lieberman
    - Not currently exporting events outside of the memory space
    - Talked about cloud events / cd events
      - https://github.com/cloudevents/spec/issues/829#issuecomment-1459080878
    - Working with Sterling Toolchain
      - Slack is formerly-named-sterling-toolchain
    - Open an issue and we can communicate there, discussions have mostly been ad-hoc
      - https://github.com/guacsec/guac/issues/460
      - Dejan might work on nats over cloud events

![live-demo-for-the-live-demo-god](https://user-images.githubusercontent.com/5950433/226699339-45b82b38-a7fc-4f2f-a858-e52ee5a6983d.png)