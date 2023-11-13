## 2023-11-07 IETF 118 Secure Patterns for Internet CrEdentials (SPICE) Meeting

> *Whoever controls...*

- Pamela Dingle co-chair
- Hannes who was co-chair for SCITT is now co-chair here
- Roman joining
- https://notes.ietf.org/notes-ietf-118-spice
- Leif - Market Driver
  - EU legislation process
  - EU attempts to build digital identity wallet
  - EU is a deal making 30 way negotiation process between member states and commission
  - Implementation Acts are law masquerading as technical specs
    - Must be written by ISO or ETSI, can reference standards produced elsewhere, such as IETF
  - Web based use cases
    - Web flows, OID for Verifiable Credentials, OID for Verifiable Presentations
    - Hey new world, solidify those standards so we can use them and have interoperability
    - Tens of millions of users need to do real web flows with this in the next few years
- Brent
  - Use cases
    - Have unspoken “so that” clause, worker provides assertions about their certification to a company
    - Some holder provides assertion from and `issuer` about `subject` to a `verifier`
      - Assertion is issued in a credential
      - Assertion is provided as a presentation
  - Need WG at IETF so that we can have increased security and focus on automation use cases (automated use)
  - Tech timeline
    - COSE (2022)
    - Three party model
  - OWASP WG is not chartered to this scope
    - Machine identity in supply chains large legal entities like EU itself as “user”
    - Cant assume users have hosted endpoints
    - No `.well-known` paths exist yet for three party, SD-JWT VC oauth IETF WG has one in draft.

![IMG_1463](https://github.com/intel/dffml/assets/5950433/5473b3c4-3a8d-43c4-9bb6-9fa7bd4fd064)
![IMG_1464](https://github.com/intel/dffml/assets/5950433/3f676c00-4eed-4acc-8451-7e1101cfa161)
