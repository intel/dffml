## 2022-09-30 @pdxjohnny Engineering Logs

- in-toto
  - manifest
    - https://docs.sigstore.dev/cosign/attestation
- GitHub Actions
  - https://github.blog/2022-04-07-slsa-3-compliance-with-github-actions/
  - https://github.blog/2021-12-06-safeguard-container-signing-capability-actions/
  - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers#adding-permissions-settings
  - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers#requesting-the-jwt-using-environment-variables
  - https://github.com/slsa-framework/slsa-github-generator/blob/main/.github/workflows/generator_container_slsa3.yml
  - https://security.googleblog.com/2022/04/improving-software-supply-chain.html
  - https://docs.sigstore.dev/fulcio/oidc-in-fulcio/#oidc-token-requirements-with-extracted-claims
  - https://docs.sigstore.dev/cosign/openid_signing/#custom-infrastructure

> For example:

```yaml
jobs:
  job:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/github-script@v6
      id: script
      timeout-minutes: 10
      with:
        debug: true
        script: |
          const token = process.env['ACTIONS_RUNTIME_TOKEN']
          const runtimeUrl = process.env['ACTIONS_ID_TOKEN_REQUEST_URL']
          core.setOutput('TOKEN', token.trim())
          core.setOutput('IDTOKENURL', runtimeUrl.trim())
```

> You can then use curl to retrieve a JWT from the GitHub OIDC provider. For example:

```yaml
    - run: |
        IDTOKEN=$(curl -H "Authorization: bearer $" $ -H "Accept: application/json; api-version=2.0" -H "Content-Type: application/json" -d "{}" | jq -r '.value')
        echo $IDTOKEN
        jwtd() {
            if [[ -x $(command -v jq) ]]; then
                jq -R 'split(".") | .[0],.[1] | @base64d | fromjson' <<< "${1}"
                echo "Signature: $(echo "${1}" | awk -F'.' '{print $3}')"
            fi
        }
        jwtd $IDTOKEN
        echo "::set-output name=idToken::${IDTOKEN}"
      id: tokenid
```

- References
  - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#customizing-the-token-claims
  - https://docs.sigstore.dev/fulcio/oidc-in-fulcio#oidc-token-requirements-with-extracted-claims

![image](https://user-images.githubusercontent.com/5950433/193351919-a3ab6573-e92d-4cc4-9edc-ccf8142e6129.png)

- SPIFFE
  - https://docs.sigstore.dev/security/
    - > #### Proving Identity in Sigstore
      > Sigstore relies on the widely used OpenID Connect (OIDC) protocol to prove identity. When running something like cosign sign, users will complete an OIDC flow and authenticate via an identity provider (GitHub, Google, etc.) to prove they are the owner of their account. Similarly, automated systems (like GitHub Actions) can use Workload Identity or [SPIFFE](https://spiffe.io/) Verifiable Identity Documents (SVIDs) to authenticate themselves via OIDC. The identity and issuer associated with the OIDC token is embedded in the short-lived certificate issued by Sigstore’s Certificate Authority, Fulcio.
- fulcio
  - https://docs.sigstore.dev/fulcio/oidc-in-fulcio#supported-oidc-token-issuers
- TODO
  - [ ] Write the wave (weekly sync meetings and rolling alice engineering logs), correlate the asciinema and the DFFML codebase, leverage CodeGen
    - https://github.com/salesforce/CodeGen