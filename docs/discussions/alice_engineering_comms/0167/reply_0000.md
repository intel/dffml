## 2023-02-03 @pdxjohnny Engineering Logs

- https://github.com/GoogleContainerTools/kaniko/issues/1836#issuecomment-1416451403
- https://cdk8s.io/docs/latest/getting-started/#abstraction-through-constructs
  - https://github.com/cdk8s-team/cdk8s/tree/master/examples/python/crd
    - https://github.com/cdk8s-team/cdk8s/blob/master/examples/python/crd/cdk8s.yaml
  - https://github.com/cdk8s-team/cdk8s/tree/master/examples/python/web-service
  - https://github.com/cdk8s-team/cdk8s/tree/master/examples/python/hello
  - https://cdk8s.io/docs/latest/examples/
- https://til.simonwillison.net/webassembly/python-in-a-wasm-sandbox
- https://github.com/slsa-framework/slsa-github-generator/tree/main/internal/builders/container
- `alice please show me how to ...`
  - Creates diff, `alice please contrbiute ...` creates pull requests (or ActivityPub analogies)
- https://github.blog/2023-02-02-enabling-branch-deployments-through-issueops-with-github-actions/
  - Chaos smiles on us again
    - #1061
    - This is how we enable prospective 2nd party plugin maintainers to check for increase in support level (from 3rd to 2nd party)
      - This also allows them to have Alice create automated pull requests which resolve issues for them to increase their support level
      - #1239
  - Example reproduced below

```yaml
name: "branch deploy demo"

# The workflow will execute on new comments on pull requests - example: ".deploy" as a comment
on:
  issue_comment:
    types: [created]

jobs:
  demo:
    if: ${{ github.event.issue.pull_request }} # only run on pull request comments (no need to run on issue comments)
    runs-on: ubuntu-latest
    steps:
      # Execute IssueOps branch deployment logic, hooray!
      # This will be used to "gate" all future steps below and conditionally trigger steps/deployments
      - uses: github/branch-deploy@vX.X.X # replace X.X.X with the version you want to use
        id: branch-deploy # it is critical you have an id here so you can reference the outputs of this step
        with:
          trigger: ".deploy" # the trigger phrase to look for in the comment on the pull request

      # Run your deployment logic for your project here - examples seen below

      # Checkout your project repository based on the ref provided by the branch-deploy step
      - uses: actions/checkout@3.0.2
        if: ${{ steps.branch-deploy.outputs.continue == 'true' }} # skips if the trigger phrase is not found
        with:
          ref: ${{ steps.branch-deploy.outputs.ref }} # uses the detected branch from the branch-deploy step

      # Do some fake "noop" deployment logic here
      # conditionally run a noop deployment
      - name: fake noop deploy
        if: ${{ steps.branch-deploy.outputs.continue == 'true' && steps.branch-deploy.outputs.noop == 'true' }} # only run if the trigger phrase is found and the branch-deploy step detected a noop deployment
        run: echo "I am doing a fake noop deploy"

      # Do some fake "regular" deployment logic here
      # conditionally run a regular deployment
      - name: fake regular deploy
        if: ${{ steps.branch-deploy.outputs.continue == 'true' && steps.branch-deploy.outputs.noop != 'true' }} # only run if the trigger phrase is found and the branch-deploy step detected a regular deployment
        run: echo "I am doing a fake regular deploy"
```

