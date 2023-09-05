## 2023-01-23 IETF SCITT

> For Alice Initiative we want to enable fully offline decentralized use due to ad-hoc grafting needed for when our nodes go on/offline and when we want to roll dev/test/prod. We want flat files! Not servers you need to run. Our goals are to ensure we can drive interop between sigstore infra and DID/VC infra. We care about this because of our [2nd party plugins](https://github.com/intel/dffml/pulls/1061/files), we want to be able to graft off new trust chains via transparency logs lickety-split.
>
> AI has been been seeing rekor/trillium infra as something we’ll want to bridge to the DID/VC space. Seems like anything in rekor/trillium could be made into VCs to proxy into SSI land.

- https://datatracker.ietf.org/group/scitt/meetings/
- https://meetecho-interims.ietf.org/conference/?group=e82e0525-bb13-44c1-b18d-8bd7595b8ecc
- sigstore presentation from Zachary Newman and Joshua Lock (screenshots from their slides, see above meetings link for full recording)
  - Overlap in goals
  - Talk about some pieces
  - Presentation was about 25 minutes, then discussion
- Both have concept of notarization
- Both have concept of auditing the transparency log
- CA is fulcio
  - Some overlap with ACME
  - > ![image](https://user-images.githubusercontent.com/5950433/214090614-c34431bb-f3c8-4939-a24a-04ea5ec0c2d4.png)
- Goals are to sign with ephemeral keys which are linked via CA issuer (fulcio) to identities
  - > ![image](https://user-images.githubusercontent.com/5950433/214091317-36637825-f15a-4047-9d53-4dfdae1a782b.png)
  - Lightweight attestation of hardware
- Countersignatures also need timestamping for traceability
  - > ![image](https://user-images.githubusercontent.com/5950433/214092038-f597c437-d0d6-4baa-a8f4-7dcc41324ca1.png)
- Centralized log infra
  - > ![image](https://user-images.githubusercontent.com/5950433/214092239-b483a9cd-b749-4ca9-8fcf-d8f3bac42dcb.png)
  - `did:merkle` or merkle-dag would be a decentralized approach to this (just to name one)
- Looking for collaboration
  - > ![image](https://user-images.githubusercontent.com/5950433/214092865-faf7a6a8-3c9d-45cd-a8ed-2df2f9df22d9.png)
- Q&A
  - Can anyone with an email sign?
    - Yes! The signature is valid if the signature happened during the validity pirod, that timestamp has a notarization / signature which is also logged in a transparency log
    - The following help us understand that the signing happened during the validity period
      - signature
      - artifact being signed
      - cert
      - signed timestamp from transparency log
  - What is sigstore doing?
    - It's doing the timestamping
    - It's associating an identity (or rather, proof of control at that time of an identity as was authed to fulcio, thanks Orie)
    - They are acting as a CA
      - Ray: If I want to audit to say that Ray was Ray, I have to walk back to the OIDC to find out that Ray was Ray.
      - Zach: The OIDC tokens aren't safe to publish. We do have a severed link there, dpop looking at that
      - Ray: There a Ephoc timestamping RFC we should all be aware of
        - https://github.com/ietf-rats/draft-birkholz-rats-epoch-marker
        - https://github.com/cbor-wg/time-tag
        - Henk: there also is tsa/tst support for cose in the queue
          - https://www.ietf.org/archive/id/draft-birkholz-cose-tsa-tst-header-parameter-00.html
- Signature transparency log supports plugable types
  - Plain over artifact
    - https://github.com/CycloneDX/specification/issues/155#issuecomment-1399654950
  - One is an in-toto attestation claim (similar to SCITT claim)
  - Could extend
- Perhaps
  - Combine auth to fulcio with OpenIDVC
  - rekor merkle grafted to DID merkle
- Cedric slides
  - > ![image](https://user-images.githubusercontent.com/5950433/214098474-8851cc7a-c00b-46d3-aefc-b6cedbaeeddc.png)
  - Domain specific policies with SCITT
- Related
  - https://docs.sigstore.dev/cosign/overview/
  - https://github.com/w3c-ccg/traceability-interop