## 2023-03-27 @pdxjohnny Engineering Logs

- Pinning git repo update

```console
$ export NEW_HASH="$(git log -n 1 --pretty=format:%H)"; sed -i -r -e "s#\"[A-Fa-f0-9]{40}\"#\"${NEW_HASH}\"#g"
$ export TARGET_OWNER=srossross \
  && export TARGET_REPO=rpmfile \
  && export TARGET_TAG=1.1.1 \
  && export TARGET_COMMIT=$(git ls-remote --tags https://github.com/${TARGET_OWNER}/${TARGET_REPO} "refs/tags/${TARGET_TAG}" | awk '{print $1}') \
  && export TARGET_VENDOR_OWNER=intel \
  && export TARGET_VENDOR_REPO=dffml \
  && export TARGET_VENDOR_BRANCH="vendored.com.github.${TARGET_OWNER}.${TARGET_REPO}.${TARGET_COMMIT}" \
  && set -x \
  && sed -i -e "s/${TARGET_OWNER}\/${TARGET_REPO}@${TARGET_TAG}/${TARGET_VENDOR_OWNER}\/${TARGET_VENDOR_REPO}@${TARGET_VENDOR_BRANCH}/g" $(git grep "${TARGET_OWNER}/${TARGET_REPO}@${TARGET_TAG}" | awk '{print $1}' | sed -e 's/://g' | sort | uniq) \
  && git commit -sam "Vendor ${TARGET_OWNER}/${TARGET_REPO}" \
  && export TARGET_DIR=$(mktemp -d ) \
  && export TARGET_REPO_URL=https://github.com/${TARGET_OWNER}/${TARGET_REPO} \
  && export VENDOR_REPO_URL=https://github.com/${TARGET_VENDOR_OWNER}/${TARGET_VENDOR_REPO} \
  && export TARGET_COMMIT=$TARGET_COMMIT\
  && mkdir -p "${TARGET_DIR}" \
  && cd "${TARGET_DIR}" \
  && git init \
  && git remote add origin "${TARGET_REPO_URL}" \
  && git fetch origin "${TARGET_COMMIT}" --depth 1 \
  && git reset --hard "${TARGET_COMMIT}" \
  && git remote set-url origin "${VENDOR_REPO_URL}" \
  && git push origin "HEAD:${TARGET_VENDOR_BRANCH}" \
  && cd - \
  && set +x
```

