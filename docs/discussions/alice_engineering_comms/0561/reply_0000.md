- If we have an enclave attestation (SLSA 4) for policy engine + policy which matches initial TCB federating set measurement. Then we want to federate a statement. On Decentralized Trust.
  - Talk to Ned about format from verifier, as recursive receipt?
    - This is why “it’s recursive”. Initial TCB bootstraps trust in measurements. TSs are where receipts for measurements are logged.
  - This needs to go in the CBOR API as an optional field
    - Value is URN of statement containing attestation or reference to
- SCRAPI changing operation id on each response to check status. Return step details
  - kcp streaming log urn in response
    - kcp/k8s OIDC token issuance leveraging that RBAC