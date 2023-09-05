## 2022-10-14 @pdxjohnny Engineering Logs

- Alice helps you understand what your software is EATing, what’s the health of its software supply chain (food as the biological supply chain). You are what you EAT and your software is its development health! You get out what you put in lifecycle wise.
- https://github.com/ossf/scorecard/blob/main/docs/checks.md
- https://gist.github.com/pdxjohnny/f56e73b82c1ea24e1e7d6b995a566984
- https://github.com/sigstore/gitsign#environment-variables
  - > Env var |    |    |    |
    > -- | -- | -- | --
    > GITSIGN_FULCIO_URL | ✅ | https://fulcio.sigstore.dev | Address of Fulcio server
    > GITSIGN_LOG | ❌ |   | Path to log status output. Helpful for debugging when no TTY is available in the environment.
    > GITSIGN_OIDC_CLIENT_ID | ✅ | sigstore | OIDC client ID for application
    > GITSIGN_OIDC_ISSUER | ✅ | https://oauth2.sigstore.dev/auth | OIDC provider to be used to issue ID token
    > GITSIGN_OIDC_REDIRECT_URL | ✅ |   | OIDC Redirect URL
    > GITSIGN_REKOR_URL | ✅ | https://rekor.sigstore.dev | Address of Rekor server