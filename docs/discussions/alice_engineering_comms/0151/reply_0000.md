## 2023-01-18 @pdxjohnny Engineering Logs

- 2nd party draft
  - Registry build webhook event triggers generating an SBOM (payload / OA / Input to start in description) which says there is a new version.
  - NVDStyle v2 API serves SBOM
  - Tight poll to start, webpubsub or DWN or ActivityPub later
  - Build results issued by downstream as VEX with description as Input where value is SARIF
    - Upstreams might "follow back" by polling downstream NVDStyles
  - Metric collection as container layer via `--build-arg` for URL, then golang style multi stage build where results are put in `FROM scratch`
    - We can use manifest style documentation to describe what filepaths are relevant (maybe within schema defaults)
    - Later https://github.com/opencontainers/distribution-spec/blob/main/spec.md
    - https://github.com/aquasecurity/trivy
      - Did CVE Bin Tool get integrated here? Can it produce VEX?

**schema/image/container/build/dffml.json**

```json
{
    "$schema": "https://github.com/intel/dffml/raw/main/schema/image/container/build/0.0.1.schema.json",
    "include": [
        {
            "branch": "main",
            "commit": "ddb32a4e65b0d79c7561ce2bdde16d963c8abde1",
            "dockerfile": "Dockerfile",
            "image_name": "dffml",
            "owner": "intel",
            "repository": "dffml"
        }
    ]
}
```

```console
$ python -c 'import pathlib, json, sys; print(json.dumps({"manifest": json.dumps(json.loads(sys.stdin.read().strip())["include"])}))' < schema/image/container/build/dffml.json | gh -R intel/dffml workflow run dispatch_build_images_containers.yml --ref main --json
```

- DFFML (upstream) files of interest

```
entities/alice/alice/please/contribute/recommended_community_standards/cli.py
entities/alice/alice/please/contribute/recommended_community_standards/code_of_conduct.py
entities/alice/alice/please/contribute/recommended_community_standards/contributing.py
entities/alice/alice/please/contribute/recommended_community_standards/meta_issue.py
entities/alice/alice/please/contribute/recommended_community_standards/readme.py
entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
entities/alice/alice/please/contribute/util/gh.py
entities/alice/alice/please/log/todos/output_urls.py
entities/alice/alice/please/log/todos/todos.py
entities/alice/alice/shouldi/contribute/cicd.py
```

- Creating an overlay to record issue URLs

```console
$ grep IssueURL entities/alice/alice/please/log/todos/todos.py
    SupportIssueURL = NewType("SupportIssueURL", str)
            "issue_url": SupportIssueURL,
    ) -> SupportIssueURL:
    CodeOfConductIssueURL = NewType("CodeOfConductIssueURL", str)
            "issue_url": CodeOfConductIssueURL,
    ) -> CodeOfConductIssueURL:
    ContributingIssueURL = NewType("ContributingIssueURL", str)
            "issue_url": ContributingIssueURL,
    ) -> ContributingIssueURL:
    SecurityIssueURL = NewType("SecurityIssueURL", str)
            "issue_url": SecurityIssueURL,
    ) -> SecurityIssueURL:
    ReadmeIssueURL = NewType("ReadmeIssueURL", str)
            "issue_url": ReadmeIssueURL,
    ) -> ReadmeIssueURL:
```

- Write and operation and enable the overlay

```patch
diff --git a/entities/alice/alice/please/log/todos/output_urls.py b/entities/alice/alice/please/log/todos/output_urls.py
new file mode 100644
index 000000000..d41d76a96
--- /dev/null
+++ b/entities/alice/alice/please/log/todos/output_urls.py
@@ -0,0 +1,26 @@
+import dffml
+from typing import NewType
+
+from .todos import AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues
+
+
+CreatedIssuesURLs = NewType("CreatedIssuesURLs", dict)
+
+
+@dffml.op(
+    stage=dffml.Stage.OUTPUT,
+)
+def grab_created_urls(
+    support: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.SupportIssueURL,
+    code_of_conduct: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.CodeOfConductIssueURL,
+    contributing: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.ContributingIssueURL,
+    security: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.SecurityIssueURL,
+    readme: AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues.ReadmeIssueURL,
+) -> CreatedIssuesURLs:
+    return {
+        "support": support,
+        "code_of_conduct": code_of_conduct,
+        "contributing": contributing,
+        "security": security,
+        "readme": readme,
+    }
diff --git a/entities/alice/entry_points.txt b/entities/alice/entry_points.txt
index 6719e138f..f31c670d3 100644
--- a/entities/alice/entry_points.txt
+++ b/entities/alice/entry_points.txt
@@ -38,3 +38,4 @@ OverlayEnsureActionsValidator                  = alice_test.shouldi.contribute.a
 OverlayCLI                                     = alice.please.log.todos.todos:OverlayCLI
 OverlayRecommendedCommunityStandards           = alice.please.log.todos.todos:AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues
 GitHubRepoID                                   = dffml_operations_innersource.cli:github_repo_id_to_clone_url
+OverlayOutputCreatedIssues                     = alice.please.log.todos.output_urls:grab_created_urls
```

- **TODO** Untangle copy pasta of subflow execution, it assumes no outputs, maybe use the output collection code from system context
- **TODO** Align `-repos` to `-keys` for exec of `alice please` commands
- https://github.com/dariusk/express-activitypub#api
  - https://www.w3.org/TR/activitypub/
  - https://github.com/immers-space/activitypub-express#next-steps-and-examples
    - > Server-to-server apps: For an app that people interact with by sending messages from another app (e.g. Mastodon), you'll want to define custom side-effects using app.on('apex-inbox', ({ actor, activity, recipient, object }) => {...}), which is fired for each incoming message.

```bash
git clone https://github.com/dariusk/express-activitypub
cd express-activitypub
npm install
dffml service http createtls server -log debug
cat > config.json <<'EOF'
{
  "USER": "alice",
  "PASS": "maryisgod",
  "DOMAIN": "localhost",
  "PORT": "3000",
  "PRIVKEY_PATH": "server.crt",
  "CERT_PATH": "server.pem"
}
EOF
node index.js
```

- Create account [:pill:](https://pdxjohnny.github.io/redpill/)

```console
$ curl --noproxy 127.0.0.1 -w '\n' -u alice:maryisgod -d "account=alice" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://127.0.0.1:3000/api/admin/create
```

- Successful account create response

```json
{"msg":"ok","apikey":"3feda0b9f6a26b0eb93135c6455833d8"}
```

- Check if account exists

```console
$ curl -w '\n' -v --noproxy 127.0.0.1 'http://127.0.0.1:3000/.well-known/webfinger?resource=acct:alice@localhost'
```

- Account exists response

```json
{"subject":"acct:alice@localhost","links":[{"rel":"self","type":"application/activity+json","href":"https://localhost/u/alice"}]}
```

```console
$ curl -w '\n' --noproxy 127.0.0.1 -d 'acct=alice' -d "apikey=8b6619996b83f016ccb71db7c5f7a583" -d 'message=HelloWorld' 'http://127.0.0.1:3000/api/sendMessage'
{"msg":"No followers for account alice@localhost"}
```

- https://github.com/immers-space/activitypub-express#usage
  - https://github.com/firebase/firebase-tools/issues/4595#issuecomment-1142325657
    - Need to upgrade nodejs to > 16

- TODO
  - [ ] Post manifest -> GitHub Actions workflow dispatch
    - This will be our base for alignment on communications for downstream validation, we will later move to DIDs and VCs
  - [ ] Webhook (container image registries) to ActivityPub proxy