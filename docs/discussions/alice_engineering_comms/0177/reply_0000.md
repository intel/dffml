## 2023-02-13 @pdxjohnny Engineering Logs

- Downstream request

```
Data to sign (request-target): post /push/inbox
host: vcs.activitypub.securitytxt.dffml.chadig.com
date: Mon, 13 Feb 2023 14:38:08 GMT
digest: SHA-256=xvQlt8xT5UzECmeLhU94qWLWL6hHug6smeMqgqEihTE=
```

- Upstream verification

```
Data to compare (request-target): post /push/inbox
host: vcs.activitypub.securitytxt.dffml.chadig.com:80
date: Mon, 13 Feb 2023 14:38:08 GMT
digest: SHA-256=xvQlt8xT5UzECmeLhU94qWLWL6hHug6smeMqgqEihTE=
Error: Invalid request signature.
```

- It was the port on `host`
- Within `src/request.ts:verify()` it's not using the FDQN, it's using the
  `Host` header which will be modified by the reverse proxy.

```typescript
return `${header}: ${req.get(header)}`
```

- https://caddyserver.com/docs/quick-starts/reverse-proxy#reverse-proxy-quick-start
  - https://caddyserver.com/docs/command-line#reverse-proxy
    - > `--change-host-header` will cause Caddy to change the Host header from the incoming value to the address of the upstream.
      - Not it rebuilds `host` within `verify()` to just be `:8000`, not what we want, we want the `FDQN`

```console
$ FDQN=vcs.activitypub.securitytxt.dffml.chadig.com WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=push ADMIN_USERNAME=admin ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start

> dumbo@1.0.0 start
> node build/index.js

Dumbo listening on port 8000…
GET /push 200 1493 - 11.075 ms
Data to compare (request-target): post /push/inbox
host: :8000
date: Mon, 13 Feb 2023 14:44:32 GMT
digest: SHA-256=3TGS+O9ajWB71TSN6Tm5IBVBizH35dxrE1wDw7LAw9Y=
Error: Invalid request signature.
    at verify (file:///home/alice/activitypub-starter-kit-alternate_port/build/request.js:123:15)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
    at async file:///home/alice/activitypub-starter-kit-alternate_port/build/activitypub.js:36:16
POST /push/inbox 401 12 - 616.413 ms
```

