## 2023-09-11 @pdxjohnny Engineering Logs

- https://github.com/fedora-infra/flask-oidc/issues/7#issuecomment-1140935907
- https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
  - https://token.actions.githubusercontent.com/.well-known/openid-configuration
  - https://token.actions.githubusercontent.com/.well-known/jwks
  - https://pyjwt.readthedocs.io/en/latest/usage.html#oidc-login-flow
  - https://pyjwt.readthedocs.io/en/latest/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint
  - https://auth0.com/blog/how-to-handle-jwt-in-python/
    - SSH keys for signing
- TODO
  - [ ] SCITT
    - [x] Auth Middleware plugin scaffolding
      - [x] OIDC plugin - https://github.com/scitt-community/scitt-api-emulator/pull/31