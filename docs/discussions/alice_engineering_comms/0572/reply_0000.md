## 2024-03-23 @pdxjohnny Engineering Logs

- https://notes.ietf.org/notes-ietf-119-scitt
  - Mentions of scitt-action and CI/CD
  - > Orie: apologizes for all of Jenkins
- https://github.com/intel/GenAIExamples/blob/main/CodeGen/codegen/codegen-app/openai_protocol.py
- https://github.com/huggingface/text-generation-inference
- https://github.com/intel/cve-bin-tool-action
- https://github.com/pdxjohnny/scitt-api-emulator/blob/github-action/action.yml
- https://github.com/intel/meta-acrn
- https://codeberg.org/meissa/forgejo/src/branch/forgejo-federated-star/docs/unsure-where-to-put/threat_analysis_star_activity.md
- https://codeberg.org/meissa/forgejo/src/branch/forgejo-federated-star/docs/unsure-where-to-put/blog.md
- https://federated-repo.prod.meissa.de/api/swagger#/activitypub
    > `GET` `/activitypub/repository-id/{repository-id}` Returns the Repository actor for a repo
    > `POST` `/activitypub/repository-id/{repository-id}/inbox` Send to the inbox
    > `GET` `/activitypub/user-id/{user-id}` Returns the Person actor for a user
    > `POST` `/activitypub/user-id/{user-id}/inbox` Send to the inbox
- https://codeberg.org/forgejo/forgejo/issues/59
  - https://forgejo.org/2024-02-monthly-update/
    - > The pull request to implement federated stars made progress. Discussions happened on how a federated Person should be mapped to a local FederatedUser representation. Read more in the activity summary.
      > 
      > The F3 Forgejo driver refactor is complete: it is back where it was about six month ago. The representation of a remote user was split out of the driver as it is generally useful for both data portability and federation.
      > 
      > The federation implementation task list was updated.
- https://github.com/intel/Multi-llms-Chatbot-CloudNative-LangChain
  - https://docs.litellm.ai/docs/completion/function_call
    - We'll intercept function calls and add our SCITT verification, where we construct workflows which our policy engines execute. Agents use workflows to decided what workflows should be added to a new S2C2F ING4 (mirror source) incoming repo to the forge.
  - https://github.com/Helicone/helicone/tree/main
    - Can chain litellm proxy with helicone proxy to use for metrics / observability
- We'll get a recursive bootstraped trust relationship as we go down the dependency rabbit hole again (Volume 1 Chapter 1). Workflows using GitHub Actions all which get mirrored in. Nothing from outside the mirror is allowed through to the forge's 3rd party ING4 set. The mirror is the policy engine which exec's github actions workflows. We'll use forgjo and have the policy engine initiate the request to scan a repo and determine if it's ingestable or not, and if it is, what workflows should be added to it or run regularly or on trigger for it to keep it secure. Ideally auto release rolling is in this set of workflows.
- https://kubernetes.io/docs/reference/access-authn-authz/authentication/#openid-connect-tokens
- Send me a receipt and I issue you a JWT
  - https://github.com/pdxjohnny/httptest/blob/2239666733f9e77221b01425c8cc71fb18062eb4/httptest/oidc.py#L16-L34
  - What is receipt for?
  - Workflow / BOM
  - TCB is source code within forge
  - What is JWT for? Determining if you can request to litellm proxy, forge becomes an instance of an AGI agent. Missalignment via BOM analysis same as source analysis for 3rd party case (could be due to measured lack of security bar, or due to metrics from Entity Analysis Trinity trending in missaligned directions).
  - Entering wonderland
  - You are what you EAT
- https://kubernetes.io/docs/reference/access-authn-authz/authentication/#service-account-tokens
  - `curl --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt -H "Authorization: Bearer /var/run/secrets/kubernetes.io/serviceaccount/" https://kubernetes.default.svc/api/v1/namespaces/{namespace}/serviceaccounts/{name}/token`
    - Use a token in a pod to create a token, can also do via kubectl as admin or other role outside of a pod
  - `export JWT_PUBLIC_KEY_URL="https://k8s|k3s|kcp-api-server/openid/v1/jwks/"`
    - `kind cluster create`
    - `kubectl proxy --port=8080`
    - `curl http://127.0.0.1:8080/openapi/v2 | jq | less -r`
    - `"/.well-known/openid-configuration/"`
    - https://docs.litellm.ai/docs/proxy/token_auth

```console
$ python -m httptest.oidc \
    --issuer https://oidc.svc \
    --audience https://llmproxy.svc \
    --addr 0.0.0.0 \
    --port 8000 \
    --subject test-subject \
    --private-key-pem-path private-key.pem \
    --token-path token.jwt
$ curl -H "Authorization: Bearer $(curl https://oidc.svc/token | jq -r token)" -v https://llmproxy.svc
$ curl -H "Authorization: Bearer $(cat token.jwt)" -v https://llmproxy.svc
```

- https://github.com/pdxjohnny/Multi-llms-Chatbot-CloudNative-LangChain/tree/scitt-validated-tool-use
- https://platform.openai.com/docs/guides/function-calling
- https://platform.openai.com/docs/assistants/tools
- https://python.langchain.com/docs/modules/agents/tools/custom_tools
- https://python.langchain.com/docs/modules/agents/agent_types/openai_tools#using-with-chat-history
- https://sakana.ai/evolutionary-model-merge/
  - Data Flow and Parameter based evolutionary model layer merging
- No need to do JWT stuff within k8s yet
- Focus on assistants API in LLM proxy and langchain tool use (and flow/process stuff in Eze’s API) protocol analysis and validation by SCITT
  - Stream of Consciousness
- Transport Acquisition is about how we know we can trust the potential compute we have available to us and what claims for JWTs we issue based off SCITT receipts.

![Sketch of Transport Acquisition](https://github.com/intel/dffml/assets/5950433/1e586f25-083f-49d4-b239-f0f18baf5805)

- https://radicle.xyz/guides/user
  - SCITT federation via `workspace/storage/*.cbor` as git repo heartwood federated
  - Service Parameters files can be federated under instance FQDN or key ids or something.
- policy engine `request.yml` (dirconf load of workflow.yml ideally) committed to federated git repos for IaC-ish manifest ADR style dispatch
- Phase 0
  - Just manifest federation
    - Federation of different repos always namespaced by owner/tcb
    - Owner as handle, fqdn, string
    - Also owner each jwk of SCITT TS signing key it is root of trust for that TCB identity provider (our Rats relying party) 
      - Build service whoch consumes recipts on git pull and issues JWK. Send JWK to orchestrator to use for job. This can go in policy engine for now but abstract it into its own service later. Then integrate into kcp service account issuer
- https://github.com/intel/dffml/blob/5897cd290e3facfa3739f5b9467a4a3363379d1d/docs/discussions/alice_engineering_comms/0223/reply_0000.md?plain=1#L164
  - Don't worry about federation yet. Just do one TCB with on disk repos.
  - Start with building the service for workload identity using `httptest.oidc` `/token` as a base. Take receipt as POST body.
  - SCITT service issues token
    - Because we're builtin to the policy engine for phase 0, piggyback of transparency-configuration jwks
- docs/registration_polcies.md update do curl calls to loopback or socket policy engine fastapi
- https://github.com/scitt-community/scitt-api-emulator/commit/a8646d512e26b07ee1f7edd2ccdacc921c23a95a
  - Need a revoke token endpoint remove key after lookup by kid after decoding token (POST token in json request body)