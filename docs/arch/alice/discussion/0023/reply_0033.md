What makes web3 / Peer DIDs different than classical blockchain technologies? https://identity.foundation/peer-did-method-spec/#diddocs

> Early explorations of this DID method used the term microledger for backing storage. This term has some resonance, in that backing storage is an append-only record of immutable transactions. However, ledger technology requires strong ordering, whereas our ordering requirements are somewhat relaxed. What we need is closer to the approach of [triple-signed receipts](https://opentransactions.org/wiki/Triple-Signed_Receipts) or [KERI](https://arxiv.org/abs/1907.02143), not to a ledger or blockchain maintained by pure consensus. Thus, we have chosen not to emphasize the term here, because it may feel intimidating to some, and because the actual storage mechanism in an implementation of this method could be a simple file, a database, or anything else that provides suitable features.

---

- [ ] Use tdDEX and Peer DIDs for first context issuance to chain as request for execution.
- [ ] Treat DID methods as manifests
  - [ ] `did:schema:` 
  - [ ] `did:manifest:` - These we can use for encoding operations. can also just have flows added to chain which return static data.
- [ ] Define manifest DID method
  - [ ] Make fields for system context attributes
    - [ ] We can leverage DID update resolution mechanisms if we define as a DID method
- [ ] Use tbDEX to create bit
- [ ] Later: Leverage keybase for web2 identity oracle (require only access oracle data run on proxies with attested hardware for provenance)
  - https://mlsteele.keybase.pub/.well-known/stellar.toml
  - https://book.keybase.io/guides/proof-integration-guide#1-config
  - https://book.keybase.io/guides/proof-integration-guide#proof-verification-script
  - https://github.com/intel/dffml/issues/1284

---

- https://twitter.com/dizaytsev/status/1524116790657179649
- https://developers.redhat.com/blog/2020/04/02/how-to-write-an-abi-compliance-checker-using-libabigail
  - Risk of changes