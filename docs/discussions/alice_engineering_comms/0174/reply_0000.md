## 2023-02-10 @pdxjohnny Engineering Logs

- Doing More with Less: Orchestrating Serverless Applications without an Orchestrator
  - [David H. Liu](http://www.cs.princeton.edu/~hl7/), Shadi Noghabi, Sebastian Burckhardt, [Amit Levy](http://amitlevy.com/).
  - Proc. 20th Symposium on Networked Systems Design and Implementation (NSDI ‘23), Boston, MA
  - https://www.amitlevy.com/papers/2023-nsdi-unum.pdf
  - Sounds aligned to OCAP work from ActivityPub maintainers and Ariadne (Chainguard P.E.)
- https://github.com/samim23/polymath
- https://motion-canvas.github.io/
  - https://motion-canvas.github.io/docs/flow
  - We may just have found our UI side for new Input events, we need to fix #837
- https://github.com/acheong08/EdgeGPT
  - Bingo

```console
$ rm -f db/database.sqjlite3; ssh -R 80:localhost:8000 nokey@localhost.run 2>&1 | grep 'tunneled with tls termination' | awk '{print $1}' | xargs -l -I '{}' -- sh -c 'echo "{}" | tee ../fdqn; PROTO=https FDQN=$(cat ../fdqn) WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start'
```

- https://github.com/testifysec/witness
- https://github.com/testifysec/witness/blob/main/docs/witness_run.md
- https://github.com/testifysec/archivista

```console
$ gh api --jq .content https://api.github.com/repos/intel/dffml/contents/scripts/alice_shouldi_contribute.Dockerfile | base64 -d | docker build --build-arg=GH_ACCESS_TOKEN=$(grep oauth_token < ~/.config/gh/hosts.yml | sed -e 's/    oauth_token: //g') --build-arg=REPO_URL=https://github.com/intel/dffml -f - -t scan-results-of-intel-dffml /dev/null
$ docker save scan-results-of-intel-dffml | tar --extract --to-stdout --wildcards --no-anchored 'layer.tar' | tar --extract --to-stdout  --wildcards --no-anchored 'result.yaml'
```

- Have been looking at a methodology around communication of transparency log entries to enable organizations to collaboratively contribute to trust graphs, and allow grafting off of trust chains for walled garden usage with added org policy flavor [WIP: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/de2b016b37d6762fba9f5b1bcde96324c67ce25e/openssf_metrics.md#activitypub-extensions-for-securitytxt)⁠
- `grep` and `awk` had to be unbuffered

```console
$ npm run build
$ rm -f db/database.sqjlite3; ssh -R 80:localhost:8000 nokey@localhost.run 2>&1 | grep --line-buffered 'tunneled with tls termination' | awk -W interactive '{print $1}' | xargs -l -I '{}' -- sh -c 'reset; echo "{}"; PROTO=https FDQN="{}" WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run start' &
958c0017e28b96.lhr.life

> dumbo@1.0.0 start
> node build/index.js

Dumbo listening on port 8000…
Data to sign (request-target): post /push/inbox
host: vcs.activitypub.securitytxt.dffml.chadig.com
date: Fri, 10 Feb 2023 23:19:54 GMT
digest: SHA-256=pDDFT32yzejspS7rWQvjoFxYTqM+3EuUEanBXgxV0c4=
GET /alice 200 1354 - 2.713 ms
file:///home/pdxjohnny/activitypub-starter-kit-alice/build/request.js:64
        throw new Error(res.statusText + ": " + (await res.text()));
              ^

Error: Unauthorized: Unauthorized
    at send (file:///home/pdxjohnny/activitypub-starter-kit-alice/build/request.js:64:15)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
    at async file:///home/pdxjohnny/activitypub-starter-kit-alice/build/admin.js:53:5
$ curl -ku alice:$(cat ../password) -X POST -v http://localhost:8000/admin/follow/push/vcs.activitypub.securitytxt.dffml.chadig.com/443/https
```

- Still getting Unauthorized
- Server side says Invalid request Signature, is the HOST off again?
- https://docs.openml.org/#runs
- From ActivityPub spec: https://www.w3.org/TR/activitypub/#delivery
  - > NOTE: Relationship to Linked Data Notifications
    - > While it is not required reading to understand this specification, it is worth noting that ActivityPub's targeting and delivery mechanism overlaps with the [Linked Data Notifications](https://www.w3.org/TR/ldn/) specification, and the two specifications may interoperably combined. In particular, the inbox property is the same between ActivityPub and Linked Data Notifications, and the targeting and delivery systems described in this document are supported by Linked Data Notifications. In addition to JSON-LD compacted ActivityStreams documents, Linked Data Notifications also supports a number of RDF serializations which are not required for ActivityPub implementations. However, ActivityPub implementations which wish to be more broadly compatible with Linked Data Notifications implementations may wish to support other RDF representations.
- https://github.com/tpm2-software/tpm2-tss/blob/master/SECURITY.md
- The goal is to align across static (.md) and runtime/dynamic (.txt) analysis in terms of declaring a way to get more info about a project, be it deployed or at rest. We're hoping to use this approach to facilitate CD for #1061 but there are other applications such as the above (which I guess is sort of also CD). Fundamentally it's about going from a static point to a dynamic auxiliary endpoint (ActivityPub) for out of band, lifecycle events to the application or source. Had been targeting the SSI stack via Decentralized Web Nodes, but the communities schedule kept slipping, and ActivityPub is fairly mature today, we can always recommend further Contact field options as other protocols mature.
- https://github.com/hyperledger-labs/weaver-dlt-interoperability#weaver-use-cases
  - > ![Weaver](https://github.com/hyperledger-labs/weaver-dlt-interoperability/raw/main/resources/images/weaver-support-table.png)
- Future
  - [ ] Event stream actor watching failed builds and re-trigger as appropriate