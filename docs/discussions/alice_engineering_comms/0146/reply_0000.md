- https://circleci.com/blog/jan-4-2023-incident-report/
  - Annnnnnnnd this is why ephemeral attested compute for CI/CD and den envs (on top of chromebook style hardened clients)
- https://github.com/quartzjer/did-jwk/blob/main/spec.md
- merkle trees
  - https://github.com/transmute-industries/merkle-proof/blob/main/test/alignment.test.ts
  - https://github.com/digitalbazaar/pyld
  - https://medium.com/transmute-techtalk/briefcase-a-fun-way-to-share-small-fragments-of-structured-data-using-decentralized-identifiers-c13eea74550c
  - https://www.rfc-editor.org/rfc/rfc7516
  - https://github.com/confidential-containers/attestation-agent
    - We want the CC to come up and attest to whatever via VC ideally cross verified by places it sends the VC with a SCITT log
      - This enables hardware root of trust SSI Eden nodes to truly peer to peer auth
        - This is helpful for dev pipeline use cases (ref: android key signing) and other "offline"
          aka sperate roots of trust or ephemeral roots of trust (testing) use cases. Which are
          EVERYWHERE with CI/CD, if we do this right then it'll be "out of the box" easy for any
          software project to spin secure dev/test/prod PKI and associated transparency logs for
          SBOM, VEX, VDR, etc.
- https://oras.land/blog/oras-looking-back-at-2022-and-forward-to-2023/
- DWN and VC status update: https://twitter.com/i/spaces/1mrGmkbnWQkxy
- https://blog.humphd.org/pouring-language-through-shape/
- https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
- https://datatracker.ietf.org/doc/html/draft-ietf-oauth-dpop
- Alignment to common authentication and authorization patterns helps us communicate
  - https://w3c-ccg.github.io/vp-request-spec/#peer-to-peer
- https://github.com/deepmind/tracr#how-tracr-works-conceptually
- Alice should close issues and PRs if recommended community standards files are now present
- Vulnerability Disclosure Program (VDP)
  - How could Alice help our projects have a machine readable or machine parsable VDP to direct to SCITT, VEX, VDR, SBOM locations
- Container image build files (melange, Dockerfile, PKGBUILD, etc.) -> extract build args -> manifest
  - Tag commits for git clones