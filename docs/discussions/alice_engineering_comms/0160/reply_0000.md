## 2023-01-27 @pdxjohnny Engineering Logs

```console
$ ssh -R 80:localhost:8000 nokey@localhost.run &
8c0fe6b82d8db0.lhr.life tunneled with tls termination, https://8c0fe6b82d8db0.lhr.life/
$ openssl genrsa -out keypair.pem 4096 && openssl rsa -in keypair.pem -pubout -out publickey.crt && openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key
$ FDQN=8c0fe6b82d8db0.lhr.life PORT=8000 ADMIN_USERNAME=alice ADMIN_PASSWORD=alice PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run dev
$ curl -u alice:alice -X POST -v https://8c0fe6b82d8db0.lhr.life/admin/follow/alice/8c0fe6b82d8db0.lhr.life/443/https
$ curl -u alice:alice -X POST --header "Content-Type: application/json" --data @post.json -v https://8c0fe6b82d8db0.lhr.life/admin/create
```

- https://asciinema.org/a/554880
  - localhost.run to test with HTTPS
    - Success!
    - https://github.com/pdxjohnny/activitypub-starter-kit/commit/871ddad4ee774e4452b71075350fde723fe090f7
- https://goharbor.io/docs/2.7.0/install-config/download-installer/

![image](https://user-images.githubusercontent.com/5950433/215056574-8eb9ae89-f395-4381-8573-6a4b7a15ed67.png)

![image](https://user-images.githubusercontent.com/5950433/215056602-032f6068-e6b7-416b-b029-603106b68c74.png)

![image](https://user-images.githubusercontent.com/5950433/215057033-8cc8f889-2fcf-4736-898c-1d85612bd98c.png)

- https://github.com/jakelazaroff/activitypub-starter-kit/pull/2
- Alice's first post has federated it's way on over to mastodon.social!
  - https://mastodon.social/@alice@70739a422394f5.lhr.life/109760532115001430
- https://github.com/distribution/distribution
- We have the basis for our distributed stream of consciousness
  - We'll work to move from federation to true decentralization ASAP
    - https://areweweb5yet.com/ - 51%
- What do we want now?
  - Register webhooks for GitHub and Harbor or ORAS.land
    - GitHub
      - Push event
        - We want to know when Dockerfiles change so we can analyze them and dispatch any downstream workflows.
      - Everything else
        - Proxy to ActivityPub notes
    - Container registry
      - Image pushed
        - Create ActivityPub note with version and content address
  - We can leverage the 0010-Schema ADR to make posts json manifest instances
- https://github.com/digitalocean/sample-nodejs
- https://github.com/digitalocean/sample-websocket/blob/main/.do/app.yaml
- https://goharbor.io/docs/2.7.0/install-config/installation-prereqs/
  - Spun up VM with minimum requirements ($12/month on DO, will move to DevCloud later with ephemeral infra)
- DNS nameservers updated to DO
  - dffml.registry.chadig.com is correctly resolving
    - Confirmed via `dig`

```console
$ dig dffml.registry.chadig.com

; <<>> DiG 9.18.8 <<>> dffml.registry.chadig.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 9790
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;dffml.registry.chadig.com.     IN      A

;; ANSWER SECTION:
dffml.registry.chadig.com. 3600 IN      A       143.244.181.104

;; Query time: 68 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
;; WHEN: Fri Jan 27 02:39:06 PST 2023
;; MSG SIZE  rcvd: 70
```

- https://github.com/mholt/caddy-l4
  - Forgot about this, layer 4 ssh proxing for caddy
- https://caddyserver.com/docs/quick-starts/reverse-proxy
- https://caddyserver.com/docs/command-line#caddy-reverse-proxy
- Create `alice` user, download caddy for auto https

```console
[root@prophecy-0 ~]# curl -fLo caddy "https://caddyserver.com/api/download?os=linux&arch=amd64"
[root@prophecy-0 ~]# chmod 755 caddy
[root@prophecy-0 ~]# mv caddy /usr/bin/caddy
[root@prophecy-0 ~]# setcap CAP_NET_BIND_SERVICE=+eip /usr/bin/caddy
[root@prophecy-0 ~]# dnf module install -y tmux nodejs:16
[root@prophecy-0 ~]# useradd -m -s $(which bash) alice
[root@prophecy-0 ~]# su alice
```

- Download and compile the activitypub server
- https://github.com/pdxjohnny/activitypub-starter-kit/commit/be9be9bf8e307c36a09e80ed96579bd436d01e73

```console
[alice@prophecy-0 ~]$ tmux
[alice@prophecy-0 ~]$ curl -sfL https://github.com/pdxjohnny/activitypub-starter-kit/archive/refs/heads/alternate_port.tar.gz | tar xvz
[alice@prophecy-0 ~]$ cd activitypub-starter-kit-alternate_port/
[alice@prophecy-0 ~]$ npm install
[alice@prophecy-0 ~]$ npm run build
[alice@prophecy-0 ~]$ head -n 10000 /dev/urandom | sha384sum | awk '{print $1}' | tee ../password
[alice@prophecy-0 ~]$ head -n 10000 /dev/urandom | sha384sum | awk '{print $1}' | tee ../webhook
[alice@prophecy-0 ~]$ openssl genrsa -out keypair.pem 4096 && openssl rsa -in keypair.pem -pubout -out publickey.crt && openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key
[alice@prophecy-0 ~]$ cat .env <<'EOF'
# The Node environment
NODE_ENV="production"

# The path to the database schema
SCHEMA_PATH="db/schema.sql"

# The path to the database file
DATABASE_PATH="db/database.sqlite3"

# The hostname (i.e. the "example.com" part of https://example.com/alice)
HOSTNAME="prophecy.chadig.com"

# The account name (i.e. the "alice" part of https://example.com/alice)
ACCOUNT="alice"
EOF
[alice@prophecy-0 ~]$ FDQN=prophecy.chadig.com WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start
```

- Now run the reverse proxy in another tmux pane (eventually auto start with systemd based off image to VM builds)

```console
[alice@prophecy-0 ~]$ caddy reverse-proxy --from https://prophecy.chadig.com --to :8000
2023/01/27 11:38:17.564 WARN    admin   admin endpoint disabled
2023/01/27 11:38:17.566 INFO    http    server is listening only on the HTTPS port but has no TLS connection policies; adding one to enable TLS {"server_name": "proxy", "https_port": 443}
2023/01/27 11:38:17.567 INFO    http    enabling automatic HTTP->HTTPS redirects        {"server_name": "proxy"}
2023/01/27 11:38:17.568 INFO    http    enabling HTTP/3 listener        {"addr": ":443"}
2023/01/27 11:38:17.569 INFO    failed to sufficiently increase receive buffer size (was: 208 kiB, wanted: 2048 kiB, got: 416 kiB). See https://github.com/lucas-clemente/quic-go/wiki/UDP-Receive-Buffer-Size for details.
2023/01/27 11:38:17.569 INFO    http.log        server running  {"name": "proxy", "protocols": ["h1", "h2", "h3"]}
2023/01/27 11:38:17.570 INFO    http.log        server running  {"name": "remaining_auto_https_redirects", "protocols": ["h1", "h2", "h3"]}
2023/01/27 11:38:17.571 INFO    http    enabling automatic TLS certificate management   {"domains": ["prophecy.chadig.com"]}
Caddy proxying https://prophecy.chadig.com -> :8000
2023/01/27 11:38:17.572 INFO    tls.obtain      acquiring lock  {"identifier": "prophecy.chadig.com"}
2023/01/27 11:38:17.578 INFO    tls.obtain      lock acquired   {"identifier": "prophecy.chadig.com"}
2023/01/27 11:38:17.579 INFO    tls.obtain      obtaining certificate   {"identifier": "prophecy.chadig.com"}
2023/01/27 11:38:17.584 INFO    tls.cache.maintenance   started background certificate maintenance      {"cache": "0xc00013eee0"}
2023/01/27 11:38:17.586 INFO    tls     cleaning storage unit   {"description": "FileStorage:/home/alice/.local/share/caddy"}
2023/01/27 11:38:17.586 INFO    tls     finished cleaning storage units
2023/01/27 11:38:17.832 INFO    http    waiting on internal rate limiter        {"identifiers": ["prophecy.chadig.com"], "ca": "https://acme-v02.api.letsencrypt.org/directory", "account": ""}
2023/01/27 11:38:17.833 INFO    http    done waiting on internal rate limiter   {"identifiers": ["prophecy.chadig.com"], "ca": "https://acme-v02.api.letsencrypt.org/directory", "account": ""}
2023/01/27 11:38:17.926 INFO    http.acme_client        trying to solve challenge       {"identifier": "prophecy.chadig.com", "challenge_type": "tls-alpn-01", "ca": "https://acme-v02.api.letsencrypt.org/directory"}
2023/01/27 11:38:18.070 INFO    tls     served key authentication certificate   {"server_name": "prophecy.chadig.com", "challenge": "tls-alpn-01", "remote": "54.244.41.23:38056", "distributed": false}
2023/01/27 11:38:18.157 INFO    tls     served key authentication certificate   {"server_name": "prophecy.chadig.com", "challenge": "tls-alpn-01", "remote": "23.178.112.106:16466", "distributed": false}
2023/01/27 11:38:18.201 INFO    tls     served key authentication certificate   {"server_name": "prophecy.chadig.com", "challenge": "tls-alpn-01", "remote": "18.224.32.186:23554", "distributed": false}
2023/01/27 11:38:18.530 INFO    http.acme_client        authorization finalized {"identifier": "prophecy.chadig.com", "authz_status": "valid"}
2023/01/27 11:38:18.532 INFO    http.acme_client        validations succeeded; finalizing order {"order": "https://acme-v02.api.letsencrypt.org/acme/order/936031817/161295115697"}
2023/01/27 11:38:18.943 INFO    http.acme_client        successfully downloaded available certificate chains    {"count": 2, "first_url": "https://acme-v02.api.letsencrypt.org/acme/cert/03b13046a47a2e95fe2496fc4d8c64aac8d0"}
2023/01/27 11:38:18.945 INFO    tls.obtain      certificate obtained successfully       {"identifier": "prophecy.chadig.com"}
2023/01/27 11:38:18.946 INFO    tls.obtain      releasing lock  {"identifier": "prophecy.chadig.com"
```

![Screenshot from 2023-01-27 03-40-30](https://user-images.githubusercontent.com/5950433/215078120-ae508beb-ba70-410c-b2ca-0cc1b193a30a.png)

- https://mastodon.social/@alice@prophecy.chadig.com
- https://github.com/intel/dffml/issues/1247#issuecomment-1371317321
  - Now in webhook beta so should be able to test via CLI
  - https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads?actionType=edited#discussion_comment
  - https://docs.github.com/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#push

```console
$ gh webhook forward --repo=intel/dffml --events=discussion_comment --url=http://localhost:8000/webhook/$(cat ../webhook) &
Forwarding Webhook events from GitHub...

$ rm -f db/database.sqlite3
$ PROTO=http FDQN=localhost:8000 WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run dev &
Dumbo listening on port 8000…
POST /webhook/b7ad8661a006195b317985d922b2ff37ebe8beac9a8f9cfe4ba0a177848c5e96e75ff926de82e87943ea79dca533cdc7 204 - - 13.781 ms
GET /alice/outbox 200 40582 - 2.251 ms
$ curl -s http://localhost:8000/alice/outbox | python -c 'import yaml, json, sys; print(yaml.dump(json.load(sys.stdin)))'
```

- It's alive! :)

```yaml
'@context': https://www.w3.org/ns/activitystreams
id: http://localhost:8000/alice/outbox
orderedItems:
- '@context': https://www.w3.org/ns/activitystreams
  actor: http://localhost:8000/alice
  cc: []
  id: http://localhost:8000/alice/posts/48c61646-1538-471b-92e1-4d30a7337336
  object:
    attributedTo: http://localhost:8000/alice
    cc:
    - http://localhost:8000/alice/followers
    content: "{\"action\":\"edited\",\"comment\":{\"id\":4794771,\"node_id\":\"DC_kwDOCOlgGM4ASSmT\"\
      ,\"html_url\":\"https://github.com/intel/dffml/discussions/1406#discussioncomment-4794771\"\
      ,\"parent_id\":4794098,\"child_comment_count\":0,\"repository_url\":\"intel/dffml\"\
      ,\"discussion_id\":4225995,\"author_association\":\"MEMBER\",\"user\":{\"login\"\
      :\"pdxjohnny\",\"id\":5950433,\"node_id\":\"MDQ6VXNlcjU5NTA0MzM=\",\"avatar_url\"\
      :\"https://avatars.githubusercontent.com/u/5950433?v=4\",\"gravatar_id\":\"\"\
      ,\"url\":\"https://api.github.com/users/pdxjohnny\",
      :\"https://api.github.com/users/pdxjohnny/gists{/gist_id}\",\"starred_url\"\
      ,\"type\":\"User\",\"site_admin\":false}}"
    id: http://localhost:8000/alice/post/58688c80-f982-4dc0-a676-34c955c4a4cd
    published: '2023-01-27T17:49:23.949Z'
    to:
    - https://www.w3.org/ns/activitystreams#Public
    type: Note
  published: '2023-01-27T17:49:23.000Z'
  to:
  - https://www.w3.org/ns/activitystreams#Public
  type: Create
totalItems: 1
type: OrderedCollection
```

- https://stedolan.github.io/jq/manual/
- https://stackoverflow.com/questions/38061346/jq-output-array-of-json-objects

**schema/alice/shouldi/contribute/0.0.0.schema.json**

```json
{
    "$id": "https://github.com/intel/dffml/raw/alice/schema/alice/shouldi/contribute/0.0.0.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "description": "Schema for Alice Should I Contribute? Gatekeeper",
    "properties": {
        "$schema": {
            "type": "string"
        },
        "community_health_check": {
            "description": "Community Health Check",
            "$ref": "#/definitions/community_health_check"
        },
    },
    "additionalProperties": false,
    "required": [
        "$schema",
        "community_health_check"
    ]
    "definitions": {
        "community_health_check": {
            "type": "object",
            "properties": {
                "has_support": {
                    "description": "FileSupportPresent",
                    "type": "boolean",
                    "enum": [true]
                },
            },
            "additionalProperties": false,
            "required": [
                "has_support"
            ]
        }
    }
}
```

- Playing with output operation as schema validation to assist with data model alignment

```console
$ alice shouldi contribute -keys https://github.com/pdxjohnny/httptest | tee dffml_list_records_stdout.json
[████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] Running CodeNarc for 29s
```

**dffml_list_records_stdout.json**

```json
[
    {
        "extra": {},
        "features": {
            "ActionsValidatorBinary": [],
            "CodeNarcServerProc": [],
            "FileCodeOfConductPresent": [
                false
            ],
            "FileContributingPresent": [
                false
            ],
            "FileReadmePresent": [
                true
            ],
            "FileSecurityPresent": [
                false
            ],
            "FileSupportPresent": [
                false
            ],
            "GitHubActionsWorkflowUnixStylePath": [
                ".github/workflows/tests.yml",
                ".github/workflows/release.yml"
            ],
            "HasDocs": [
                {
                    "example": false,
                    "known issues": false,
                    "readme_present": true,
                    "support": true,
                    "usage": true
                }
            ],
            "JavaBinary": [],
            "NPMGroovyLintCMD": [],
            "NPMGroovyLintResult": [
                {
                    "files": {},
                    "summary": {
                        "detectedRules": {},
                        "fixedRules": {},
                        "totalFilesLinted": 0,
                        "totalFilesWithErrorsNumber": 0,
                        "totalFixedErrorNumber": 0,
                        "totalFixedInfoNumber": 0,
                        "totalFixedNumber": 0,
                        "totalFixedWarningNumber": 0,
                        "totalFoundErrorNumber": 0,
                        "totalFoundInfoNumber": 0,
                        "totalFoundNumber": 0,
                        "totalFoundWarningNumber": 0,
                        "totalRemainingErrorNumber": 0,
                        "totalRemainingInfoNumber": 0,
                        "totalRemainingNumber": 0,
                        "totalRemainingWarningNumber": 0
                    }
                }
            ],
            "RepoDirectory": [
                "/tmp/dffml-feature-git-zcv0u_6h"
            ],
            "URL": [],
            "author_count": [
                0
            ],
            "author_line_count": [
                {}
            ],
            "commit_count": [
                0
            ],
            "date": [
                "2023-01-27 19:15"
            ],
            "date_pair": [
                [
                    "2023-01-27 19:15",
                    "2022-10-27 19:15"
                ]
            ],
            "git_branch": [],
            "git_commit": [
                "0486a73dcadafbb364c267e5e5d0161030682599"
            ],
            "git_remote": [],
            "git_repository": [],
            "git_repository_checked_out": [
                {
                    "URL": "https://github.com/pdxjohnny/httptest",
                    "commit": "0486a73dcadafbb364c267e5e5d0161030682599",
                    "directory": "/tmp/dffml-feature-git-zcv0u_6h"
                }
            ],
            "quarter": [],
            "quarter_start_date": [],
            "release_within_period": [
                false
            ],
            "str": [],
            "valid_git_repository_URL": [],
            "work_spread": [
                0
            ]
        },
        "key": "https://github.com/pdxjohnny/httptest",
        "last_updated": "2023-01-27T19:16:37Z"
    }
]
```

```console
$ jq '.[].features | {repo_url: .git_repository_checked_out[0].URL, community_health_check: {has_support: (if .FileSupportPresent then .FileSupportPresent[0] else false end)}}' dffml_list_records_stdout.json | jq -s
[
  {
    "repo_url": "https://github.com/pdxjohnny/httptest",
    "community_health_check": {
      "has_support": false
    }
  }
]
```

- https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md
- https://github.com/intel/dffml/blob/alice/docs/arch/0010-Schema.rst

```console
$ jsonschema --instance <(jq '.[].features | {repo_url: .git_repository_checked_out[0].URL, community_health_check: {has_support: (if .FileSupportPresent then .FileSupportPresent[0] else false end)}}' dffml_list_records_stdout.json | jq -s | jq '.[0]') 0.0.0.schema.json
False: False is not one of [True]
{'repo_url': 'https://github.com/pdxjohnny/httptest', 'community_health_check': {'has_support': False}}: Additional properties are not allowed ('repo_url' was unexpected)
{'repo_url': 'https://github.com/pdxjohnny/httptest', 'community_health_check': {'has_support': False}}: '$schema' is a required property
```

- We can leverage the GitHub CLI webhook proxy to bypass static registration
  - We can have periodically scheduled jobs on runners we add which just sit and translate
  - [![hack-the-planet](https://img.shields.io/badge/hack%20the-planet-blue)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#hack-the-planet-)
- https://stackoverflow.com/questions/22429744/how-to-setup-route-for-websocket-server-in-express
  - Looking to decouple listening for events via websocket
  - https://github.com/vi/websocat
  - https://github.com/websockets/ws#server-broadcast
  - https://github.com/websockets/ws#how-to-detect-and-close-broken-connections
  - https://github.com/websockets/ws#client-authentication
  - https://github.com/LionC/express-basic-auth
- https://github.com/jakelazaroff/activitypub-starter-kit/commit/ca1ac728af3eaa1cc8f7f0af201e398bc6a1b3ec
  - Basic no auth Websocket inbox rebroadcast to connected clients

```console
$ curl -fLo websocat https://github.com/vi/websocat/releases/download/v1.11.0/websocat.x86_64-unknown-linux-musl
$ chmod 755 websocat
$ mv websocat ~/.bin/
$ websocat --exit-on-eof ws://localhost:8000/listen/websocket &
{"@context":"https://www.w3.org/ns/activitystreams","type":"Create","published":"2023-01-28T00:06:07.286Z","actor":"http://localhost:8000/alice","to":["https://www.w3.org/ns/activitystreams#Public"],"cc":["http://localhost:8000/alice"],"object":{"attributedTo":"http://localhost:8000/alice","published":"2023-01-28T00:06:07.286Z","to":["https://www.w3.org/ns/activitystreams#Public"],"cc":["http://localhost:8000/alice/followers"],"type":"Note","content":"Alice is Here!","id":"http://localhost:8000/alice/post/493e970e-ca9f-43ce-97e3-453c6677ecf0"},"id":"http://localhost:8000/alice/post/3ed6a6f4-4da0-4386-9faf-6eaec0d83240"}
$ curl -u alice:$(cat ../password) -X POST -v http://localhost:8000/admin/follow/alice/localhost/8000/http
$ curl -u alice:$(cat ../password) -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/create
```

- Success, now to add auth to WebSocket connection
  - https://spdx.dev/ids/
  - https://github.com/LionC/express-basic-auth/blob/dd17b4de9fee9558269cdc583310bde5331456e7/index.js#L1-L17
  - https://github.com/jshttp/basic-auth#example
  - https://stackoverflow.com/questions/63552689/how-to-deal-with-server-handleupgrade-was-called-more-than-once-in-nodejs

**post.json**

```json
{
  "object": {
    "type": "Note",
    "content": "Alice is Here!"
  }
}
```

```console
$ rm -f db/database.sqlite3; PROTO=http HOSTNAME=localhost WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run dev &
$ websocat --exit-on-eof ws://localhost:8000/listen/websocket
websocat: WebSocketError: WebSocketError: Received unexpected status code (401 Unauthorized)
websocat: error running
$ websocat --exit-on-eof --basic-auth alice:alice ws://localhost:8000/listen/websocket
websocat: WebSocketError: WebSocketError: Received unexpected status code (401 Unauthorized)
websocat: error running
$ websocat --exit-on-eof --basic-auth alice:$(cat ../password) ws://localhost:8000/listen/websocket &
{"@context":"https://www.w3.org/ns/activitystreams","id":"http://localhost:8000/a0265dc0-e781-4f5b-89dd-0e1c36454a37","type":"Accept","actor":"http://localhost:8000/alice","object":{"@context":"https://www.w3.org/ns/activitystreams","id":"http://localhost:8000/@914e5adf-e47d-4c2a-a4be-48546081b6be","type":"Follow","actor":"http://localhost:8000/alice","object":"http://localhost:8000/alice"}}
{"@context":"https://www.w3.org/ns/activitystreams","id":"http://localhost:8000/@914e5adf-e47d-4c2a-a4be-48546081b6be","type":"Follow","actor":"http://localhost:8000/alice","object":"http://localhost:8000/alice"}
{"@context":"https://www.w3.org/ns/activitystreams","type":"Create","published":"2023-01-28T00:52:56.799Z","actor":"http://localhost:8000/alice","to":["https://www.w3.org/ns/activitystreams#Public"],"cc":["http://localhost:8000/alice"],"object":{"attributedTo":"http://localhost:8000/alice","published":"2023-01-28T00:52:56.799Z","to":["https://www.w3.org/ns/activitystreams#Public"],"cc":["http://localhost:8000/alice/followers"],"type":"Note","content":"Alice is Here!","id":"http://localhost:8000/alice/post/3479f6f3-5d8c-48e0-96ea-626760fb6388"},"id":"http://localhost:8000/alice/post/2afd800d-07a6-402e-8585-873e3989ba5e"}
$ curl -u alice:$(cat ../password) -X POST -v http://localhost:8000/admin/follow/alice/localhost/8000/http
$ curl -u alice:$(cat ../password) -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/create
```

- We have liftoff on WebSocket auth!
  - https://github.com/jakelazaroff/activitypub-starter-kit/commit/4e8f9f541bffabe6ab5b0ffe1206d1d9337b5185
- With the account following itself all listeners connected to `/listen/websocket`
  will be notified when the account sent an post.
  - Friends, today is a great day! 🛤️
- Playing with data in websocket listener stream

```console
$ websocat --exit-on-eof --basic-auth alice:$(cat ../password) ws://localhost:8000/listen/websocket | jq --unbuffered -r .
```

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "http://localhost:8000/8f82f22b-28b9-4e16-9c88-9891922253b1",
  "type": "Accept",
  "actor": "http://localhost:8000/alice",
  "object": {
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": "http://localhost:8000/@51e24f61-e594-4cbd-87e1-c6e121e79a2a",
    "type": "Follow",
    "actor": "http://localhost:8000/alice",
    "object": "http://localhost:8000/alice"
  }
}
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "http://localhost:8000/@51e24f61-e594-4cbd-87e1-c6e121e79a2a",
  "type": "Follow",
  "actor": "http://localhost:8000/alice",
  "object": "http://localhost:8000/alice"
}
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Create",
  "published": "2023-01-28T01:24:04.873Z",
  "actor": "http://localhost:8000/alice",
  "to": [
    "https://www.w3.org/ns/activitystreams#Public"
  ],
  "cc": [
    "http://localhost:8000/alice"
  ],
  "object": {
    "attributedTo": "http://localhost:8000/alice",
    "published": "2023-01-28T01:24:04.873Z",
    "to": [
      "https://www.w3.org/ns/activitystreams#Public"
    ],
    "cc": [
      "http://localhost:8000/alice/followers"
    ],
    "type": "Note",
    "content": "Alice is Here!",
    "id": "http://localhost:8000/alice/posts/ac466e40-a7ac-4815-963f-fc419b821f74"
  },
  "id": "http://localhost:8000/alice/posts/78118a66-52a4-402d-ad2e-b6ae79997f57"
}
```

- When querying URLs published found that `post/` should be `posts/`
  - https://www.w3.org/TR/activitypub/
  - https://github.com/jakelazaroff/activitypub-starter-kit/commit/3999fc0f722168b98f6f28fcb2d8521ca600d53e
- Example of resolving each post received from any followed account (could do this with content address within body)
  - https://unix.stackexchange.com/questions/435413/using-jq-within-pipe-chain-produces-no-output

```console
$ websocat --exit-on-eof --basic-auth alice:$(cat ../password) ws://localhost:8000/listen/websocket | jq --unbuffered -r .object.id | xargs -l -I '{}' -- sh -c "curl -sfL '{}' | jq -r" &
{
  "id": "http://localhost:8000/alice/posts/b60924b2-e1dd-4bf1-92bd-a374623064ba",
  "contents": "{\"attributedTo\":\"http://localhost:8000/alice\",\"published\":\"2023-01-28T01:28:24.336Z\",\"to\":[\"https://www.w3.org/ns/activitystreams#Public\"],\"cc\":[\"http://localhost:8000/alice/followers\"],\"type\":\"Note\",\"content\":\"Alice is Here!\"}",
  "created_at": "2023-01-28 01:28:24",
  "createdAt": "2023-01-28T01:28:24.000Z"
}
$ curl -u alice:$(cat ../password) -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/create
```

- Playing with streaming to YAML for readability

```console
$ websocat --exit-on-eof --basic-auth alice:$(cat ../password) ws://localhost:8000/listen/websocket | python -uc "import sys, pathlib, json, yaml; list(map(print, map(yaml.dump, map(json.loads, sys.stdin))))"
```

```yaml
'@context': https://www.w3.org/ns/activitystreams
actor: http://localhost:8000/alice
cc:
- http://localhost:8000/alice
id: http://localhost:8000/alice/posts/ec323059-2b02-49d8-99fe-4f6518f19c95
object:
  attributedTo: http://localhost:8000/alice
  cc:
  - http://localhost:8000/alice/followers
  content: Alice is Here!
  id: http://localhost:8000/alice/posts/018b199a-5131-40ef-9862-0d989f3ec636
  published: '2023-01-28T01:32:46.989Z'
  to:
  - https://www.w3.org/ns/activitystreams#Public
  type: Note
published: '2023-01-28T01:32:46.989Z'
to:
- https://www.w3.org/ns/activitystreams#Public
type: Create

'@context': https://www.w3.org/ns/activitystreams
actor: http://localhost:8000/alice
cc:
- http://localhost:8000/alice
id: http://localhost:8000/alice/posts/d3e1b1e8-bf77-4005-8f29-fab3bc2c6670
object:
  attributedTo: http://localhost:8000/alice
  cc:
  - http://localhost:8000/alice/followers
  content: Alice is Here!
  id: http://localhost:8000/alice/posts/7dcfed5a-5236-4fc2-91a7-bfe79b8540ba
  published: '2023-01-28T01:32:49.343Z'
  to:
  - https://www.w3.org/ns/activitystreams#Public
  type: Note
published: '2023-01-28T01:32:49.343Z'
to:
- https://www.w3.org/ns/activitystreams#Public
type: Create
```

```console
$ curl -s http://localhost:8000/alice | jq -r
```

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1"
  ],
  "id": "http://localhost:8000/alice",
  "type": "Person",
  "preferredUsername": "alice",
  "inbox": "http://localhost:8000/alice/inbox",
  "outbox": "http://localhost:8000/alice/outbox",
  "followers": "http://localhost:8000/alice/followers",
  "following": "http://localhost:8000/alice/following",
  "publicKey": {
    "id": "http://localhost:8000/alice#main-key",
    "owner": "http://localhost:8000/alice",
    "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAozVUsUl3mXxhSJbTGW8K\naOrSzcx7FnZij6Qc5jRmuiGKUlQbwHojhcwQUMkVYioVZR1hK80rKT9FXndDYpjo\nB6O1z92TRYBiwpz2T5VR/1oqtB2j8ajGJbG43wuMvi3f5YYMzl7cySpzwRDCZSzA\njryz7zDBwEu17d912ufUqT7TAbcoGbLx8yM0ONtIDi89WnXZNQk1C3issO2pb/n9\nYtAaXlrsrTeB99IY6I1G9qnq00NkSR2XW6R6+GDFWV2wcu61XKXvMT4g2U6HibrL\nLIVmWv+hPIvvLWweCNpg74gnq8DLa/TMjkt0Q6UImuG3Iwdbg29KOdhS98MmrttR\nRq8ljsttwfwqqyLRZFNQuW2v1ZxwC0BB7XomhkJgdHCIOWGeAULxRlQarlFstT6f\nGaNSlVbcHoKDX6j+XckF+13prsRzWrZxM44v2zw8Yx2oh7LJKcvFdqow8TZBG+Yn\naO6w1Wel2+n92iaOC0oU+sgxtfBvECebzMM94YPB58Ja3hlbIz627Ut+v/TDXHmV\njxueufw285GpSI7GmsZihcdB5eBMIDE0UKnvNbqc+TncoTUXAIxXs7cvnEHusAmM\nONxtxXlRNOSfKaJ/PWkVwa3NvPrd4oeIJWdLRppNd5mYA1i2CkPdd5lBAiMWwk2A\nzP5Hrjlf3/QyZe7mHQAfvjkCAwEAAQ==\n-----END PUBLIC KEY-----"
  }
}
```

- https://www.w3.org/wiki/SocialCG/ActivityPub/MediaUpload
- https://www.w3.org/TR/activitystreams-vocabulary/#dfn-person
  - Person inherits from Object
  - https://www.w3.org/TR/activitystreams-vocabulary/#dfn-summary
    - Object has property summary, which is currently not present in `Person` for user `alice`.
- https://www.rfc-editor.org/rfc/rfc9116#name-contact
  - Proposed extension
    - `Contact: https://example.com/security-contact.html`
    - In the event that the contact URL is resolve to an ActivityPub `Person`
      - https://example.social/@security-contact-handle
    - In the event that the `summary` field for that `Person` is a manifest
      - https://github.com/intel/dffml/raw/alice/schema/security/vulnerability-disclosure-program/0.0.0.schema.json
    - Fulfill the manifest in alignment with it's ADR as needed within context
      - Possible fields in sketch below
        - Later option of DIDs instead of ActivityPub
        - Consider TOML option since easier to parse
          - https://toml.io/en/

**schema/security/vulnerability-disclosure-program/example-pass.yaml**

```yaml
$schema: "https://github.com/intel/dffml/raw/alice/schema/security/vulnerability-disclosure-program/0.0.0.schema.json"
sbom_feed:
- "https://example.social/@security-contact-handle-sbom-feed"
vex_feed:
- "https://example.social/@security-contact-handle-vex-feed"
vdr_feed:
- "https://example.social/@security-contact-handle-vdx-feed"
vcs_feed:
- "https://example.social/@dev-contact-handle-git-feed"
deploy_feed:
- "https://example.social/@ops-contact-handle-deploy-feed"
```

- We could have these be `attachement`s to the `Person` which our server is acting on behalf of.
- `sbom_feed`s can be downstream of `FROM` rebuild streams.
  - #1426
- Expand on ActivityPub spec EXAMPLE 4 `inReplyTo` to and addition of a `/admin/reply` `POST` handler to reply to a `Note`

> ```json
> {"@context": "https://www.w3.org/ns/activitystreams",
>  "type": "Create",
>  "id": "https://chatty.example/ben/p/51086",
>  "to": ["https://social.example/alyssa/"],
>  "actor": "https://chatty.example/ben/",
>  "object": {"type": "Note",
>             "id": "https://chatty.example/ben/p/51085",
>             "attributedTo": "https://chatty.example/ben/",
>             "to": ["https://social.example/alyssa/"],
>             "inReplyTo": "https://social.example/alyssa/posts/49e2d03d-b53a-4c4c-a95c-94a6abf45a19",
>             "content": "<p>Argh, yeah, sorry, I'll get it back to you tomorrow.</p>
>                         <p>I was reviewing the section on register machines,
>                            since it's been a while since I wrote one.</p>"}}
> ```

- Bailing on this for now and just going to spin a separate subdomain feed for webhooks -> vcs feed
  - `@push@git.vcs.dffml.org`

```patch
diff --git a/src/activitypub.ts b/src/activitypub.ts
index a6a90e4..a89b67e 100644
--- a/src/activitypub.ts
+++ b/src/activitypub.ts
@@ -12,7 +12,7 @@ import {
   listPosts,
   updateFollowing,
 } from "./db.js";
-import { HOSTNAME, PORT, ACCOUNT, PUBLIC_KEY, PROTO, FDQN } from "./env.js";
+import { HOSTNAME, PORT, ACCOUNT, PUBLIC_KEY, PROTO, FDQN, SECURITY_TXT_CONTACT_VSC_FEED } from "./env.js";
 import { send, verify } from "./request.js";

 export const activitypub = Router();
@@ -168,6 +168,15 @@ activitypub.get("/:actor/following", async (req, res) => {
   });
 });

+const security_txt_contact_vsc_feed_note = createPost({
+  attributedTo: actor,
+  published: date.toISOString(),
+  to: ["https://www.w3.org/ns/activitystreams#Public"],
+  cc: [`${actor}/followers`],
+  type: "Note",
+  content: (SECURITY_TXT_CONTACT_VSC_FEED !== null) ? SECURITY_TXT_CONTACT_VSC_FEED : "N/A",
+});
+
 activitypub.get("/:actor", async (req, res) => {
   const actor: string = req.app.get("actor");

@@ -185,11 +194,15 @@ activitypub.get("/:actor", async (req, res) => {
     outbox: `${actor}/outbox`,
     followers: `${actor}/followers`,
     following: `${actor}/following`,
+    summary: ``,
     publicKey: {
       id: `${actor}#main-key`,
       owner: actor,
       publicKeyPem: PUBLIC_KEY,
     },
+    attachment: [
+      security_txt_contact_vsc_feed_note,
+    ]
   });
 });

