## 2023-01-17 @pdxjohnny Engineering Logs

- https://fediverse.party/en/miscellaneous/
  - https://docs.microblog.pub/user_guide.html
    - https://git.sr.ht/~tsileo/microblog.pub/tree/v2/item/app/database.py
  - ActivityPub with pull channel for downstream validation
    - Periodic launching of workflows which federate via localhost.run or similar
    - https://semapps.org/docs/guides/activitypub
    - https://semapps.org/docs/middleware/activitypub
    - https://jena.apache.org/documentation/fuseki2/fuseki-main.html
    - https://jena.apache.org/documentation/fuseki2/fuseki-data-access-control.html
    - https://jena.apache.org/download/maven.html
    - https://repository.apache.org/content/repositories/snapshots/org/apache/jena/jena-fuseki-server/
    - keybase style VC post proof
      - To handoff as comms spin up / down
  - https://github.com/forgeflux-org
    - Similar in theory
    - > API-space software forge federation
- https://github.com/w3c-ccg/traceability-interop/commit/d863afd085491d4c21268c4bf1571da02e468d31
  - https://w3id.org/traceability/v1
- https://w3c-ccg.github.io/traceability-interop/draft/
  - > As this specification deals with the implementation of software that relates directly to the traceability of physical real world objects in the supply chain, implementations of software conformant with this specification should be treated as [Critical Software ](https://www.nist.gov/itl/executive-order-improving-nations-cybersecurity/critical-software-definition)and as such SHOULD follow all guidelines related to the protection of [Software Supply Chains ](https://www.nist.gov/itl/executive-order-improving-nations-cybersecurity/software-supply-chain-security). Solutions implementing this specification SHOULD seek conformance with NIST [800-161 Rev. 1 ](https://csrc.nist.gov/publications/detail/sp/800-161/rev-1/draft)or superceding documents. Solutions implementing this specification SHOULD seek conformance with NIST [800-218 ](https://csrc.nist.gov/publications/detail/sp/800-218/draft)or superceding documents. The [Guidelines on Minimum Standards for Developer Verification of Software - NISTIR 8397 ](https://nvlpubs.nist.gov/nistpubs/ir/2021/NIST.IR.8397.pdf)MUST be followed by developers implementing solutions intended to be conformant with this specification. NB: this guidance applies to sections beyond Software Supply Chain issues, and many of the topics covered have discrete sections in this specification or supplemental aids such as the [test suite](https://github.com/w3c-ccg/traceability-interop/tree/main/tests/postman) provided in the repository for this specification.
  - > Any system conforming with this specification for interoperability MUST utilize [Linked Data Signatures for JWS ](https://github.com/w3c-ccg/lds-jws2020/) **or superceding version if it is standardized as a part of the VC Working Group for signing Linked Data in usage with Verifiable Credentials.**
- https://www.nsa.gov/portals/75/documents/what-we-do/cybersecurity/professional-resources/ctr-nsa-css-technical-cyber-threat-framework.pdf
- Another description: Copy exact across heterogeneous environments via cattle to pets equilibrium mapping (values streams)

```json
{
    "SoftwareBillOfMaterials": {
      "@context": {
      },
      "@id": "https://w3id.org/traceability#SoftwareBillOfMaterials"
    },
    "SoftwareBillofMaterialsCredential": {
      "@context": {
      },
      "@id": "https://w3id.org/traceability#SoftwareBillOfMaterialsCredential"
    }
}
```

- Example overlay of running actions validator
  - https://github.com/intel/dffml/blob/12e862924a85c4ec36499c869406d411bb07c9fb/operations/innersource/dffml_operations_innersource/actions_validator.py#L56-L76
- Example of enabling that for `alice shouldi contribute`
  - https://github.com/intel/dffml/blob/12e862924a85c4ec36499c869406d411bb07c9fb/entities/alice/entry_points.txt#L29
- Example of ensuring binary available for testing
  - https://github.com/intel/dffml/blob/12e862924a85c4ec36499c869406d411bb07c9fb/entities/alice/alice_test/shouldi/contribute/actions_validator.py#L62-L83
  - https://github.com/intel/dffml/blob/12e862924a85c4ec36499c869406d411bb07c9fb/entities/alice/entry_points.txt#L35
    - **TODO** Command to enable overlays by creating blank package and installing