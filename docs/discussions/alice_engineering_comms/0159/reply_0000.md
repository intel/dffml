## 2023-01-26 @pdxjohnny Engineering Logs

- https://lxml.de/installation.html#requirements
- https://github.com/alstr/todo-to-issue-action
- https://github.com/scitt-community/scitt-api-emulator
- https://scitt.io/components/enotary.html
- https://scitt.io/distributing-with-oci-scitt.html
- https://lists.spdx.org/g/Spdx-tech/message/4943
  - > Dick Brooks: MO, the SPDX Package Supplier is the same as Supplier Name within the NTIA minimum elements (attached). Three roles are coming into view on the IETF SCITT initiative:
Supplier (original creator of the software product/component). Authorized Signing Party (A party that is authorized to sign an artifact). Distributor  (app stores, package managers, GitHub). A single entity may serve in all 3 roles, or each role may be served by separate entities. There’s also another role, “Vendor” – this would be System Integrators that are delivering software products as part of an all-inclusive solution for a consumer. The consumer role is always present. This is all still very much under discussion within SCITT.
  - > ![some-kind-of-list-of-maybe-spdx-related](https://user-images.githubusercontent.com/5950433/215008561-34a97cb8-b70b-4bc8-8b2f-8af92ed3082b.jpeg)
- https://projects.laion.ai/Open-Assistant/docs/data/schemas
  - This looks similar to what we're doing
  - https://docs.google.com/presentation/d/1iaX_nxasVWlvPiSNs0cllR9L_1neZq0RJxd6MFEalUY/edit#slide=id.g1c26e0a54b8_0_965
    - This looks very similar
  - https://github.com/LAION-AI/Open-Assistant/issues/883#issuecomment-1405830706
    - Reached out
    - > We've been looking at AI ethics with a similar project, Alice, the Open Architecture: https://github.com/w3c/cogai/pull/47
      >
      > The approach we're taking is to leverage data flow based plugins so that end-users can overlay their own "ethics" (whatever that might mean to them) onto upstream flows. The hope is, this combined with a review system facilitated by software vulnerability semantics as a backbone will enable end-users to see the downstream effects their ethical overlays have on the fulfilment of their requests.
      >
      > - Related
      >   - https://mailarchive.ietf.org/arch/msg/scitt/sVaDAFfMSB7X_jjEBCZ1xt7vZJE/
      >     - > We additionally want to be able to do this without invalidating *future* builds once things are back under control.
- How to open the definition of an entrypoint loadable class
  - [![use-the-source](https://img.shields.io/badge/use%20the-source-blueviolet)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#use-the-source-)

```console
$ vim $(git grep -i mysql | grep @entrypoint | sed -e 's/:.*//g')
```

- https://stackoverflow.com/questions/27951603/git-command-to-show-branch-upstream
- https://git-scm.com/docs/pretty-formats

```console
$ tee schema/image/container/build/dffml.json <<EOF
{
    "\$schema": "https://github.com/intel/dffml/raw/main/schema/image/container/build/0.0.1.schema.json",
    "include": [
        {

            "branch": "$(git name-rev @{u} | awk '{print $2}')",
            "commit": "$(git log -n 1 --format=%H)",
            "dockerfile": "Dockerfile",
            "image_name": "$(git remote -v | grep '(push)' | head -n 1 | awk '{print $2}' | sed -e 's/.*\///' | sed -e 's/\.git//g' | sed -e 's/\./-/g')",
            "owner": "$(git remote -v | grep '(push)' | head -n 1 | awk '{print $2}' | sed -e 's/.*github.com\///' | sed -e 's/\/.*//' | sed -e 's/\.git//g' | sed -e 's/\./-/g')",
            "repository": "$(git remote -v | grep '(push)' | head -n 1 | awk '{print $2}' | sed -e 's/.*\///' | sed -e 's/\.git//g')"
        }
    ]
}
EOF
```

```json
{
    "$schema": "https://github.com/intel/dffml/raw/main/schema/image/container/build/0.0.1.schema.json",
    "include": [
        {

            "branch": "alice",
            "commit": "38880e3a873d252bd15e00c8d10509fee32f597a",
            "dockerfile": "Dockerfile",
            "image_name": "dffml",
            "owner": "pdxjohnny",
            "repository": "dffml"
        }
    ]
}
```

```console
$ cat dffml.json | python -c "import sys, pathlib, json, yaml; print(yaml.dump(json.load(sys.stdin)))"
$schema: https://github.com/intel/dffml/raw/main/schema/image/container/build/0.0.1.schema.json
include:
- branch: alice
  commit: 38880e3a873d252bd15e00c8d10509fee32f597a
  dockerfile: Dockerfile
  image_name: dffml
  owner: pdxjohnny
  repository: dffml
```

- https://datatracker.ietf.org/doc/draft-bweeks-acme-device-attest/
- https://github.com/opencomputeproject/onie
  - > The Open Network Install Environment (ONIE) defines an open “install environment” for modern networking hardware. ONIE enables an open networking hardware ecosystem where end users have a choice among different network operating systems.
- https://github.com/anteater/anteater
  - Abstract version of our test_ci.py
- JSON-LD and RDF https://earthstream.social/@mprorock/109756220250660052
  - Context awareness is important
  - https://github.com/intel/dffml/blob/alice/docs/arch/0010-Schema.rst
  - https://arxiv.org/pdf/2210.03945.pdf
    - Understanding HTML with Large Language Models
  - https://arxiv.org/pdf/2209.15003.pdf
    - COMPOSITIONAL SEMANTIC PARSING WITH LARGE LANGUAGE MODELS
- https://mailarchive.ietf.org/arch/msg/scitt/sVaDAFfMSB7X_jjEBCZ1xt7vZJE/
  - > We additionally want to be able to do this without invalidating *future* builds once things are back under control.
- https://github.com/w3c-ccg/traceability-interop/tree/main/docs/tutorials
- https://github.com/w3c/websub/tree/master/implementation-reports
- http://pubsubhubbub.appspot.com/
- https://websub.rocks/publisher
- https://github.com/mastodon/mastodon/issues/17134#issuecomment-994211542
  - ActivityPub Follow is next gen websub
- https://duckduckgo.com/?q=ActivityPub+Follow+site%3Agithub.com&ia=web
  - https://github.com/jakelazaroff/activitypub-starter-kit
    - MIT

```console
$ PORT=8000 ADMIN_USERNAME=alice ADMIN_PASSWORD=alice npm run dev
$ curl -u alice:alice -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/create
$ curl -u alice:alice -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/follow/http://localhost:7000/bob
```

- Follow failing currently, 404s, not sure why
- If this works it will be perfect for the downstream triggers
  - Note as registry content address
    - Even metric manifest scratch works with this pattern
- Overlay to set port for own actor

```patch
diff --git a/src/index.ts b/src/index.ts
index 676cc41..ffdabfe 100644
--- a/src/index.ts
+++ b/src/index.ts
@@ -7,7 +7,7 @@ import { admin } from "./admin.js";

 const app = express();

-app.set("actor", `https://${HOSTNAME}/${ACCOUNT}`);
+app.set("actor", `http://${HOSTNAME}:${PORT}/${ACCOUNT}`);

 app.use(
   express.text({ type: ["application/json", "application/activity+json"] })
```

- Apply overlay: Need to use http for now
  - Overlay application orchestrator: shell pipeline, grep and sed

```console
$ git grep https -- src/ | grep -v .org
src/activitypub.ts:        id: `https://${HOSTNAME}/${crypto.randomUUID()}`,
src/admin.ts:  const uri = `https://${HOSTNAME}/@${crypto.randomUUID()}`;
src/index.ts:app.set("actor", `https://${HOSTNAME}/${ACCOUNT}`);
src/request.ts:  const fragment = actor.inbox.replace("https://" + url.hostname, "");
$ sed -e 's/https:\/\/${HOSTNAME}/http:\/\/\${HOSTNAME}:\${PORT}/g' -e 's/https:\/\/" + url.hostname/http:\/\/" + url.hostname/g' $(git grep https -- src/ | grep -v .org | sed -e 's/:.*//g') | grep http | grep -v .org
$ sed -i -e 's/https:\/\/${HOSTNAME}/http:\/\/\${HOSTNAME}:\${PORT}/g' -e 's/https:\/\/" + url.hostname/http:\/\/" + url.hostname/g' $(git grep https -- src/ | grep -v .org | sed -e 's/:.*//g')
$ git diff
```

- Resulting dataflows after dynamic overlay application

```diff
diff --git a/src/activitypub.ts b/src/activitypub.ts
index 11cce94..1b9dc4b 100644
--- a/src/activitypub.ts
+++ b/src/activitypub.ts
@@ -63,7 +63,7 @@ activitypub.post("/:actor/inbox", async (req, res) => {
     case "Follow": {
       await send(actor, body.actor, {
         "@context": "https://www.w3.org/ns/activitystreams",
-        id: `https://${HOSTNAME}/${crypto.randomUUID()}`,
+        id: `http://${HOSTNAME}/${crypto.randomUUID()}`,
         type: "Accept",
         actor,
         object: body,
diff --git a/src/admin.ts b/src/admin.ts
index 024ddcd..ca00c46 100644
--- a/src/admin.ts
+++ b/src/admin.ts
@@ -4,7 +4,7 @@ import { is, omit, type } from "superstruct";
 import { Router } from "express";
 import basicAuth from "express-basic-auth";

-import { ADMIN_PASSWORD, ADMIN_USERNAME, HOSTNAME } from "./env.js";
+import { ADMIN_PASSWORD, ADMIN_USERNAME, HOSTNAME, PORT } from "./env.js";
 import {
   createFollowing,
   createPost,
@@ -61,16 +61,21 @@ admin.post("/create", async (req, res) => {
   return res.sendStatus(204);
 });

-admin.post("/follow/:actor", async (req, res) => {
-  const actor: string = req.app.get("actor");

-  const object = req.params.actor;
-  const uri = `https://${HOSTNAME}/@${crypto.randomUUID()}`;
-  await send(actor, object, {
+admin.post("/follow/:actor/:hostname/:port/:proto", async (req, res) => {
+  const our_actor: string = req.app.get("actor");
+  console.log(`Follow endpoint, our actor: ${our_actor}`)
+
+  const { proto, hostname, port, actor } = req.params;
+  const object = `${proto}://${hostname}:${port}/${actor}`;
+  console.log(`Follow endpoint, object: ${object}`)
+  const uri = `http://${HOSTNAME}:${PORT}/@${crypto.randomUUID()}`;
+  console.log(`Follow endpoint, uri: ${uri}`)
+  await send(our_actor, object, {
     "@context": "https://www.w3.org/ns/activitystreams",
     id: uri,
     type: "Follow",
-    actor,
+    actor: our_actor,
     object,
   });

@@ -78,7 +83,7 @@ admin.post("/follow/:actor", async (req, res) => {
   res.sendStatus(204);
 });

-admin.delete("/follow/:actor", async (req, res) => {
+admin.delete("/follow/:actor/:hostname", async (req, res) => {
   const actor: string = req.app.get("actor");

   const object = req.params.actor;
diff --git a/src/request.ts b/src/request.ts
index 462bcbd..3665f71 100644
--- a/src/request.ts
+++ b/src/request.ts
@@ -31,7 +31,7 @@ export async function send(sender: string, recipient: string, message: object) {
   const url = new URL(recipient);

   const actor = await fetchActor(recipient);
-  const fragment = actor.inbox.replace("https://" + url.hostname, "");
+  const fragment = actor.inbox.replace("http://" + url.hostname, "");
   const body = JSON.stringify(message);
   const digest = crypto.createHash("sha256").update(body).digest("base64");
   const d = new Date();
```

- YES! We got a meaningful error

```console
$ PORT=8000 npm run dev

> dumbo@1.0.0 dev
> ts-node --esm src/index.ts

Dumbo listening on port 8000…
Follow endpoint, our actor: http://localhost:8000/alice
Follow endpoint, object: https://localhost:7000/bob
Follow endpoint, uri: http://localhost:8000/@d935a0cc-43a2-4d96-8eaf-b7dad202d836
file:///home/pdxjohnny/activitypub-starter-kit-alice/node_modules/node-fetch/src/index.js:108
                        reject(new FetchError(`request to ${request.url} failed, reason: ${error.message}`, 'system', error));
          ^
FetchError: request to https://localhost:7000/bob failed, reason: connect ECONNREFUSED 127.0.0.1:7000
    at ClientRequest.<anonymous> (file:///home/pdxjohnny/activitypub-starter-kit-alice/node_modules/node-fetch/src/index.js:108:11)
    at ClientRequest.emit (node:events:513:28)
    at ClientRequest.emit (node:domain:489:12)
    at TLSSocket.socketErrorListener (node:_http_client:496:9)
    at TLSSocket.emit (node:events:513:28)
    at TLSSocket.emit (node:domain:489:12)
    at emitErrorNT (node:internal/streams/destroy:151:8)
    at emitErrorCloseNT (node:internal/streams/destroy:116:3)
    at processTicksAndRejections (node:internal/process/task_queues:82:21) {
  type: 'system',
  errno: 'ECONNREFUSED',
  code: 'ECONNREFUSED',
  erroredSysCall: 'connect'
}
```

- Try following self

```console
$ PORT=8000 npm run --watch dev

> dumbo@1.0.0 dev
> ts-node --esm src/index.ts

Dumbo listening on port 8000…
Follow endpoint, our actor: http://localhost:8000/alice
Follow endpoint, object: http://localhost:8000/alice
Follow endpoint, uri: http://localhost:8000/@b7ec4963-659b-46bc-805a-375aa71bb96f
GET /alice 200 1412 - 2.391 ms
GET /alice 200 1412 - 0.580 ms
Error: Invalid request signature.
    at verify (file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:126:24)
    at processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/src/activitypub.ts:51:12
POST /alice/inbox 401 12 - 97.576 ms
file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:64
    throw new Error(res.statusText + ": " + (await res.text()));
          ^
Error: Unauthorized: Unauthorized
    at send (file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:64:11)
    at processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/src/admin.ts:74:3
```

- Generate key
  - https://github.com/jakelazaroff/activitypub-starter-kit#deploying-to-production
  - https://stackoverflow.com/questions/44474516/how-to-create-public-and-private-key-with-openssl/44474607#44474607

```console
$ openssl genrsa -out keypair.pem 4096
$ openssl rsa -in keypair.pem -pubout -out publickey.crt
$ openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in keypair.pem -out pkcs8.key
```

```console
$ PORT=8000 ADMIN_USERNAME=alice ADMIN_PASSWORD=alice PUBLIC_KEY=publickey.crt PRIVATE_KEY=keypair.pem npm run dev

> dumbo@1.0.0 dev
> ts-node --esm src/index.ts

Dumbo listening on port 8000…
POST /admin/follow/alice/localhost/8000/http 401 0 - 1.020 ms
POST /admin/create 204 - - 16.262 ms
Follow endpoint, our actor: http://localhost:8000/alice
Follow endpoint, object: http://localhost:8000/alice
Follow endpoint, uri: http://localhost:8000/@1367d6ef-78a2-4b26-a7b2-4ca0e7a79989
GET /alice 200 611 - 1.014 ms
Error: error:1E08010C:DECODER routines::unsupported
    at Object.createPrivateKey (node:internal/crypto/keys:620:12)
    at send (file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:39:22)
    at processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/src/admin.ts:74:3 {
  library: 'DECODER routines',
  reason: 'unsupported',
  code: 'ERR_OSSL_UNSUPPORTED'
}
```

- Create post

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
$ curl -u alice:alice -X POST --header "Content-Type: application/json" --data @post.json -v http://localhost:8000/admin/create
$ curl -u alice:alice -X POST -v http://localhost:8000/admin/follow/alice/localhost/8000/http
```

- ERR_OSSL_UNSUPPORTED failure
- `--openssl-legacy-provider` did not help (compile then ran)
  - https://github.com/auth0/node-jsonwebtoken/issues/846#issuecomment-1361667054
  - https://stackoverflow.com/questions/69962209/what-is-openssl-legacy-provider-in-node-js-v17
- https://nodejs.org/download/release/latest-v16.x/
  - Downgraded from nodejs 18 to 16

```console
$ PORT=8000 ADMIN_USERNAME=alice ADMIN_PASSWORD=alice PUBLIC_KEY=publickey.crt PRIVATE_KEY=keypair.pem npm run dev

> dumbo@1.0.0 dev
> ts-node --esm src/index.ts

Dumbo listening on port 8000…
Follow endpoint, our actor: http://localhost:8000/alice
Follow endpoint, object: http://localhost:8000/alice
Follow endpoint, uri: http://localhost:8000/@1bba04e4-ca3d-4f9c-84c0-924f7ee5d796
GET /alice 200 611 - 3.711 ms
Error: error:0909006C:PEM routines:get_name:no start line
    at Object.createPrivateKey (node:internal/crypto/keys:620:12)
    at send (file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:39:22)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/src/admin.ts:74:3 {
  library: 'PEM routines',
  function: 'get_name',
  reason: 'no start line',
  code: 'ERR_OSSL_PEM_NO_START_LINE'
}
```

- Perhaps a missformatted key?
  - Looks like there's a PEM start lin to me, although sometimes
    these things need to be find replaced from RSA to PEM ENCODED

```console
$ cat keypair.pem
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
```

- nodejs docs
  - crypto.createPrivateKey(key)#
    - https://nodejs.org/api/crypto.html#cryptocreateprivatekeykey
    - `key <Object> | <string> | <ArrayBuffer> | <Buffer> | <TypedArray> | <DataView>`
      - `key: <string> | <ArrayBuffer> | <Buffer> | <TypedArray> | <DataView> | <Object>`
        - The key material, either in PEM, DER, or JWK format.

```console
$ PORT=8000 ADMIN_USERNAME=alice ADMIN_PASSWORD=alice PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run dev
Dumbo listening on port 8000…
Follow endpoint, our actor: http://localhost:8000/alice
Follow endpoint, object: http://localhost:8000/alice
Follow endpoint, uri: http://localhost:8000/@3eca6f29-414e-449e-9543-19f718314593
GET /alice 200 1410 - 3.044 ms
GET /alice 200 1410 - 0.618 ms
Error: Invalid request signature.
    at verify (file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:128:24)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/src/activitypub.ts:51:12
POST /alice/inbox 401 12 - 111.891 ms
file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:66
    throw new Error(res.statusText + ": " + (await res.text()));
          ^
Error: Unauthorized: Unauthorized
    at send (file:///home/pdxjohnny/activitypub-starter-kit-alice/src/request.ts:66:11)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/src/admin.ts:74:3
```

- Update `fragment` on `activitypub.send()`

```patch
diff --git a/src/request.ts b/src/request.ts
index 462bcbd..cad57a7 100644
--- a/src/request.ts
+++ b/src/request.ts
@@ -31,7 +31,7 @@ export async function send(sender: string, recipient: string, message: object) {
   const url = new URL(recipient);
 
   const actor = await fetchActor(recipient);
-  const fragment = actor.inbox.replace("https://" + url.hostname, "");
+  const fragment = url.pathname + "/inbox";
   const body = JSON.stringify(message);
   const digest = crypto.createHash("sha256").update(body).digest("base64");
   const d = new Date();
@@ -46,6 +46,7 @@ export async function send(sender: string, recipient: string, message: object) {
   const signature = crypto
     .sign("sha256", Buffer.from(data), key)
     .toString("base64");
+  console.log(`crypto.sign("sha256", data: ${data}, key: ${key}, signature: ${signature})`);
 
   const res = await fetch(actor.inbox, {
     method: "POST",
@@ -119,6 +120,7 @@ export async function verify(req: Request): Promise<string> {
       return `${header}: ${req.get(header)}`;
     })
     .join("\n");
+  console.log(`crypto.verify("sha256", data: ${comparison}, key: ${key}, signature: ${included.signature})`);
   const data = Buffer.from(comparison);
 
   // verify the signature against the headers using the actor's public key

```

- Previous: https://asciinema.org/a/537643
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0002_shes_ariving_when.md#scitt-api-emulator-spin-up
    - We're going to put content addresses in both places, we'll then use the registry and proxies to serve content out of it ORAS.land style.
      - Proxies can handle scratch image with manifest to memetype for example to jpeg or anything.
    - SCITT will be for the receipts of ActivityPub messages (TCP handshake style)

```console
$ dffml service dev export alice.cli:ALICE_COLLECTOR_DATAFLOW
```

- https://github.com/jakelazaroff/activitypub-starter-kit/pull/1
  - We've now successfully posted content and content addresses to SCITT and via ActivityPub. Forming the basis for our Thought Communication Protocol three way handshake. We've used the  SHA384 sum of living threat model collector dataflow as a stand in for the content address whose content will exist in https://oras.land. ActivityPub and SCITT enable us to close the loop of vuln analysis and remediation.
    - https://github.com/intel/dffml/issues/51#issuecomment-1172615272
      - Related to distributed locking and Thought Communication Protocol three way handshake
  - Thank you Jake Lazaroff for https://github.com/jakelazaroff/activitypub-starter-kit!

[![asciicast](https://asciinema.org/a/554864.svg)](https://asciinema.org/a/554864)

- Tested with https://localhost.run based HTTPS

```console
$ ssh -R 80:localhost:8000 nokey@localhost.run
```

```console
$ curl -u alice:alice -X POST -v https://9e2336258d686a.lhr.life/admin/follow/alice/9e2336258d686a.lhr.life/443/https
$ curl -u alice:alice -X POST --header "Content-Type: application/json" --data @post.json -v https://9e2336258d686a.lhr.life/admin/create
```

- https://asciinema.org/a/554872
- https://asciinema.org/a/554875
- TODO
  - [ ] Downstream validation via activitypub, regisrty, cve bin tool and trivy for sbom vex scitt for registry recipts
  - [ ] Status update video