diff --git a/src/env.ts b/src/env.ts
index 3d1eb0f..ae24b27 100644
--- a/src/env.ts
+++ b/src/env.ts
@@ -4,6 +4,7 @@ import dotenv from "dotenv";

 dotenv.config();

+export const SECURITY_TXT_CONTACT_VSC_FEED = process.env.SECURITY_TXT_CONTACT_VSC_FEED || null;
 export const WEBHOOK_PATH = process.env.WEBHOOK_PATH || "webhook";
 export const FDQN = process.env.FDQN || null;
 export const PROTO = process.env.PROTO || "https";
```

- Start `SECURITY_TXT_CONTACT_VSC_FEED` at known location
  - Update `security.txt` in repo with `SECURITY_TXT_CONTACT_VSC_FEED` as
    the `Contact` URL.
- Analysis of repo with `security.txt` pointed to `SECURITY_TXT_CONTACT_VSC_FEED`
  - If the repo is a dependency of a downstream repo we care about.
    - We care about it if resources within the repo are relevant to the downstream
      repos `FROM` rebuild chain
      - Example: action-validator cargo build for `alice shouldi contribute`
        - Some base images require this be rebuilt
    - Two localhost.run subprocess with `dffml.Subproces.STDOUT_READLINE` event
      - Start one 30 seconds after the other
      - Every time we get issued a new URL
        - For the server running which got its address changed, send an unfollow to
          the `SECURITY_TXT_CONTACT_VSC_FEED` being watched for new `push` events.
        - Start a new ActivityPub server for the new domain.
          - Send a follow request to the `SECURITY_TXT_CONTACT_VSC_FEED` for the
            new domain.
        - Start `websocat` to listen for new events using websocket listener API
          - Trigger rebuilds of container images using container image manifest
            and `workflow_dispatch` for any containers which need to be rebuilt
            due to a broadcast VSC `push` event, later for `deploy` container image
            `push` events from registry.
            - https://docs.github.com/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#push
            - https://goharbor.io/docs/1.10/working-with-projects/project-configuration/configure-webhooks/
          - If a `vsc.push` event results in a repo having something we know how to do
            something about to help with (`alice shouldi contribute` -> `alice please contribute`),
            then we can raise an issue or pull request as appropriate.
            - If we find a vuln, log in a SCITT registry via self-noterization or otherwise and
              `inReplyTo` the place the vuln exists.
            - We should `inReplyTo` when we start analysis so we can watch for other replies and see
              what other entities are running analysis jobs. We should then deduplicate based off
              analysis (dataflow) content address. Decentralized actors should be enabled to
              communicate with each other so not all running jobs drop in event of multiple
              of the same launched at the same time (see IPVM caching).
            - https://www.w3.org/TR/activitystreams-vocabulary/#dfn-replies
            - https://www.w3.org/TR/activitystreams-vocabulary/#dfn-attachment
              - Could use pinned post semantics and then inReplyTo to those, parse pinned 
                post content body and attachment to understand what the post is for.
                Or could have two attachments, an image (screenshot as universal API).
                Content is content address of manifest for attachments and own doc.
- Making some demo gifs
  - https://github.com/charmbracelet/vhs#continuous-integration

```console
$ curl -sfL https://github.com/charmbracelet/vhs/releases/download/v0.2.0/vhs_0.2.0_Linux_x86_64.tar.gz | tar xvz
LICENSE
README.md
completions/vhs.bash
completions/vhs.fish
completions/vhs.zsh
manpages/vhs.1.gz
vhs
$ echo 'Output demo.gif' > test.vhs; ./vhs record >> test.vhs
$ echo Hello World
Hello World
$ (Ctrl+D) exit
$ cat test.vhs
Output demo.gif
Sleep 500ms
Type "echo Hello"
Sleep 500ms
Type " World"
Enter
Ctrl+D
$ ./vhs < test.vhs
ttyd is not installed. Install it from: https://github.com/tsl0922/ttyd
$ ssh vhs.example.com < test.vhs > demo.gif
$ curl -sfLo ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64
$ chmod 755 ttyd
$ mv ttyd ~/.local/bin/
$ ./vhs < test.vhs
[launcher.Browser]2023/01/28 05:03:55 try to find the fastest host to download the browser binary
[launcher.Browser]2023/01/28 05:03:55 check https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/1033860/chrome-linux.zip
[launcher.Browser]2023/01/28 05:03:55 check https://registry.npmmirror.com/-/binary/chromium-browser-snapshots/Linux_x64/1033860/chrome-linux.zip
[launcher.Browser]2023/01/28 05:03:55 check https://playwright.azureedge.net/builds/chromium/1033860/chromium-linux-arm64.zip
```

- TODO
  - [ ] Redirect CodeNarc stderr
- Future
  - [ ] DIDme.me for An Image for auto conversion into screenshot YAML manifest for downstreams
  - [ ] Bridge us to DWNs
    - https://identity.foundation/decentralized-web-node/spec/#messages
  - [ ] DWN or activitypub channel helpers
    - WebRTC comms between endpoints
    - DERP ad-hoc