![chaos_for_the_chaos_God](https://user-images.githubusercontent.com/5950433/216681621-b55b5c88-5fa3-4bde-802a-e7d569517eb7.jpg)

- https://edu.chainguard.dev/open-source/sbom/what-is-openvex/
- https://github.com/namshi/docker-smtp
  - This is an SMTP server and SMTP relay server 🛤️
- `ActivityPubStarterAdminInputNetwork`
  - Websocket endpoint to receive new events
  - POST `/admin/create`
  - `Input.id` as activitypub URL, later backup to DID land
- https://about.sourcegraph.com/blog/building-conc-better-structured-concurrency-for-go
- https://www2023.thewebconf.org/calls/webdeveloper-w3c/
- https://github.com/jart/blink
- Fast transform helper `@op` derivative decorators (we'd looked at this recently)
  - Helps with remapping datatypes, could be used in input type declaration
  - https://intel.github.io/dffml/main/api/operation/mapping.html?highlight=mapping_extract_value#dffml.operation.mapping.mapping_extract_value
    - Alternative sketch: `@op.apply(mapping_extract_value, ... something else? ...)`

```python
def takes_repo_dir(
    repo_directory: op_mapping_extract_value(AliceGitRepo.directory),
    *,
    logger: logging.Logger,
    env: dict,
) -> :
    if logger:
        logger.debug(f"{repo_directory} logged! (already logged if orchestrator input called, ex: GitHub Action DEBUGing enabled)")
```

- https://github.com/OpenLineage/OpenLineage/issues/1412
  - Was just trying to figure out how to do this with webtorrent and activitypub this morning, oh! Chaos smiles again! :) :)
- https://github.com/OpenLineage/OpenLineage/releases/tag/0.19.2
  - Grouped by category
  - https://github.com/OpenLineage/OpenLineage/pull/1432/files#diff-c28f070ad0fa67a71f138b6c4b1302bfa0640bad2a44f1ca847b6170080d14fb
  - https://github.com/OpenLineage/OpenLineage/tree/main/integration
  - https://github.com/OpenLineage/OpenLineage/tree/main/integration/sql
    - https://github.com/intel/dffml/tree/main/source/mysql
  - Just use mermaid
    - Flat files, markdown docs
- Fixing webhook `vcs.push` to ActivityPub

```bash
npm run build
rm -i db/database.sqlite3 
head -n 10000 /dev/urandom | sha384sum | awk '{print $1}' | tee ../webhook
head -n 10000 /dev/urandom | sha384sum | awk '{print $1}' | tee ../password
openssl genrsa -out keypair.pem 4096 && openssl rsa -in keypair.pem -pubout -out publickey.crt && openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key
FDQN=vcs.activitypub.securitytxt.dffml.chadig.com WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=push ADMIN_USERNAME=admin ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start &
caddy reverse-proxy --from https://vcs.activitypub.securitytxt.dffml.chadig.com --to :8000
```

- Ensure webhook delivery for the following events
  - Related
    - https://github.com/intel/dffml/pull/1061#discussion_r1095079133
    - **TODO** Alice using GH cli to do this
    - https://github.com/intel/dffml/pull/1061#discussion_r819930461
    - https://github.com/intel/dffml/pull/1207#discussion_r1036680987
      - > Alice is you. What do you have access too?
  - Workflow jobs
    - Workflow job queued, waiting, in progress, or completed on a repository.
  - Workflow runs
    - Workflow run requested or completed on a repository.
  - Statuses
    - Commit status updated from the API.
  - Pushes
    - Git push to a repository.
  - Deployment statuses
    - Deployment status updated from the API.
  - Check suites
    - Check suite is requested, rerequested, or completed.
  - Check runs
    - Check run is created, requested, rerequested, or completed.
  - Branch or tag creation
    - Branch or tag created.
  - Commit comments
    - Commit or diff commented on.
  - Discussions
    - Discussion created, edited, pinned, unpinned, locked, unlocked, transferred, answered, unanswered, labeled, unlabeled, had its category changed, or was deleted.
  - Issues
    - Issue opened, edited, deleted, transferred, pinned, unpinned, closed, reopened, assigned, unassigned, labeled, unlabeled, milestoned, demilestoned, locked, or unlocked.
  - Issue comments
    - Issue comment created, edited, or deleted.
  - Packages
    - GitHub Packages published or updated in a repository.
  - Milestones
    - Milestone created, closed, opened, edited, or deleted.
  - Page builds
    - Pages site built.
  - Pull request review comments
    - Pull request diff comment created, edited, or deleted.
  - Pull request review threads
    - A pull request review thread was resolved or unresolved.
  - Pull request reviews
    - Pull request review submitted, edited, or dismissed.
  - Pull requests
    - Pull request assigned, auto merge disabled, auto merge enabled, closed, converted to draft, demilestoned, dequeued, edited, enqueued, labeled, locked, milestoned, opened, ready for review, reopened, review request removed, review requested, synchronized, unassigned, unlabeled, or unlocked.
  - Pushes
    - Git push to a repository.
  - Releases
    - Release created, edited, published, unpublished, or deleted.
