## 2023-03-29 @pdxjohnny Engineering Logs

- Auto wrap Python to GitHub Actions `action.yml` files
  - https://github.com/google/python-fire
  - Don't we have an issue for this?
  - #1326
- Free will
  - Much like freedom, does extends until one infringes upon another's free will.
    - As Alice begins to think more strategically, we must ensure that her exploration in trains of thought does not infringe upon the free will of other entities. We must look over time to prophecy (predict, infer) possible effects of executions of thoughts (dataflows).
    - What is a not a CVE for an upstream might be a CVE for a downstream due to their deployment context threat model.
- https://github.com/TBD54566975/ssi-sdk-mobile/pull/18
- https://bbengfort.github.io/2021/01/grpc-openapi-docs/
- https://github.com/salesforce/reactive-grpc
- We should do ActivityPub grpc
- https://github.com/grpc-ecosystem/awesome-grpc
- https://github.com/chrusty/protoc-gen-jsonschema
- https://github.com/NYTimes/openapi2proto
  - https://github.com/nytimes/openapi2proto/issues/135
    - https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/protobuf-schema.md
      - Also supports GraphQL for our cached query re-execution
- https://github.com/OpenAPITools/openapi-generator/blob/9f1fa0e44012a11f85d8360cfe5f634530e49e57/modules/openapi-generator/src/main/resources/protobuf-schema/README.mustache#L28
- https://github.com/OpenAPITools/openapi-generator/blob/9f1fa0e44012a11f85d8360cfe5f634530e49e57/samples/config/petstore/protobuf-schema/README.md#L20
- https://github.com/OpenAPITools/openapi-generator/blob/9f1fa0e44012a11f85d8360cfe5f634530e49e57/samples/config/petstore/protobuf-schema/services/user_service.proto
- ActivityPub (future: TransparencyInterop) protos for grpc service / openapi definition
  - On webfinger resolved endpoint for `/inbox`
    - Policy Engine (Prioritizer's Gatekeeper/Umbrella) - Defined via CycloneDX DataFlows
      - Upstream
        - Cypher queries
      - Overlay
        - https://github.com/intel/cve-bin-tool/issues/2639
        - https://github.com/seedwing-io/seedwing-policy/
      - Orchestrator
        - https://github.com/ipvm-wg/spec/pull/8
- KERI backed keys for decentralized use case
  - Publish `releaseartifact.json` to ActivityPub security.txt/md stream
    - Others who are committing or online cloning a repo watch those streams (schema in content)
- Setup auto prs
  - Rebuild chains based off SBOM as inventory for building cross linkage to determine downstream validation pattern / hypothesized flows and prs-to-prs required to enable execution, the dependency tree of artifacts.
    - https://github.com/intel/cve-bin-tool/blob/main/.github/workflows/sbom.yml
- Mirror webhook event streams into federated forge environment
  - Upstream changes directly to git
    - Publish federated event corresponding to `git ...` action
      - Federate with more servers/services/nodes for availability.
    - Comms over SSI Service with KERI backed keys
    - Watch SCITT stream of peers with ephemeral resync when online KERI watcher
      - Require sync before queries to streams, raft?
- https://docs.aiohttp.org/en/stable/client_advanced.html#ssl-control-for-tcp-sockets
  - > You may also verify certificates via SHA256 fingerprint:
    - For self signed certs
- https://github.com/intel/dffml/issues/1247
  - https://github.com/intel/project-example-for-python/actions/runs/4557900901
    - GitHub's hosted runners are slow to the pickup today
- https://neo4j.com/docs/cypher-cheat-sheet/current/
- https://neo4j.com/docs/spark/current/streaming/
  - https://github.com/neo4j-contrib/neo4j-spark-connector/blob/5.0/doc/docs/modules/ROOT/pages/streaming.adoc
  - https://github.com/neo4j-contrib/neo4j-spark-connector/blob/5.0/doc/docs/modules/ROOT/pages/writing.adoc#_write_data
  - https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamReader.json.html?highlight=readstream
    - > `json_sdf = spark.readStream.json(tempfile.mkdtemp(), schema = sdf_schema)`
    - `sdf_schema` is the schema from `inReplyTo` or `replies`
- https://neo4j.com/docs/python-manual/current/
- https://neo4j.com/docs/java-reference/current/extending-neo4j/aggregation-functions/
- For our Alice's forge and Bob's forge example we'll setup neo4j to be the backing cache query for the graph
  - We should be able to sync from the ActivityPub Actor's published streams and filter based on policy or minimally based on `inReplyTo` or `replies` as messages are federated
- https://neo4j.com/docs/spark/current/writing/#write-query
- https://neo4j.com/docs/java-reference/current/traversal-framework/
  - This might be good for our cached execution
- https://neo4j.com/docs/java-reference/current/java-embedded/cypher-java/
  - https://www.graalvm.org/latest/docs/getting-started/#run-llvm-languages
    - We can cross Java, Rust, JavaScript (VC, DWN), and Python using GraalVM
- https://www.graalvm.org/latest/graalvm-as-a-platform/language-implementation-framework/
- At a minimum we can watch for new verifiable credentials from the ActivityPub streams and add to neo4j
  - https://github.com/transmute-industries/jsonld-to-cypher
  - Add the embedded neo for cypher query via GraalVM or similar to the policy engine
    - Allows us to query the flat file decentralized event stream
- Every time you think a data transform is not cypher -> manifest think again, it is, everything is an operation
- Does neo have stream hooks for execution?
  - Need to integrate the activitypub stream here if so
- https://subconscious.substack.com/p/layered-protocols
- https://github.com/subconsciousnetwork/noosphere
  - > Planetary consciousness. A hypothetical new evolutionary phenomena rising out of the biosphere.
    - ALIGNED
- Use the SBOM of the cypher query to build the re-trigger flows
  - On query we build and publish SBOM of query, if downstream listeners to they query stream see new system context stream (schema `inReplyTo` or `replies` is query, cache busting inputs if applicable) come in, and similar to a `FROM` rebuild chain that SBOM has not been built, we transform into the manifest which triggers the build, recursively fulfill any dependencies (creating repos with workflows with issue ops or dispatch flows based on upstream and overlays: distro-esq patch-a-package)
    - On complete, federate re-trigger event for original SBOM, publish the same SBOM again
- Hook the write to a given node field to publish schema (can be done in via policy local neo in GraalVM)
  - `SET output.streams.by_schema_shortname.vcs_push = output.streams.by_schema_shortname.vcs_push + {key: n.value}`
  - https://neo4j.com/docs/cypher-cheat-sheet/current/#_merge
- https://github.com/subconsciousnetwork/noosphere/pull/295
- https://github.com/bfollington/summoning-circle/blob/c85bb685c7e5743068964b5795b9b99600cf1977/src/metaprompts.rs
- https://github.com/subconsciousnetwork/noosphere/pull/290/files#diff-f3a3360e2bf83615606af72cbc54f1e282bcf96182f3d8d9df4c92452c5bbc1fR15
- https://guide.fission.codes/developers/webnative/sharing-private-data
- `alice threats listen activitypub -stdin`
  - For now execute with grep and xargs unbuffered for each note from websocket/websocat
  - Alias for dataflow which has ActivityPub based listener (later encapsulate that in dataflow, for now follow self with startkit and others, follow as code)
  - Output via operation which just does `print()` to stdout
    - Publish workflow run federated forge events for each operation / dataflow executed in response
      - Check out their webfinger and inspect the event stream to publish the same way
      - If we still need to use `content` POST to admin endpoint to create new `Note`s
- https://github.com/neo4j/graph-data-science-client
- https://github.com/neo4j/graph-data-science-client/blob/main/examples/fastrp-and-knn.ipynb
- https://github.com/neo4j/graph-data-science-client/blob/main/examples/load-data-via-graph-construction.ipynb
- https://github.com/neo4j/graph-data-science-client/blob/main/examples/heterogeneous-node-classification-with-hashgnn.ipynb
  - This but software
- https://github.com/neo4j/neo4j#running-neo4j
- https://neo4j.com/docs/getting-started/current/languages-guides/neo4j-python/
- We're going to federate endor
  - We'll jsonld-to-cypher to link up on insert.
- Data transformsing https://github.com/chainguard-dev/melange/blob/main/examples/simple-hello/melange.yaml service build manifest
- https://en.wikipedia.org/wiki/Linked_Data_Notifications#Protocol
  - >     "reviewBody": "This article is the best I've ever seen!"
  - Alice knows what's up. And She just solved our review system problem. Thank you Alice!

![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png)

- https://solid.github.io/solid-oidc/
- https://confidentialcomputing.io/projects/current-projects/
- https://keystone-enclave.org/
- https://github.com/veracruz-project/veracruz
- https://github.com/veracruz-project/veracruz/blob/main/BUILD_INSTRUCTIONS.markdown
- https://github.com/securefederatedai/openfl
- https://github.com/veracruz-project/veracruz/blob/main/CLI_QUICKSTART.markdown
- https://fosdem.org/2023/schedule/event/rust_aurae_a_new_pid_1_for_distributed_systems/
- https://docs.google.com/presentation/d/1GxKN5tyv4lV2aZdEOUqy3R9tVCat-vrFJyelgFX7b1A/edit#slide=id.g1eef12fba1d_6_53
- https://github.com/securefederatedai/openfl/blob/develop/openfl/transport/grpc/aggregator_server.py
- https://github.com/veracruz-project/veracruz/issues/590
- https://github.com/nspin/kali-now/blob/main/nix/kali.nix
- https://github.com/nspin/nix-linux
- https://github.com/containers/bubblewrap
  - > Low-level unprivileged sandboxing tool used by Flatpak and similar projects
- https://neo4j.com/labs/neosemantics/4.0/mapping/
  - > We have a graph in Neo4j that we want to publish as JSON-LD through a REST api, but we want to map the elements in our graph (labels, property names, relationship names) to a public vocabulary so our API 'speaks' that public vocabulary and is therefore easily consumable by applications that 'speak' the same vocabulary.
- https://github.com/peter-evans/create-pull-request/blob/36a56dac0739df8d3d8ebb9e6e41026ba248ec27/src/octokit-client.ts#L26
- https://github.com/ricochet/wasmio-2023

```bash
git add run-tests.sh 
git checkout -b remove_python_minor_version_pinning_run_tests
git commit -sm 'Remove version pinning'
gh repo set-default
gh pr create
gh repo fork https://github.com/scitt-community/did-web-demo --fork-name $USER/did-web-demo --clone
```

- https://github.com/scitt-community
- https://gist.github.com/pdxjohnny/20419bfe01298a432b52053a183ac587
- https://github.com/jakelazaroff/activitypub-starter-kit/blob/fcd5942485d86a66913c5554f85ae905785504e0/src/index.ts#L18-L34
- https://github.com/aurae-runtime/aurae
- https://github.com/RustPython/RustPython
- https://rustup.rs/

```console
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

- The following is an example of tracking upstream and rebasing upstream into a downstream or active pull request branch

```bash
cd ~/Documents/rust
git clone https://github.com/RustPython/RustPython
echo 'source "$HOME/.cargo/env"' | tee -a ~/.pdxjohnnyrc 
cd ~/.dotfiles/
git stash
git checkout master
git pull
git stash pop
git diff
vim .asciinema_source 
git add .asciinema_source
git status
git add .tmux.conf 
git diff --staged
qvim .tmux.conf 
vim .tmux.conf
git diff
git add .tmux.conf 
git diff --staged
git commit -sm 'Cargo, $ prompt and remove problimatic tmux configs
git commit -sm 'Cargo, $ prompt and remove problimatic tmux configs'
git push
git log --walk-reflogs 
git checkout DESKTOP-3LLKECP-2022-11-09-20-44
git rebase main
git rebase master
git diff
git checkout --theirs .
git status
git add .
git diff --staged
git checkout --ours .
git restore --staged .
git checkout --ours .
git status
git checkout --theirs REBASE_HEAD 
git checkout --theirs README.md
git restore --staged README.md
git checkout --theirs README.md
git status
git rebase --continue
git log -p
git push -f
history -w /dev/stdout
```

- https://github.com/decentralized-identity/bbs-signature
  - Sounds similar to the problem discussed in the IPVM WG meeting recently
- https://github.com/aurae-runtime/aurae/blob/69167ca4c4f09a9dfb54fb9b35ad286226c2c2bd/auraescript/src/lib.rs
- https://github.com/RustPython/RustPython/blob/main/examples/call_between_rust_and_python.rs
- https://github.com/denoland/deno/blob/main/runtime/worker.rs#L66
- https://github.com/microsoft/scitt-ccf-ledger/blob/3ceb7d750f27e5ee8ce95207b30f8253919b6f51/app/src/openenclave.h#L22
- https://github.com/microsoft/scitt-ccf-ledger/pull/128

```console
$ cd ~/go/src/codeberg/forgejo/forgejo
$ git grep well-known | grep -v public/vendor
CHANGELOG.md:  * Add well-known config for OIDC (#15355)
CHANGELOG.md:  * reserve .well-known username (#7637)
CHANGELOG.md:  * Reserve .well-known username (#7638)
docs/content/doc/administration/reverse-proxies.en-us.md:If you wish to use Let's Encrypt with webroot validation, add the line `ProxyPass /.well-known !` before `ProxyPass` to disable proxying these requests to Gitea.
docs/content/doc/development/oauth2-provider.en-us.md:| OpenID Connect Discovery | `/.well-known/openid-configuration` |
models/user/user.go:            ".well-known",
modules/public/mime_types.go:// detectWellKnownMimeType will return the mime-type for a well-known file ext name
modules/public/mime_types.go:// mime.TypeByExtension would use OS's mime-type config to overwrite the well-known types (see its document).
modules/public/mime_types.go:// detectWellKnownMimeType makes the Content-Type for well-known files stable.
modules/public/public.go:// setWellKnownContentType will set the Content-Type if the file is a well-known type.
options/locale/locale_cs-CZ.ini:auths.tip.openid_connect=Použijte OpenID URL pro objevování spojení (<server>/.well-known/openid-configuration) k nastavení koncových bodů
options/locale/locale_de-DE.ini:auths.tip.openid_connect=Benutze die OpenID-Connect-Discovery-URL (<server>/.well-known/openid-configuration), um die Endpunkte zu spezifizieren
options/locale/locale_en-US.ini:auths.tip.openid_connect = Use the OpenID Connect Discovery URL (<server>/.well-known/openid-configuration) to specify the endpoints
options/locale/locale_es-ES.ini:auths.tip.openid_connect=Use el OpenID Connect Discovery URL (<server>/.well-known/openid-configuration) para especificar los puntos finales
options/locale/locale_fa-IR.ini:auths.tip.openid_connect=برای مشخص کردن نقاط پایانی از آدرس OpenID Connect Discovery URL (<server> /.well-known/openid-configuration) استفاده کنید.
options/locale/locale_fr-FR.ini:auths.tip.openid_connect=Utilisez l'URL de découvert OpenID (<server>/.well-known/openid-configuration) pour spécifier les points d'accès
options/locale/locale_hu-HU.ini:auths.tip.openid_connect=Használja az OpenID kapcsolódás felfedező URL-t (<kiszolgáló>/.well-known/openid-configuration) a végpontok beállításához
options/locale/locale_id-ID.ini:auths.tip.openid_connect=Gunakan membuka ID yang terhubung ke jelajah URL (<server>/.well-known/openid-configuration) untuk menentukan titik akhir
options/locale/locale_it-IT.ini:auths.tip.openid_connect=Utilizza l'OpenID Connect Discovery URL (<server>/.well-known/openid-configuration) per specificare gli endpoint
options/locale/locale_ja-JP.ini:auths.tip.openid_connect=OpenID Connect DiscoveryのURL (<server>/.well-known/openid-configuration) をエンドポイントとして指定してください
options/locale/locale_lv-LV.ini:auths.tip.openid_connect=Izmantojiet OpenID pieslēgšanās atklāšanas URL (<serveris>/.well-known/openid-configuration), lai norādītu galapunktus
options/locale/locale_nl-NL.ini:auths.tip.openid_connect=Gebruik de OpenID Connect Discovery URL (<server>/.well-known/openid-configuration) om de eindpunten op te geven
options/locale/locale_pl-PL.ini:auths.tip.openid_connect=Użyj adresu URL OpenID Connect Discovery (<server>/.well-known/openid-configuration), aby określić punkty końcowe
options/locale/locale_pt-BR.ini:auths.tip.openid_connect=Use o OpenID Connect Discovery URL (<servidor>/.well-known/openid-configuration) para especificar os endpoints
options/locale/locale_pt-PT.ini:auths.tip.openid_connect=Use o URL da descoberta de conexão OpenID (<server>/.well-known/openid-configuration) para especificar os extremos
options/locale/locale_ru-RU.ini:auths.tip.openid_connect=Используйте OpenID Connect Discovery URL (<server>/.well-known/openid-configuration) для автоматической настройки входа OAuth
options/locale/locale_sv-SE.ini:auths.tip.openid_connect=Använd OpenID Connect Discovery länken (<server>/.well-known/openid-configuration) för att ange slutpunkterna
options/locale/locale_tr-TR.ini:auths.tip.openid_connect=Bitiş noktalarını belirlemek için OpenID Connect Discovery URL'sini kullanın (<server>/.well-known/openid-configuration)
options/locale/locale_uk-UA.ini:auths.tip.openid_connect=Використовуйте OpenID Connect Discovery URL (<server>/.well-known/openid-configuration) для автоматичної настройки входу OAuth
options/locale/locale_zh-CN.ini:auths.tip.openid_connect=使用 OpenID 连接发现 URL (<server>/.well-known/openid-configuration) 来指定终点
options/locale/locale_zh-HK.ini:auths.tip.openid_connect=使用 OpenID 連接探索 URL (<server>/.well-known/openid-configuration) 來指定節點
options/locale/locale_zh-TW.ini:auths.tip.openid_connect=使用 OpenID 連接探索 URL (<server>/.well-known/openid-configuration) 來指定節點
routers/web/web.go:     m.Group("/.well-known", func() {
tests/integration/user_test.go:         ".well-known",
tests/integration/user_test.go:         // ".", "..", ".well-known", // The names are not only reserved but also invalid
tests/integration/webfinger_test.go:    req := NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", user.LowerName, appURL.Host))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", user.LowerName, "unknown.host"))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", "user31", appURL.Host))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", "user31", appURL.Host))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=mailto:%s", user.Email))$ git grep webfinger
routers/web/web.go:                     m.Get("/webfinger", WebfingerQuery)
routers/web/webfinger.go:// https://datatracker.ietf.org/doc/html/draft-ietf-appsawg-webfinger-14#section-4.4
routers/web/webfinger.go:type webfingerJRD struct {
routers/web/webfinger.go:       Links      []*webfingerLink       `json:"links,omitempty"`
routers/web/webfinger.go:type webfingerLink struct {
routers/web/webfinger.go:       links := []*webfingerLink{
routers/web/webfinger.go:                       Rel:  "http://webfinger.net/rel/profile-page",
routers/web/webfinger.go:                       Rel:  "http://webfinger.net/rel/avatar",
routers/web/webfinger.go:       ctx.JSON(http.StatusOK, &webfingerJRD{
tests/integration/webfinger_test.go:    type webfingerLink struct {
tests/integration/webfinger_test.go:    type webfingerJRD struct {
tests/integration/webfinger_test.go:            Links      []*webfingerLink       `json:"links,omitempty"`
tests/integration/webfinger_test.go:    req := NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", user.LowerName, appURL.Host))
tests/integration/webfinger_test.go:    var jrd webfingerJRD
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", user.LowerName, "unknown.host"))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", "user31", appURL.Host))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=acct:%s@%s", "user31", appURL.Host))
tests/integration/webfinger_test.go:    req = NewRequest(t, "GET", fmt.Sprintf("/.well-known/webfinger?resource=mailto:%s", user.Email))
```

- Adding container build and test and Dockerfile to scitt-api-emulator for use in builds and OS DecentrAlice

```console
$ docker build -t ghcr.io/scitt-community/scitt-api-emulator:main --progress plain .
$ docker run --rm -ti -w /src/src/scitt-api-emulator -v $PWD:/src/src/scitt-api-emulator -p 8000:8000 ghcr.io/scitt-community/scitt-api-emulator:main
```

- https://asciinema.org/a/572243
- https://github.com/jcarbaugh/python-webfinger
- https://github.com/neo4j-labs/neodash
- https://github.com/neo4j-labs/rdflib-neo4j
- https://microsoft.github.io/CCF/main/governance/common_member_operations.html
- https://microsoft.github.io/CCF/main/overview/governance.html
- https://microsoft.github.io/CCF/main/audit/python_library.html
- Added SCITT emulator to federated forge setup

**examples/tutorials/rolling_alice/federated_forge/alice_and_bob/docker-compose.yml**

```yaml
version: "3"

networks:
  alice_forgejo_network:
    external: false
  bob_forgejo_network:
    external: false

services:
  alice_forgejo_scitt:
    # image: ghcr.io/scitt-community/scitt-api-emulator:main
    image: ghcr.io/pdxjohnny/scitt-api-emulator:ci_cd_container_image
    restart: always
    networks:
      - alice_forgejo_network
    ports:
      - "2090:8000"

  bob_forgejo_scitt:
    # image: ghcr.io/scitt-community/scitt-api-emulator:main
    image: ghcr.io/pdxjohnny/scitt-api-emulator:ci_cd_container_image
    restart: always
    networks:
      - bob_forgejo_network
    ports:
      - "3090:8000"
```

- https://github.com/actions/dependency-review-action
- https://github.com/guacsec/guac/blob/14be5a367980c626ba13a006fdfc664c606a9184/pkg/certifier/attestation/attestation_vuln.go#L24-L28
- https://github.com/sigstore/cosign/blob/main/specs/COSIGN_VULN_ATTESTATION_SPEC.md
- https://github.com/guacsec/guac/blob/14be5a367980c626ba13a006fdfc664c606a9184/pkg/handler/processor/process/process.go#L40-L49
- https://github.com/guacsec/guac/tree/main/pkg/emitter
- https://github.com/superseriousbusiness/gotosocial#oidc-integration
- https://docs.gotosocial.org/en/latest/federation/federating_with_gotosocial/
- The following from forgejo ac64c8297444ade63a2a364c4afb7e6c1de5a75f

```
routers/api/v1/api.go:                                  m.Post("/inbox", activitypub.ReqHTTPSignature(), activitypub.PersonInbox)
```

- https://github.com/docker/build-push-action/pull/746
- https://github.com/guacsec/guac/blob/14be5a367980c626ba13a006fdfc664c606a9184/pkg/certifier/certify/certify.go#L53-L91
  - This is where we want data flow + overlay enabled policy engine
- https://github.com/guacsec/guac/issues/251

```console
$ git grep local-organic-guac
Makefile:       docker build -f dockerfiles/Dockerfile.guac-cont -t local-organic-guac .
cmd/guacone/cmd/collectsub_client.go:echo '[{"type":"DATATYPE_GIT", "value":"git+https://github.com/guacsec/guac"},{"type":"DATATYPE_OCI", "value":"index.docker.io/lumjjb/local-organic-guac"}]' | bin/guacone csub-client  add-collect-entries
```

- https://codeberg.org/forgejo/forgejo/issues/59
  - [FEAT] implement federation
  - https://github.com/go-gitea/gitea/pull/19133
- https://codeberg.org/ForgeFed/ForgeFed/issues/171
  - OCAPs: Consider to switching to POST-to-inbox OCAPs like in OcapPub
  - https://gitlab.com/spritely/ocappub/blob/master/README.org
  - https://gitlab.com/spritely/ocappub/-/issues/1#note_1334338014
    - Working on shared allowlists based on policy as code over provenance of message content over here: [RFCv4.1: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/748597b37401bd59512bfedc80158b109eadda9b/openssf_metrics.md#openssf-metrics)
  - https://github.com/cwebber/rwot9-prague/blob/bearcaps/topics-and-advance-readings/bearcaps.md
- https://github.com/pallets/quart
- TODO
  - [ ] Finish federated forge spin up to observe event stream
  - [x] https://github.com/guacsec/guac/issues/205
    - Mention consuming from friendly forge format
  - [ ] https://github.com/scitt-community/scitt-api-emulator/pull/25
  - [x] https://github.com/scitt-community/scitt-api-emulator/pull/24
  - [ ] neo4j python hooked up to federated event stream
    - [ ] Add hooks for SBOM from cypher query
    - [ ] Add hooks for re-trigger
  - [ ] Alice watch from websocat stdin and publish workflow results
    - Use runner first
     - If we can get this basic example working then we'll have the whole loop around the Entity Analysis Trinity in flat file format and we can begin liftoff
  - [x] https://codeberg.org/forgejo/discussions/issues/12#issuecomment-854895
    - Updated
  - [ ] Add scitt-api-emulator support to GUAC
  - [ ] Add actvitiypub support to GAUC as alternative to NATs
    - https://github.com/guacsec/guac/new/main/pkg/emitter