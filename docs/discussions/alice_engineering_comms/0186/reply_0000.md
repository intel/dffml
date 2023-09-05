## 2023-02-22 @pdxjohnny Engineering Logs

- https://www.youtube.com/watch?v=hbe3CQamF8k
- Alignment with Ned on KERI, need further discussion on if we need SCITT over it, seems like yes still.
  - KERI+SCITT would enable fully isolated SSI transparency logs with hardware roots of trust (DICE). This plus OpenSSF Metrics use case is POC of decentralized AI driven Trust as a Service. The propagation of trust and remediation enables us to iterate at critical velocity, to enter the fully connected development model (graphic: singularity acceleration asymptote). We're filling out the Entity Analysis Trinity comms and automation which our Living Threat Models rolls along. We have the communication of vulns/problems/issues via architecture and Threat Modeling, VEX/VDR, SBOM. Remediation via AI and testing within CI/CD. Alignment to strategic principles again via Threat Model. The isolated trust chains means orgs or entities can iterate at high speed together or within isolated trains of thought.
  - https://opentitan.org/
- https://github.com/WebOfTrust/signify-ts/issues/8#issuecomment-1376401489
- https://github.com/WebOfTrust/did-keri-resolver/blob/f77303334a971b21f96e0f952ef2b4793b05686e/src/dkr/didcomm/utils.py#L115
  - `await DidKeriResolver().resolve()`
  - https://github.com/WebOfTrust/did-keri-resolver/blob/f77303334a971b21f96e0f952ef2b4793b05686e/src/dkr/didcomm/hello-world.py#L8
    - `alice = createKeriDid()`
- https://cs.github.com/jolocom/ddoresolver-rs/blob/85f1d71a9c9774693fcfbd679586438c65e7ed2f/src/keri.rs
- https://github.com/DvorakDwarf/Infinite-Storage-Glitch
  - grep video encoding
- https://github.com/WebOfTrust/vLEI/blob/267c6c7720902eb0e43b0fcc8d9b5f2f63fd5bfa/samples/acdc/legal-entity-engagement-context-role-vLEI-credential.json

```console
$ gh webhook forward --repo=intel/dffml --events=discussion_comment --url=https://vcs.activitypub.securitytxt.dffml.chadig.com/webhook/cadb4a72003b7892c814d4fdfa254559fce998b070a091b318821883e81bd51c9170ece5bb1c66b90e32fbf23d05ecd9
Forwarding Webhook events from GitHub...
2023/02/23 00:24:00 [LOG] received the following event: discussion_comment
```

- https://github.com/TBD54566975/dwn-aggregator/blob/4269041795f004fe819a4f1d9cdd3a13d979be0d/examples/pubsub.js#L27
  - How do we combine `did:keri:`, ActivityPub security.txt, and SCITT OCI image security?