- https://github.com/guacsec/guac/issues/594
  - > In the CycloneDX PR (https://github.com/CycloneDX/cyclonedx-maven-plugin/pull/306), the proposal is to add a [hash to the reference which acts as a merkle tree of PURLs](https://github.com/CycloneDX/cyclonedx-maven-plugin/blob/1ebfae540c43aa0341e034cba12c575de9c72e80/src/main/java/org/cyclonedx/maven/DefaultProjectDependenciesConverter.java#L263-L298) which a pkg depends on.
    >
    > In GUAC, we can take a similar approach where we can perform a hash on descendants of a package when parsing the SBOMs. And express them in our pkg data model as a qualifier (which are used to express specific instances of a library). This can be done via taking the serialization of GUAC pkg predicates for descendants and use that hash as a qualifier via a merkle tree hash by pkg serialization lexical order.
    >
    > The ideal situation is that the Java ecosystem would encode a way to differentiate between such instances or provide the identifiers to do this analysis. Possibly as a qualifier on a PURL.
  - Looks like the GUAC folks are tackling the dependency DAG problem over here
- https://github.com/CycloneDX/specification/issues/192#issuecomment-1485405123
  - https://github.com/in-toto/attestation/issues/165
- https://github.com/CycloneDX/specification/issues/201
- https://github.com/ipvm-wg/spec/pull/8
  - > IPVM provides a deterministic-by-default, content addressed execution environment. Computation MAY be run locally or remotely. While local operation has zero latency, there are many cases where remote exection is desirable: access to large data, faster processors, trusted execution environments, or access to specialized hardware, among others.
    - ❤️ This helps us with our hermetic / arbitrary granularity cache-able builds
- https://huggingface.co/EleutherAI/gpt-j-6B
- https://github.com/BlinkDL/ChatRWKV/blob/main/v2/chat.py
- https://github.com/sahil280114/codealpaca
- https://github.com/neonbjb/tortoise-tts
  - Text to speech for the response half of of Writing the Wave
  - > The original colab no longer works by a combination of Google's tendency to forward-break things and Python's package management system. I do not intend to keep fixing it so it has been removed. Apologies!
    - Yeah... bane of my existence... hence the pinning stuff and the eventing for it and the CI/CD and the AI...
- https://github.com/Picsart-AI-Research/Text2Video-Zero
- https://github.com/RDFLib/rdflib
- https://forgefed.org/spec/#repository-forking
- https://codeberg.org/ForgeFed/ForgeFed/src/branch/main/doc/EXAMPLE_WORKFLOWS.md
- https://codeberg.org/ForgeFed/ForgeFed/src/branch/main/doc/
  - > Distributed version control systems (VCS) were created to allow maximal flexibility of project management structures and code hosting, in contrast to the client-server version control systems that were most widely used at the time, which denote one replica as the canonical master source. Existing project management / code hosting websites (aka: forges) soon began supporting these, and some new ones sprung up as well; but even the new ones were modeled upon the centralized "hub" paradigm (star topology, in networking lingo), with a single canonical "upstream" parent replica, and all other replicas implicitly and permanently designated as "downstream" child replicas (aka: forks). This type of website well serves the traditional purpose of facilitating release distribution, collaboration, and end-user participation; but at the expense of re-centralizing the naturally distributed VCS.
    >
    > The goal of the ForgeFed project is to support the familiar collaborative features of centralized web forges with a decentralized, federated design that, by fully embracing the mostly forgotten merits distributed VCS, does not rely on a single authoritative central host, does not impose a hierarchical master/fork collaboration structure, and can be self-hosted by anyone; with all such independent peers cooperating to form a larger logical network of inter-operable and correlated services.
- https://github.com/renovatebot/renovate
- https://docs.renovatebot.com/modules/platform/gitea/
  - Let's hook this up to our commit stream and have it bump active PRs against the ones in their virtual branch set based off federated CI results
  - Our policy engine with ability to provide per-pull-request depedency-links style alternate deps will help use decide if we should create pull requests on active pull request to update relevant manifests when we have a multi-branch CR0/4 style setup across a poly repo federated set
- https://git.mastodont.cat/spla/gitcat
  - For running mastodon for truly federated non-single users servers such as activitypubstarterkit
- https://forgejo.dev/forgejo.dev/infrastructure-as-code/
- https://codeberg.org/forgejo/-/packages/container/forgejo/1.19.0-2-rootless
- https://code.forgejo.org/earl-warren/setup-forgejo-release/commit/89b6ae4da602c35e4d98b986fe98251e826e59c4
  - We need to enable some kind of per-branch upload-artifact style releases so that pull requests can grab built packages from other pull requests in their active poly repo virtual branch setup
- https://forgejo.org/docs/latest/admin/database-preparation/
  - https://github.com/intel/dffml/blob/d6631495b3d6c567de0841580ee63b625c571b4d/source/mysql/dffml_source_mysql/util/mysql_docker.py
  - https://github.com/go-gitea/gitea/issues/10828
    - We'll hold off on TLS until this issue is closed
- https://docs.gitea.io/en-us/install-with-docker/
- https://forgejo.org/docs/latest/user/
- https://forgejo.org/docs/latest/admin/config-cheat-sheet/
- https://f3.forgefriends.org/schemas/index.html#release-asset
  - This might be all we need
- https://f3.forgefriends.org/schemas/index.html#review-comment
- https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/pullrequest.json
- https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/pullrequestbranch.json
  - We should see about referencing pull request objects or branch objects as vuln proof of concepts

```console
$ cd examples/tutorials/rolling_alice/federated_forge/alice_and_bob
$ docker-compose up
```

- Create initial config

```yaml
app_name: 'Forgejo: Beyond coding. We forge.'
app_url: http://127.0.0.1:2000/
charset: utf8
db_host: localhost:3306
db_name: gitea
db_path: /var/lib/gitea/data/gitea.db
db_type: sqlite3
db_user: root
default_allow_create_organization: 'on'
default_enable_timetracking: 'on'
domain: 127.0.0.1
enable_federated_avatar: 'on'
enable_open_id_sign_in: 'on'
enable_open_id_sign_up: 'on'
http_port: '3000'
lfs_root_path: /var/lib/gitea/git/lfs
log_root_path: /var/lib/gitea/data/log
no_reply_address: noreply.localhost
password_algorithm: pbkdf2_hi
repo_root_path: /var/lib/gitea/git/repositories
run_user: git
ssh_port: '2022'
ssl_mode: disable
```

- https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
- Convert to URL params

```console
$ echo "${ALICE_DATA_RAW_INIT_FORGE}"
db_type=sqlite3&db_host=localhost%3A3306&db_user=root&db_passwd=&db_name=gitea&ssl_mode=disable&db_schema=&charset=utf8&db_path=%2Fvar%2Flib%2Fgitea%2Fdata%2Fgitea.db&app_name=Forgejo%3A+Beyond+coding.+We+forge.&repo_root_path=%2Fvar%2Flib%2Fgitea%2Fgit%2Frepositories&lfs_root_path=%2Fvar%2Flib%2Fgitea%2Fgit%2Flfs&run_user=git&domain=127.0.0.1&ssh_port=2022&http_port=3000&app_url=http%3A%2F%2F127.0.0.1%3A2000%2F&log_root_path=%2Fvar%2Flib%2Fgitea%2Fdata%2Flog&smtp_addr=&smtp_port=&smtp_from=&smtp_user=&smtp_passwd=&enable_federated_avatar=on&enable_open_id_sign_in=on&enable_open_id_sign_up=on&default_allow_create_organization=on&default_enable_timetracking=on&no_reply_address=noreply.localhost&password_algorithm=pbkdf2_hi&admin_name=&admin_passwd=&admin_confirm_passwd=&admin_email=
$ curl 'http://127.0.0.1:2000/' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: lang=en-US; _csrf=VjZKcTdlMK7zjeMnbayeSuOzQi46MTY3OTk3MzYxOTc2NTgzNTY3NA; i_like_gitea=d5249768265f875d' \
  -H 'Origin: null' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Sec-GPC: 1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  --data-raw "${ALICE_DATA_RAW_INIT_FORGE}" \
  --compressed
$ python -c 'import sys, urllib.parse, yaml; print(yaml.dump({key: value for key, value in urllib.parse.parse_qsl(sys.argv[-1])}))' "${ALICE_DATA_RAW_INIT_FORGE}"
$ curl 'http://127.0.0.1:2000/user/sign_up' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: lang=en-US; _csrf=VjZKcTdlMK7zjeMnbayeSuOzQi46MTY3OTk3MzYxOTc2NTgzNTY3NA; i_like_gitea=d5249768265f875d' \
  -H 'Origin: null' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Sec-GPC: 1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  --data-raw '_csrf=$XXS_CSRF_TOKEN&user_name=alice&email=alice%40chadig.com&password=maryisgod&retype=maryisgod' \
  --compressed
```

- https://gist.github.com/pdxjohnny/f6fe1a39bd4e66e7d0c6e7802872d3b5#file-download-py-L63-L78
  - Maybe we can just disable CSRF to avoid having to double request every time
    - Update: It doesn't look like there is a way to do this across multiple handlers without recompiling

[![use-the-source](https://img.shields.io/badge/use%20the-source-blueviolet)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#use-the-source-)

```console
$ git grep -i disablecsrf
modules/context/auth.go:        DisableCSRF     bool
modules/context/auth.go:                if !options.SignOutRequired && !options.DisableCSRF && ctx.Req.Method == "POST" {
routers/web/web.go:     ignSignInAndCsrf := context.Toggle(&context.ToggleOptions{DisableCSRF: true})
```

- We need to enable federation to see messages fly between `/inbox` endpoints
  - https://github.com/go-gitea/gitea/blob/8df1b4bd699897264c60da7ce982b09cee57f345/custom/conf/app.example.ini#L2442-L2469
- Maybe we can do it all within an integration test?

```console
$ git log -n 1
commit 95e4f16899cb85b68657fcc66da11cf4c38d1d7e (HEAD -> forgejo, origin/forgejo, origin/HEAD)
Merge: 5100a777a 70afc6a29
Author: Loïc Dachary <loic@dachary.org>
Date:   Sun Mar 26 21:02:12 2023 +0200

    Merge remote-tracking branch 'forgejo/forgejo-development' into forgejo
$ git grep -i federation
CHANGELOG.md:  * User keypairs and HTTP signatures for ActivityPub federation using go-ap (#19133)
CHANGELOG.md:* FEDERATION
CHANGELOG.md:  * Create pub/priv keypair for federation (#17071)
CHANGELOG.md:  * Add nodeinfo endpoint for federation purposes (#16953)
CONTRIBUTING/WORKFLOW.md:### [Federation](https://codeberg.org/forgejo/forgejo/issues?labels=79349)
CONTRIBUTING/WORKFLOW.md:* [forgejo-federation](https://codeberg.org/forgejo/forgejo/src/branch/forgejo-federation) based on [forgejo-development](https://codeberg.org/forgejo/forgejo/src/branch/forgejo-development)
CONTRIBUTING/WORKFLOW.md:  Federation support for Forgejo
README.md:- Federation: (WIP) We are actively working to connect software forges with each other through **ActivityPub**,
RELEASE-NOTES.md:  * User keypairs and HTTP signatures for ActivityPub federation using go-ap (https://github.com/go-gitea/gitea/pull/19133)
custom/conf/app.example.ini:;[federation]
custom/conf/app.example.ini:;; Enable/Disable federation capabilities
custom/conf/app.example.ini:;; Enable/Disable user statistics for nodeinfo if federation is enabled
custom/conf/app.example.ini:;; Maximum federation request and response size (MB)
custom/conf/app.example.ini:;; WARNING: Changing the settings below can break federation.
custom/conf/app.example.ini:;; GET headers for federation requests
custom/conf/app.example.ini:;; POST headers for federation requests
docs/content/doc/administration/config-cheat-sheet.en-us.md:## Federation (`federation`)
docs/content/doc/administration/config-cheat-sheet.en-us.md:- `ENABLED`: **false**: Enable/Disable federation capabilities
docs/content/doc/administration/config-cheat-sheet.en-us.md:- `SHARE_USER_STATISTICS`: **true**: Enable/Disable user statistics for nodeinfo if federation is enabled
docs/content/doc/administration/config-cheat-sheet.en-us.md:- `MAX_SIZE`: **4**: Maximum federation request and response size (MB)
docs/content/doc/administration/config-cheat-sheet.en-us.md: WARNING: Changing the settings below can break federation.
docs/content/doc/administration/config-cheat-sheet.en-us.md:- `GET_HEADERS`: **(request-target), Date**: GET headers for federation requests
docs/content/doc/administration/config-cheat-sheet.en-us.md:- `POST_HEADERS`: **(request-target), Date, Digest**: POST headers for federation requests
modules/activitypub/client.go:  if err = containsRequiredHTTPHeaders(http.MethodGet, setting.Federation.GetHeaders); err != nil {
modules/activitypub/client.go:  } else if err = containsRequiredHTTPHeaders(http.MethodPost, setting.Federation.PostHeaders); err != nil {
modules/activitypub/client.go:          digestAlg:   httpsig.DigestAlgorithm(setting.Federation.DigestAlgorithm),
modules/activitypub/client.go:          getHeaders:  setting.Federation.GetHeaders,
modules/activitypub/client.go:          postHeaders: setting.Federation.PostHeaders,
modules/activitypub/client_test.go:             assert.Regexp(t, regexp.MustCompile("^"+setting.Federation.DigestAlgorithm), r.Header.Get("Digest"))
modules/setting/federation.go:// Federation settings
modules/setting/federation.go:  Federation = struct {
modules/setting/federation.go:func loadFederationFrom(rootCfg ConfigProvider) {
modules/setting/federation.go:  if err := rootCfg.Section("federation").MapTo(&Federation); err != nil {
modules/setting/federation.go:          log.Fatal("Failed to map Federation settings: %v", err)
modules/setting/federation.go:  } else if !httpsig.IsSupportedDigestAlgorithm(Federation.DigestAlgorithm) {
modules/setting/federation.go:          log.Fatal("unsupported digest algorithm: %s", Federation.DigestAlgorithm)
modules/setting/federation.go:  Federation.MaxSize = 1 << 20 * Federation.MaxSize
modules/setting/federation.go:  HttpsigAlgs = make([]httpsig.Algorithm, len(Federation.Algorithms))
modules/setting/federation.go:  for i, alg := range Federation.Algorithms {
modules/setting/setting.go:     loadFederationFrom(CfgProvider)
routers/api/v1/activitypub/reqsignature.go:     b, err = io.ReadAll(io.LimitReader(resp.Body, setting.Federation.MaxSize))
routers/api/v1/activitypub/reqsignature.go:     algo := httpsig.Algorithm(setting.Federation.Algorithms[0])
routers/api/v1/api.go:          if setting.Federation.Enabled {
routers/api/v1/misc/nodeinfo.go:// NodeInfo returns the NodeInfo for the Gitea instance to allow for federation
routers/api/v1/misc/nodeinfo.go:        if setting.Federation.ShareUserStatistics {
routers/web/web.go:     federationEnabled := func(ctx *context.Context) {
routers/web/web.go:             if !setting.Federation.Enabled {
routers/web/web.go:             }, federationEnabled)
tests/integration/api_activitypub_person_test.go:       setting.Federation.Enabled = true
tests/integration/api_activitypub_person_test.go:               setting.Federation.Enabled = false
tests/integration/api_activitypub_person_test.go:       setting.Federation.Enabled = true
tests/integration/api_activitypub_person_test.go:               setting.Federation.Enabled = false
tests/integration/api_activitypub_person_test.go:       setting.Federation.Enabled = true
tests/integration/api_activitypub_person_test.go:               setting.Federation.Enabled = false
tests/integration/api_nodeinfo_test.go: setting.Federation.Enabled = true
tests/integration/api_nodeinfo_test.go:         setting.Federation.Enabled = false
tests/integration/webfinger_test.go:    setting.Federation.Enabled = true
tests/integration/webfinger_test.go:            setting.Federation.Enabled = false
web_src/fomantic/build/semantic.css:i.icon.trade.federation:before {
$ git grep -C 5 -i federation -- routers/web/web.go
routers/web/web.go-                     ctx.Error(http.StatusNotFound)
routers/web/web.go-                     return
routers/web/web.go-             }
routers/web/web.go-     }
routers/web/web.go-
routers/web/web.go:     federationEnabled := func(ctx *context.Context) {
routers/web/web.go:             if !setting.Federation.Enabled {
routers/web/web.go-                     ctx.Error(http.StatusNotFound)
routers/web/web.go-                     return
routers/web/web.go-             }
routers/web/web.go-     }
routers/web/web.go-
--
routers/web/web.go-     m.Group("/.well-known", func() {
routers/web/web.go-             m.Get("/openid-configuration", auth.OIDCWellKnown)
routers/web/web.go-             m.Group("", func() {
routers/web/web.go-                     m.Get("/nodeinfo", NodeInfoLinks)
routers/web/web.go-                     m.Get("/webfinger", WebfingerQuery)
routers/web/web.go:             }, federationEnabled)
routers/web/web.go-             m.Get("/change-password", func(w http.ResponseWriter, req *http.Request) {
routers/web/web.go-                     http.Redirect(w, req, "/user/settings/account", http.StatusTemporaryRedirect)
routers/web/web.go-             })
routers/web/web.go-     })
routers/web/web.go-
```

- https://unifiedpush.org/
  - Notifications for end users Over The Air updates
  - Starting backwards. How do we go from F-Droid OTA of dev mode Android App or Purism store OTA of dev-mode aarch gnome app. Built from multi-branch active pull request across federated set of repos (Alice's forge and Bob's forge).
  - Starting form an edge KCP/kubernetes cluster running Forgejo needing to know when to do a rolling update behind a load balencer.
- We'll be leveraging the triage mechanism (the policy as code) to decide what pull requests upstream of the pull request for the active system context should result in an auto pull request to that active system context along with criteria for auto merge of the pull request to update pinning tracking that upstream into the active pull request. This is the automated promotion criteria which facilitates the cascading changes across a set of pull requests. We can set which CI jobs and which CD assets from those jobs get re-pinned as they cascade their way upstream.
  - https://github.com/intel/cve-bin-tool/issues/2639
  - https://github.com/peter-evans/create-pull-request
- We use our beyond the unit of the line granularity (Living Threat Model analysis) to understand the threat model and top level system context (repo fork secrets) trust zones associated with a given current system context pull request
  - https://github.com/CycloneDX/specification/pull/194
- We capture the webhook events across GitHub repos in different orgs (intel/dffml, dffml/dffml-model-transformers)
  - We relay into the ActivityPub federated event space
  - We do data transforms into the event types of interest
    - https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/pullrequest.json
    - https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/pullrequestbranch.json
    - https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/review.json
    - https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/comment.json
    - https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/asset.json
    - https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/releaseasset.json
  - We create ad-hoc releases and release asset JSON blobs to describe CD assets from pull requests upstream of the current system context (dependencies, pull requests which our pull request requires the following example data types from: assets, packages, shouldi results)
  - We decide based on the policy as code if we want to federate a new pullrequest object against the active system context to bump pinned versions of tracked CD assets from other pull requests which we depend on within the poly repo set.
    - We use the https://github.com/peter-evans/create-pull-request flow to create a new pull request to the pull request
  - We decide based on policy as code if we want to auto merge the new pull request into the current / active system context pull request.
    - We use CI jobs within the current system context pull request to decide if we should to auto merge the new pull request into it
      - We can use wait-for-message to facilitate more complex poly repo flows for use cases like tutorial validation were the pinning triggers integration across as set of support level 1, 2, N plugins.
- https://codeberg.org/forgejo/discussions/issues/12#issuecomment-854895
  - > Looking closer at the specs I think https://lab.forgefriends.org/friendlyforgeformat/f3-schemas/-/blob/main/releaseasset.json is the vocab for CD event federation. It looks like the stages of CI runs (and other CI events) is still an open. Probably also the intermediate artifact uploads (which fall more under CD depending on use case).