[![use-the-source](https://img.shields.io/badge/use%20the-source-blueviolet)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#use-the-source-)

```console
$ git grep FDQN
src/index.ts:7:import { ADMIN_USERNAME, ADMIN_PASSWORD, ACCOUNT, HOSTNAME, PORT, PROTO, FDQN } from "./env.js";
src/index.ts:78:const endpoint: string = (FDQN != null ? FDQN: `${HOSTNAME}:${PORT}`);
```

```typescript
       else if (FDQN != null && header === "host")
        return `host: ${FDQN}`;
```

- Downstream

```console
$ curl -ku alice:$(cat ../password) -X POST -v http://localhost:8000/admin/follow/push/vcs.activitypub.securitytxt.dffml.chadig.com/443/https
* Uses proxy env variable no_proxy == 'localhost,127.0.0.0/8,::1'
*   Trying 127.0.0.1:8000...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
* Server auth using Basic with user 'alice'
> POST /admin/follow/push/vcs.activitypub.securitytxt.dffml.chadig.com/443/https HTTP/1.1
> Host: localhost:8000
> Authorization: Basic YWxpY2U6ODkyZTI1Y2MwMTMzYTcwYTEzMzRlYTIyNmQ2NDNkNTNhMDRjYzc5MDIwOWM0MzY1ZTUwMzA2Mjc3MGVmZTdmOWVlM2M3MDI4OWNlODdiYzJmZThiYzE2NGNlNTQxYTYx
> User-Agent: curl/7.68.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 204 No Content
< X-Powered-By: Express
< ETag: W/"a-bAsFyilMr4Ra1hIU5PyoyFRunpI"
< Date: Mon, 13 Feb 2023 14:50:51 GMT
< Connection: keep-alive
< Keep-Alive: timeout=5
<
* Connection #0 to host localhost left intact
```

- Upstream

```
Dumbo listening on port 8000…
GET /push 200 1493 - 7.432 ms
Data to compare (request-target): post /push/inbox
host: vcs.activitypub.securitytxt.dffml.chadig.com
date: Mon, 13 Feb 2023 14:50:49 GMT
digest: SHA-256=4byRebHbzxk6BlJopQYVQcI+9YiHojWKhaI2S0J8w68=
Data to sign (request-target): post /alice/inbox
host: d30a15e2d986dc.lhr.life
date: Mon, 13 Feb 2023 14:50:50 GMT
digest: SHA-256=QOPUiXd5oq6u0i+DNQu9TZRIydnRewGdlN1eoiaEsKs=
GET /push 200 1493 - 1.654 ms
POST /push/inbox 204 - - 1557.550 ms
```

- 🚀 BOOYAH BABY WE HAVE LIFTOFF! 🛤️🛤️🛤️🛤️🛤️🛤️🛤️
- Rebase and cleanup
  - `HEAD` is 6 commits, at 9d16b1fe04b5e880be59d6fcddde698cfd036b2f
- Redeploy upstream

```console
$ curl -sfL https://github.com/pdxjohnny/activitypub-starter-kit/archive/refs/heads/alternate_port.tar.gz | tar xvz
$ cd activitypub-starter-kit-alternate_port
$ cat > .env <<'EOF'
# The Node environment
NODE_ENV="production"

# The path to the database schema
SCHEMA_PATH="db/schema.sql"

# The path to the database file
DATABASE_PATH="db/database.sqlite3"

# The hostname (i.e. the "example.com" part of https://example.com/alice)
HOSTNAME="vcs.activitypub.securitytxt.dffml.chadig.com"

# The account name (i.e. the "alice" part of https://example.com/alice)
ACCOUNT="push"
EOF
$ npm i
$ head -n 10000 /dev/urandom | sha384sum | awk '{print $1}' | tee ../webhook
$ head -n 10000 /dev/urandom | sha384sum | awk '{print $1}' | tee ../password
$ openssl genrsa -out keypair.pem 4096 && openssl rsa -in keypair.pem -pubout -out publickey.crt && openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key
$ mkdir node_modules/@types/simple-proxy-agent/
$ echo "declare module 'simple-proxy-agent';" | tee node_modules/@types/simple-proxy-agent/index.d.ts
$ npm run build
$ FDQN=vcs.activitypub.securitytxt.dffml.chadig.com WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=push ADMIN_USERNAME=admin ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start

> dumbo@1.0.0 start
> node build/index.js

Dumbo listening on port 8000…
GET /push 200 1493 - 8.201 ms
GET /push 200 1493 - 1.200 ms
POST /push/inbox 204 - - 1583.186 ms
```

- Redeploy downstream and send follow request

```console
$ rm -f db/database.sqlite3; ssh -R 80:localhost:8000 nokey@localhost.run 2>&1 | tee >(grep --line-buffered 'tunneled with tls termination' | awk -W interactive '{print $1}' | xargs -l -I '{}' -- sh -c 'reset; echo "{}"; PROTO=https FDQN="{}" WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start &
c4d2dfa777b86f.lhr.life

> dumbo@1.0.0 start
> node build/index.js

Dumbo listening on port 8000…
GET /alice 200 1354 - 2.530 ms
GET /alice 200 1354 - 0.895 ms
POST /alice/inbox 204 - - 71.294 ms
POST /admin/follow/push/vcs.activitypub.securitytxt.dffml.chadig.com/443/https 204 - - 3183.157 ms
$ curl -ku alice:$(cat ../password) -X POST -v http://localhost:8000/admin/follow/push/vcs.activitypub.securitytxt.dffml.chadig.com/443/https
$ websocat --exit-on-eof --basic-auth alice:$(cat ../password) ws://localhost:8000/listen/websocket
```

- Create post on upstream

```console
$ cat > post.json <<'EOF'
{
    "object": {
        "type": "Note",
        "content": "OUR PROPHECY MUST BE FULFILLED!!! https://github.com/intel/dffml/pull/1401#issuecomment-1168023959"
    }
}
EOF
$ curl -u admin:$(cat ../password) -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/create
POST /admin/create 204 - - 133.004 ms
file:///home/alice/activitypub-starter-kit-alternate_port/build/request.js:19
        throw new Error(`Received ${res.status} fetching actor. Body: ${response_body}`);
              ^

Error: Received 503 fetching actor. Body: no ssh tunnel here :(
    at fetchActor (file:///home/alice/activitypub-starter-kit-alternate_port/build/request.js:19:15)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
    at async send (file:///home/alice/activitypub-starter-kit-alternate_port/build/request.js:31:19)
```

- Restarted the ssh tunnel and followed again
  - Response seen from downstream websocket listener

```json
{
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Create",
    "published": "2023-02-13T15:39:08.628Z",
    "actor": "https://vcs.activitypub.securitytxt.dffml.chadig.com/push",
    "to": [
        "https://www.w3.org/ns/activitystreams#Public"
    ],
    "cc": [
        "https://eb62a3437cf6a9.lhr.life/alice"
    ],
    "object": {
        "attributedTo": "https://vcs.activitypub.securitytxt.dffml.chadig.com/push",
        "published": "2023-02-13T15:39:08.628Z",
        "to": [
            "https://www.w3.org/ns/activitystreams#Public"
        ],
        "cc": [
            "https://vcs.activitypub.securitytxt.dffml.chadig.com/push/followers"
        ],
        "type": "Note",
        "content": "OUR PROPHECY MUST BE FULFILLED!!! https://github.com/intel/dffml/pull/1401#issuecomment-1168023959",
        "id": "https://vcs.activitypub.securitytxt.dffml.chadig.com/push/posts/15f4de9c-a582-4f9d-8372-a740a5ffe6a8"
    },
    "id": "https://vcs.activitypub.securitytxt.dffml.chadig.com/push/posts/58f883cd-0252-4319-a934-3ca2eb062f62"
}
```

- MOTHERFUCKER FUCK YES FUCK YES FUCK YES FUCK YES!!!!!!!
  - [![hack-the-planet](https://img.shields.io/badge/hack%20the-planet-blue)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#hack-the-planet-)

![hack-the-planet-hackers-gif](https://user-images.githubusercontent.com/5950433/191852910-73787361-b00c-4618-bc5e-f32d656bbf0f.gif)

- Friends, today is a GREAT day :D 🛤️🛤️🛤️🛤️🛤️🛤️🛤️

![Alice-playing-croquet](https://user-images.githubusercontent.com/5950433/218513641-f32f8793-37f7-4490-b258-639689acb89c.png)

https://github.com/intel/dffml/blob/d1283f6564423ed1a08713deffbd6ab38a4cdcee/operations/innersource/dffml_operations_innersource/operations.py#L244-L265

- https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28
- **TODO** Modify below example from the other day to explain how Entities can share data, such as vuln data sharing (OpenSSF Stream 8) data to facilitate software lifecycle data via the [Agora Protocol](https://anagora.org/agora-pkg-chapter)
  - https://github.com/ietf-scitt/use-cases/blob/8cc3a57a1d5d86d27af28e38b5f4d6f93f165ae0/openssf_metrics.md?plain=1#L669
  - https://time.crystals.prophecy.chadig.com
    - https://twitter.com/OR13b/status/1621907110572310528
      - Actor `acquire`
        - `attachments` `Link` to `activitypubextensions` thread
        - `content: "activitypubextensions"` thread
          - `inReplyTo: "$activitypubextensions_thread", content: "https://time.crystals.prophecy.chadig.com/bulk.1.0.0.schema.json"` thread
            - This becomes analogous to shared stream of consciousness uniform API for submitting across contexts (Manifests).
              - CI/CD across projects with different orchestrators for downstream validation of the 2nd and 3rd party plugin ecosystem.
                - This facilitates communication across pipelines across repos across PRs so we can use versioned learning to promote across trust boundaries (3rd party to 2nd party or support level 2 to 1)
                - #1207
                - #1315
                - Alice helps us see risk over time, this is where we see Coach Alice, cartography used applied to dev branches, we grow closer to distributed compute with this, as iteration time is on dev branches rather than release or main
                  - This will probably be part of Alice and the Health of the Ecosystem
      - Ask him to reply to `@acquire@time.crystals.prophecy.chadig.com`
    - ActivityPub Actor watches for messages replying to certain threads
      - https://github.com/pdxjohnny/activitypubsecuritytxt
    - Actor creates pull request to https://github.com/OR13/endor style repo
      - Actor creates didme.me and gets VC SCITT receipt for associated `did:pwk:` (committed into Endor fork, he'd used git as database)
        - This could also be our content address of something in oras.land
        - In the AI training data/human case we see the input data (meme) validated via SCITT
          - We want to enable application of policy to data set ingestion, because this will happen in MLOps aka CI/CD
           - Workstream: AI Ethics
        - In the CI/CD use case, we see the input data (manifest referenced content, images, packages, metrics data output `FROM scratch` OpenSSF metrics use case) validated via SCITT.
        - Later we build up the threat modeling for the dynamic analysis portion of Alice which plays with input data as changes to repos and connects more of our Data, Analysis, Control for the software development process.
      - Actor replies to Orie's reply with his receipt for his time crystals.
    - For k8s style or OS DecentAlice style deployments (OSS scanning feeding OpenSSF metrics) we could run the graphed trust / event chain to a sidecar ActivityPub Actor / root of trust.
- For 2nd party container rebuild chains
  - https://regexpattern.com/sha-256-hash/
  - https://stackoverflow.com/questions/23551008/sed-with-regular-expression

```console
$ export IMAGE="registry.example.org/dffml"; export NEW_HASH=""; sed -i -r -e "s#${IMAGE}@sha256:[A-Fa-f0-9]{64}#${IMAGE}@sha256:${NEW_HASH}#g" $(git grep "${IMAGE}" | sed -e 's/:.*//g' | sort | uniq)
```

- https://anagora.org/raw/garden/unrival/index.md
  - https://github.com/unrival-protocol/documentation
    - Stale
- TODO
  - [x] POC CI/CD/AI/Human comms (aka vuln sharing and downstream validation across walled gardens, aka across repos to facilitate granular permissions for poly repo envs, our 2nd party and 3rd party setup, ref: Alice  playing croquet)
    - [x] RFCv1 https://github.com/ietf-scitt/use-cases/blob/2d7d48efba01de89cd2e072dc1e30d7473f4f472/openssf_metrics.md#activitypub-extensions-for-securitytxt
  - [ ] Disable server stop on any exceptions, just keep on serving
  - [ ] `websocat --exit-on-eof --basic-auth alice:$(cat ../password) ws://localhost:8000/listen/websocket | tee staging_tempfile_for_testing | alice threats listen stdin activitypub`
    - We're about to start rolling very slowly (eventually we'll gain enough acceleration that the answer to Alice are you Rolling? will be YES!, however what we currently have is just the tippy top of the iceburg of what's needed for that, which is why that's volume 6)
      - Ref Entity Analysis Trinity: https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#entity-analysis-trinity
  - [x] Make it through the day
- Future
  - [ ] Put `/webhook` should be `/admin/webhook`
  - [ ] `alice threats serve`