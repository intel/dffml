## 2023-04-28 @pdxjohnny Engineering Logs

- https://github.com/ZrrSkywalker/LLaMA-Adapter
- https://github.com/tspascoal/dependabot-alerts-helper
- https://github.com/advanced-security/policy-as-code
- https://github.com/scitt-community/scitt-api-emulator/pull/27#issuecomment-1528073552
  - Orie reviewed!!!!! ❤️
  - Response duplicated below for the logs
  - Why is it imperative that we allow for full detail (object) in error response? (https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/62#issuecomment-1526492830)
    - To facilitate the pull-request review style conversation on attempt to insert
    - Without this SCITT is meh (of annoying use, we have to create sort lived content addressed responses with details for failure shoved in the detail string)

---

In the example documentation the policy engine is indeed implemented with python files. However this implementation lives only within that documentation file (although it's currently used within the associated tests). The intent here was to show that the execution of the engine is arbitrary, as far as the SCITT API Emulator is concerned. Policy engine results are communicated through the the presence of files and the reasoning for denial or failure potentially through their contents (`reason.json` in the example docs and tests).

The plan is to expand on this pull request in a future pull request to leverage policy referenced as content addressable JSON based abstraction of the policy, for example: `did:web:registry.example.com:policy-as-code:blocklist%40sha256%3Aaaaaaaaa`. The policy could then itself be secured following the [Distributing with OCI Registries, with SCITT Enhancements](https://scitt.io/distributing-with-oci-scitt.html) document.

```console
$ export REGISTRY=registry.example.com
$ export PROJECT=policy-as-code
$ export IMAGE=blocklist
$ export DIGEST=sha256:aaaaaaaa
$ export DID_WEB_OF_POLICY=$(python -c 'import sys, urllib; print(urllib.parse.quote(sys.argv[-1]))' "${IMAGE}@${DIGEST}")
$ echo "$(cat workspace/service_parameters.json)" \
    | jq ".insertPolicy = \"did:web:${REGISTRY}:${PROJECT}:${DID_WEB_OF_POLICY}\"" \
    | tee workspace/service_parameters.json.new \
    && mv workspace/service_parameters.json.new workspace/service_parameters.json
{
  "serviceId": "emulator",
  "treeAlgorithm": "CCF",
  "signatureAlgorithm": "ES256",
  "serviceCertificate": "-----BEGIN CERTIFICATE-----",
  "insertPolicy": "did:web:registry.example.com:policy-as-code:blocklist%40sha256%3Aaaaaaaaa"
}
$ reg layer --skip-ping --auth-url "${REGISTRY}" "${REGISTRY}/${PROJECT}/${IMAGE}@${DIGEST}" | tar -z --extract --to-stdout --wildcards --no-anchored 'policy.json' | tee insertPolicy.json
$ nodemon -e .cose --exec 'find workspace/storage/operations -name \*.cose -exec nohup sh -xc "echo {} && policy-as-code-engine insertPolicy.json {}" \;'
```

As seen in the example above the `nodemon` command in the documentation would be replaced by the `policy-as-code-engine` watching the workspace directory directly or it would continue to run the engine. The engine implements the evaluation of the JSON and executes implementations analogous or the same as the existing python files from the current revision of the docs. Effectively upleveling the existing implementation in the docs into a policy-as-code defined by the JSON workflow syntax with an associated schema and interpretation methodology of the schema.

In the above example `insertPolicy.json` would be the SCITT instance wide insert policy, which as the SCITT docs suggest could be made available at a discoverable location (webfinger?). The instance wide policy might contain per-issuer policy (or other differentiation criteria). On failure to insert (https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/62#issuecomment-1526492830) the hope would be to reply via the `error` object to the claim insert request with the JSON representation of the policy which resulted in the failure or denial. The error object could contain the specific part of the instance wide policy which caused a denial or failure for the given claim insertion.

---

- References
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/62#issuecomment-1526492830
  - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#example-requiring-a-reusable-workflow
  - https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/using-openid-connect-with-reusable-workflows
  - https://github.com/tspascoal/gh-oidc-sub

```console
$ gh extensions install tspascoal/gh-oidc-sub
Cloning into '/home/pdxjohnny/.local/share/gh/extensions/gh-oidc-sub'...
remote: Enumerating objects: 22, done.
remote: Counting objects: 100% (22/22), done.
remote: Compressing objects: 100% (16/16), done.
Receiving objects: 100% (22/22), 9.41 KiB | 9.41 MiB/s, done.
Resolving deltas: 100% (3/3), done.
remote: Total 22 (delta 3), reused 4 (delta 0), pack-reused 0
✓ Installed extension tspascoal/gh-oidc-sub
$ (cd /home/pdxjohnny/.local/share/gh/extensions/gh-oidc-sub && git log -n 1)
commit b07ae8c7acc6612a46257b120ca0efb83ff796dd (HEAD -> main, origin/main, origin/HEAD)
Author: Tiago Pascoal <tiago@pascoal.net>
Date:   Thu Feb 2 19:14:14 2023 +0000

    upload shellcheck results to code scanning
$ gh oidc-sub set --repo intel/dffml --subs "job_workflow_ref,repository_id,repository_owner_id"
{}
$ gh oidc-sub get --repo intel/dffml
{
  "use_default": false,
  "include_claim_keys": [
    "job_workflow_ref",
    "repository_id",
    "repository_owner_id"
  ]
}
```

- https://github.com/ocapn/ocapn/pull/44
- https://mastodon.social/@bengo/110278699508517744
- TODO
  - [ ] dffml-model-tensorflow auto approve pull requests from known `job_workflow_ref,repository_id,repository_owner_id` reusable workflow on DFFML push to main bump pinned sha within main of downstream
    - We'll later patch renovate and dependabot to accept these events from the federated event space
      - Notary and TS combined within dffml reusable emit event for receipt, this is our SCITT notarizing proxy