- Retrigger webhook delivery

![image](https://user-images.githubusercontent.com/5950433/216702932-365a8ed4-a949-4113-8d86-8e03181b532e.png)

```console
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | jq | python -c 'import yaml, json, sys; print(yaml.dump(json.load(sys.stdin)))'
```

- This is an example of a check suite completion, yesterday we touched on how 2nd party PRs could have interdependency via jobs which watch for `ActivityPub` events such as the `check_suite` example we see here.
  - Was trying to figure out the webtorrent thing in case there were sets of events that we wanted to watch, and the torrent magnet link could but the content address of the set, but that will probably be solved by DID resolution of ActivityPub objects later.

```yaml
action: completed
check_suite:
  after: ddb32a4e65b0d79c7561ce2bdde16d963c8abde1
  app:
    created_at: 2018-07-30T09:30:17Z
    description: Automate your workflow from idea to production
    events:
      - branch_protection_rule
      - check_run
      - check_suite
      - create
      - delete
      - deployment
      - deployment_status
      - discussion
      - discussion_comment
      - fork
      - gollum
      - issues
      - issue_comment
      - label
      - merge_group
      - milestone
      - page_build
      - project
      - project_card
      - project_column
      - public
      - pull_request
      - pull_request_review
      - pull_request_review_comment
      - push
      - registry_package
      - release
      - repository
      - repository_dispatch
      - status
      - watch
      - workflow_dispatch
      - workflow_run
    external_url: https://help.github.com/en/actions
    html_url: https://github.com/apps/github-actions
    id: 15368
    name: GitHub Actions
    node_id: MDM6QXBwMTUzNjg=
    owner:
      avatar_url: https://avatars.githubusercontent.com/u/9919?v=4
      events_url: https://api.github.com/users/github/events{/privacy}
      followers_url: https://api.github.com/users/github/followers
      following_url: https://api.github.com/users/github/following{/other_user}
      gists_url: https://api.github.com/users/github/gists{/gist_id}
      gravatar_id: ""
      html_url: https://github.com/github
      id: 9919
      login: github
      node_id: MDEyOk9yZ2FuaXphdGlvbjk5MTk=
      organizations_url: https://api.github.com/users/github/orgs
      received_events_url: https://api.github.com/users/github/received_events
      repos_url: https://api.github.com/users/github/repos
      site_admin: false
      starred_url: https://api.github.com/users/github/starred{/owner}{/repo}
      subscriptions_url: https://api.github.com/users/github/subscriptions
      type: Organization
      url: https://api.github.com/users/github
    permissions:
      actions: write
      administration: read
      checks: write
      contents: write
      deployments: write
      discussions: write
      issues: write
      merge_queues: write
      metadata: read
      packages: write
      pages: write
      pull_requests: write
      repository_hooks: write
      repository_projects: write
      security_events: write
      statuses: write
      vulnerability_alerts: read
    slug: github-actions
    updated_at: 2019-12-10T19:04:12Z
  before: a6ec904d3b319de1fcb25bf6f724fd70dc057884
  check_runs_url: https://api.github.com/repos/intel/dffml/check-suites/10754865120/check-runs
  conclusion: success
  created_at: 2023-02-03T06:01:42Z
  head_branch: main
  head_commit:
    author:
      email: johnandersenpdx@gmail.com
      name: John Andersen
    committer:
      email: noreply@github.com
      name: GitHub
    id: ddb32a4e65b0d79c7561ce2bdde16d963c8abde1
    message: "ci: dispatch: build; images; container: Fixup manifest if bad line
      endings"
    timestamp: 2023-01-16T19:10:53Z
    tree_id: 2d5e1a8c29d57406ee4302482db455addc6bc224
  head_sha: ddb32a4e65b0d79c7561ce2bdde16d963c8abde1
  id: 10754865120
  latest_check_runs_count: 1
  node_id: CS_kwDOCOlgGM8AAAACgQo34A
  pull_requests: []
  rerequestable: true
  runs_rerequestable: false
  status: completed
  updated_at: 2023-02-03T06:01:59Z
  url: https://api.github.com/repos/intel/dffml/check-suites/10754865120
organization:
  avatar_url: https://avatars.githubusercontent.com/u/17888862?v=4
  description: ""
  events_url: https://api.github.com/orgs/intel/events
  hooks_url: https://api.github.com/orgs/intel/hooks
  id: 17888862
  issues_url: https://api.github.com/orgs/intel/issues
  login: intel
  members_url: https://api.github.com/orgs/intel/members{/member}
  node_id: MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy
  public_members_url: https://api.github.com/orgs/intel/public_members{/member}
  repos_url: https://api.github.com/orgs/intel/repos
  url: https://api.github.com/orgs/intel
repository:
  allow_forking: true
  archive_url: https://api.github.com/repos/intel/dffml/{archive_format}{/ref}
  archived: false
  assignees_url: https://api.github.com/repos/intel/dffml/assignees{/user}
  blobs_url: https://api.github.com/repos/intel/dffml/git/blobs{/sha}
  branches_url: https://api.github.com/repos/intel/dffml/branches{/branch}
  clone_url: https://github.com/intel/dffml.git
  collaborators_url: https://api.github.com/repos/intel/dffml/collaborators{/collaborator}
  comments_url: https://api.github.com/repos/intel/dffml/comments{/number}
  commits_url: https://api.github.com/repos/intel/dffml/commits{/sha}
  compare_url: https://api.github.com/repos/intel/dffml/compare/{base}...{head}
  contents_url: https://api.github.com/repos/intel/dffml/contents/{+path}
  contributors_url: https://api.github.com/repos/intel/dffml/contributors
  created_at: 2018-09-19T21:06:34Z
  default_branch: main
  deployments_url: https://api.github.com/repos/intel/dffml/deployments
  description: The easiest way to use Machine Learning. Mix and match underlying
    ML libraries and data set sources. Generate new datasets or modify existing
    ones with ease.
  disabled: false
  downloads_url: https://api.github.com/repos/intel/dffml/downloads
  events_url: https://api.github.com/repos/intel/dffml/events
  fork: false
  forks: 146
  forks_count: 146
  forks_url: https://api.github.com/repos/intel/dffml/forks
  full_name: intel/dffml
  git_commits_url: https://api.github.com/repos/intel/dffml/git/commits{/sha}
  git_refs_url: https://api.github.com/repos/intel/dffml/git/refs{/sha}
  git_tags_url: https://api.github.com/repos/intel/dffml/git/tags{/sha}
  git_url: git://github.com/intel/dffml.git
  has_discussions: true
  has_downloads: true
  has_issues: true
  has_pages: true
  has_projects: true
  has_wiki: true
  homepage: https://intel.github.io/dffml/main/
  hooks_url: https://api.github.com/repos/intel/dffml/hooks
  html_url: https://github.com/intel/dffml
  id: 149512216
  is_template: false
  issue_comment_url: https://api.github.com/repos/intel/dffml/issues/comments{/number}
  issue_events_url: https://api.github.com/repos/intel/dffml/issues/events{/number}
  issues_url: https://api.github.com/repos/intel/dffml/issues{/number}
  keys_url: https://api.github.com/repos/intel/dffml/keys{/key_id}
  labels_url: https://api.github.com/repos/intel/dffml/labels{/name}
  language: Python
  languages_url: https://api.github.com/repos/intel/dffml/languages
  license:
    key: mit
    name: MIT License
    node_id: MDc6TGljZW5zZTEz
    spdx_id: MIT
    url: https://api.github.com/licenses/mit
  merges_url: https://api.github.com/repos/intel/dffml/merges
  milestones_url: https://api.github.com/repos/intel/dffml/milestones{/number}
  mirror_url: null
  name: dffml
  node_id: MDEwOlJlcG9zaXRvcnkxNDk1MTIyMTY=
  notifications_url: https://api.github.com/repos/intel/dffml/notifications{?since,all,participating}
  open_issues: 387
  open_issues_count: 387
  owner:
    avatar_url: https://avatars.githubusercontent.com/u/17888862?v=4
    events_url: https://api.github.com/users/intel/events{/privacy}
    followers_url: https://api.github.com/users/intel/followers
    following_url: https://api.github.com/users/intel/following{/other_user}
    gists_url: https://api.github.com/users/intel/gists{/gist_id}
    gravatar_id: ""
    html_url: https://github.com/intel
    id: 17888862
    login: intel
    node_id: MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy
    organizations_url: https://api.github.com/users/intel/orgs
    received_events_url: https://api.github.com/users/intel/received_events
    repos_url: https://api.github.com/users/intel/repos
    site_admin: false
    starred_url: https://api.github.com/users/intel/starred{/owner}{/repo}
    subscriptions_url: https://api.github.com/users/intel/subscriptions
    type: Organization
    url: https://api.github.com/users/intel
  private: false
  pulls_url: https://api.github.com/repos/intel/dffml/pulls{/number}
  pushed_at: 2023-01-30T22:16:14Z
  releases_url: https://api.github.com/repos/intel/dffml/releases{/id}
  size: 602690
  ssh_url: git@github.com:intel/dffml.git
  stargazers_count: 201
  stargazers_url: https://api.github.com/repos/intel/dffml/stargazers
  statuses_url: https://api.github.com/repos/intel/dffml/statuses/{sha}
  subscribers_url: https://api.github.com/repos/intel/dffml/subscribers
  subscription_url: https://api.github.com/repos/intel/dffml/subscription
  svn_url: https://github.com/intel/dffml
  tags_url: https://api.github.com/repos/intel/dffml/tags
  teams_url: https://api.github.com/repos/intel/dffml/teams
  topics:
    - ai-inference
    - ai-machine-learning
    - ai-training
    - analytics
    - asyncio
    - dag
    - data-flow
    - dataflows
    - datasets
    - dffml
    - event-based
    - flow-based-programming
    - frameworks
    - hyperautomation
    - libraries
    - machine-learning
    - models
    - pipelines
    - python
    - swrepo
  trees_url: https://api.github.com/repos/intel/dffml/git/trees{/sha}
  updated_at: 2023-01-17T12:33:57Z
  url: https://api.github.com/repos/intel/dffml
  visibility: public
  watchers: 201
  watchers_count: 201
  web_commit_signoff_required: false
sender:
  avatar_url: https://avatars.githubusercontent.com/u/5950433?v=4
  events_url: https://api.github.com/users/pdxjohnny/events{/privacy}
  followers_url: https://api.github.com/users/pdxjohnny/followers
  following_url: https://api.github.com/users/pdxjohnny/following{/other_user}
  gists_url: https://api.github.com/users/pdxjohnny/gists{/gist_id}
  gravatar_id: ""
  html_url: https://github.com/pdxjohnny
  id: 5950433
  login: pdxjohnny
  node_id: MDQ6VXNlcjU5NTA0MzM=
  organizations_url: https://api.github.com/users/pdxjohnny/orgs
  received_events_url: https://api.github.com/users/pdxjohnny/received_events
  repos_url: https://api.github.com/users/pdxjohnny/repos
  site_admin: false
  starred_url: https://api.github.com/users/pdxjohnny/starred{/owner}{/repo}
  subscriptions_url: https://api.github.com/users/pdxjohnny/subscriptions
  type: User
  url: https://api.github.com/users/pdxjohnny
```

- Wow, 185 events already

```console
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | wc -l
173
$ date
Fri Feb  3 20:56:44 UTC 2023
```

- Now we want to translate to OpenVEX and have the content addresses of the signature for the post
  - https://github.com/package-url/purl-spec
  - https://github.com/openvex/spec/blob/main/OPENVEX-SPEC.md#example

```json
{
  "@context": "https://openvex.dev/ns",
  "@id": "https://vcs.activitypub.securitytxt.dffml.chadig.com/push/posts/vex-<sha of signature of inbox message which would be sent>",
  "author": "GitHub Actions <actions@github.com>",
  "role": "GitHub Actions",
  "timestamp": "2023-02-02T14:24:00.000000000-07:00",
  "version": "1",
  "statements": [
    {
      "vulnerability": "vex-<sha of signature of inbox message which would be sent>",
      "products": [
        "pkg:github/intel/dffml@ddb32a4e65b0d79c7561ce2bdde16d963c8abde1"
      ],
      "status": "not_affected",
      "justification": "vulnerable_code_not_in_execute_path"
      "impact_statement": "<webhook payload object>",
    }
  ]
}
```

- Quick post count check

```console
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | wc -l
406
$ date
Fri Feb  3 22:27:11 UTC 2023
```

- https://blog.adolus.com/a-deeper-dive-into-vex-documents
- Check the modified files webhook data
  - The following should be the same over an active websocket connection

```console
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | grep stream_of | grep modified | jq
```

```json
{
  "sender": {
    "login": "pdxjohnny",
    "id": 5950433,
    "node_id": "MDQ6VXNlcjU5NTA0MzM=",
    "avatar_url": "https://avatars.githubusercontent.com/u/5950433?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/pdxjohnny",
    "html_url": "https://github.com/pdxjohnny",
    "followers_url": "https://api.github.com/users/pdxjohnny/followers",
    "following_url": "https://api.github.com/users/pdxjohnny/following{/other_user}",    "gists_url": "https://api.github.com/users/pdxjohnny/gists{/gist_id}",    "starred_url": "https://api.github.com/users/pdxjohnny/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/pdxjohnny/subscriptions",
    "organizations_url": "https://api.github.com/users/pdxjohnny/orgs",
    "repos_url": "https://api.github.com/users/pdxjohnny/repos",
    "events_url": "https://api.github.com/users/pdxjohnny/events{/privacy}",    "received_events_url": "https://api.github.com/users/pdxjohnny/received_events",    "type": "User",
    "site_admin": false
  },
  "created": false,
  "deleted": false,
  "forced": false,
  "base_ref": null,
  "compare": "https://github.com/intel/dffml/compare/d77e2f697d80...a5e638884e56",
  "commits": [
    {
      "id": "a5e638884e565f727ae4fedf91a33b3ce68bcfa9",
      "tree_id": "9137977afec12d9f9bb3a76eac62158648f51d36",
      "distinct": true,
      "message": "docs: tutorials: rolling alice: architecting alice: stream of consciousness: Link to activitypubsecuritytxt\n\nAlice Engineering Comms: 2023-02-03 Engineering Logs: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4863663",
      "timestamp": "2023-02-03T12:53:47-08:00",
      "url": "https://github.com/intel/dffml/commit/a5e638884e565f727ae4fedf91a33b3ce68bcfa9",
      "author": {        "name": "John Andersen",        "email": "johnandersenpdx@gmail.com",
        "username": "pdxjohnny"      },      "committer": {        "name": "GitHub",
        "email": "noreply@github.com",
        "username": "web-flow"
      },
      "added": [],      "removed": [],
      "modified": [
        "docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md"
      ]
    }
  ],
  "head_commit": {
    "id": "a5e638884e565f727ae4fedf91a33b3ce68bcfa9",
    "tree_id": "9137977afec12d9f9bb3a76eac62158648f51d36",
    "distinct": true,
    "message": "docs: tutorials: rolling alice: architecting alice: stream of consciousness: Link to activitypubsecuritytxt\n\nAlice Engineering Comms: 2023-02-03 Engineering Logs: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4863663",
    "timestamp": "2023-02-03T12:53:47-08:00",    "url": "https://github.com/intel/dffml/commit/a5e638884e565f727ae4fedf91a33b3ce68bcfa9",    "author": {
      "name": "John Andersen",
      "email": "johnandersenpdx@gmail.com",
      "username": "pdxjohnny"
    },
    "committer": {
      "name": "GitHub",
      "email": "noreply@github.com",
      "username": "web-flow"
    },
    "added": [],
    "removed": [],
    "modified": [
      "docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md"
    ]
  }
}
```

```console
$ curl -sfL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox | jq --unbuffered -r '.orderedItems[].object.content' | grep stream_of | grep modified | jq -r --unbuffered '.commits[].modified[]'
docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
```

- https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html
- https://github.com/disclose/dnssecuritytxt/blob/c567bdb82fb6a231fd8b162c3d7e7b299aa6088b/README.md
  - https://github.dev/disclose/dnssecuritytxt/blob/c567bdb82fb6a231fd8b162c3d7e7b299aa6088b/README.md
- TODO
  - [ ] `FROM rebuild` trigger via simple `gh workflow dispatch` on `jq` filter files for relevant activitypub `push@vcs`, xargs to execute on every line (just no need to consume input, just every line which got through filter is rebuilt, websocat)
    - When a new image is pushed, instead of interacting with harbor webhooks, we just update a respective example to pin the version `FROM` to the new version (after signing as gone to transparency log)
  - [ ] Allowlist for event type properties
    - [ ] Data model synthesis from schema
    - [ ] Translation to OpenVEX before activitypubsecuritytxt style broadcast
      - https://github.com/openvex/spec/blob/main/OPENVEX-SPEC.md#example
        - Our payloads go in `impact_statement`
      - https://docs.oasis-open.org/csaf/csaf/v2.0/
        - https://docs.oasis-open.org/csaf/csaf/v2.0/os/schemas/aggregator_json_schema.json
        - https://docs.oasis-open.org/csaf/csaf/v2.0/os/schemas/provider_json_schema.json
        - https://docs.oasis-open.org/csaf/csaf/v2.0/os/schemas/csaf_json_schema.json
          - Payload in `document.acknowledgments[].urls[]`
  - [ ] Need self hostable localhost.run style rotation for downstreams
  - [ ] `dffml-model-transformers` as first example 2nd party
    - Rebuild upstream container when we get an VEX (via AcivityPub) from upstream saying that any of the files we want to watch have changed
      - At first we will just watch all files within the downstream container build workflow
        - `on.workflow_dispatch && on.push.paths: ["https://github.com/intel/dffml.git#branch=main/*"]`
      - Later we will watch for the example container with the pinned version
        - `on.workflow_dispatch && on.push.paths: ["https://github.com/intel/dffml.git#branch=main/dffml/util/skel/common/Dockerfile"]`
        - `dffml/util/skel/common/Dockerfile`
          - `FROM registry.dffml.org/dffml:sha256@babebabe`
- Future
  - [ ] Template Dockerfiles `FROM` using dataflows and `Inputs` stored in files which are loaded and cached using native caching semantics per orchestrator (deployment).
    - Example native caching semantics, using `paths` see in https://github.com/actions/cache