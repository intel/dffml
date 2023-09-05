## 2023-03-31 @pdxjohnny Engineering Logs

- https://phoenixnap.com/kb/kubernetes-kind
- Future
  - New events into DMZ KCP via ingress plugin
- https://github.com/intel/dffml/tree/alice/examples/tutorials/rolling_alice/transparency_service/kubernetes_dataflow_policy_engine
- https://github.com/pixelfed/pixelfed/blob/dev/.github/workflows/build-docker.yml
  - https://didme.me
- https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/using-openid-connect-with-reusable-workflows#defining-the-trust-conditions
- I really don't like relying on `docker`, but here we are...
  - https://kind.sigs.k8s.io/docs/user/quick-start/
- KCP in GUAC?
- https://github.com/EC-CS-528-BU-Cloud-Computing/smart-distributed-vulnerability-management/commits/main
  - `FROM` rebuild chain resolver potential base
  - https://github.com/EC-CS-528-BU-Cloud-Computing/smart-distributed-vulnerability-management/issues/12
  - https://github.com/EC-CS-528-BU-Cloud-Computing/smart-distributed-vulnerability-management/blob/8c88acc1701c68335b649fadbd1d77fa0f5d6d08/debian.json
- asciicast for policy engine docs
  - Orchestrator
    - https://segfault.net
      - https://thc.org

```console
$ mkdir -p ~/asciinema
$ export REC_HOSTNAME="segfault.net"; export REC_TITLE="IETF SCITT: API Emulator: Registration Policies: Simple decoupled file based policy engine"; asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "sshpass -p segfault ssh -t -o 'StrictHostkeyChecking=no' root@segfault.net tmux" "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).ndjson"
$ asciinema upload /home/pdxjohnny/asciinema/segfault.net-rec-2023-03-31T15:19:52-07:00.ndjson
```

- Full demo below

```console
$ python -m pip install -U pip setuptools wheel
$ echo "Clone SCITT API emulator at pinned to pdxjohnny policy_engine branch HEAD as of 2023-03-31 09:54-7:00" \
  && set -x \
  && export TARGET_DIR=scitt-api-emulator \
  && export TARGET_REPO_URL=https://github.com/scitt-community/scitt-api-emulator \
  && export TARGET_COMMIT=2787820abf3fa4701bc46a9629cd98d11254fbe6 \
  && mkdir -p "${TARGET_DIR}" \
  && cd "${TARGET_DIR}" \
  && git init \
  && git remote add origin "${TARGET_REPO_URL}" \
  && git fetch origin "${TARGET_COMMIT}" --depth 1 \
  && git reset --hard "${TARGET_COMMIT}" \
  && python -m pip install \
    --no-cache \
    -e . \
    -r dev-requirements.txt \
  && cd -
$ echo 'export PATH="${PATH}:${HOME}/.local/bin"' | tee -a ~/.bashrc
$ echo 'export PATH="${PATH}:${HOME}/.local/node_modules/.bin"' | tee -a ~/.bashrc
$ . ~/.bashrc
$ (cd ~/.local && npm install nodemon)
$ cat > enforce_policy.py <<'EOF'
import os
import sys
import pathlib

cose_path = pathlib.Path(sys.argv[-1])
policy_action_path = cose_path.with_suffix(".policy." + os.environ["POLICY_ACTION"].lower())
policy_action_path.write_text("")
Simple drop rule based on claim content blocklist.
EOF
$ cat > is_on_blocklist.py <<'EOF'
import os
import sys
import json

import cbor2
import pycose
from pycose.messages import CoseMessage, Sign1Message

from scitt_emulator.scitt import ClaimInvalidError, COSE_Headers_Issuer

BLOCKLIST_DEFAULT = [
    "did:web:example.com",
]
BLOCKLIST_DEFAULT_JSON = json.dumps(BLOCKLIST_DEFAULT)
BLOCKLIST = json.loads(os.environ.get("BLOCKLIST", BLOCKLIST_DEFAULT_JSON))

claim = sys.stdin.buffer.read()

msg = CoseMessage.decode(claim)

if pycose.headers.ContentType not in msg.phdr:
    raise ClaimInvalidError(
        "Claim does not have a content type header parameter"
    )
if COSE_Headers_Issuer not in msg.phdr:
    raise ClaimInvalidError("Claim does not have an issuer header parameter")

if msg.phdr[COSE_Headers_Issuer] not in BLOCKLIST:
    sys.exit(1)

# EXIT_SUCCESS == MUST block. In case of thrown errors/exceptions.
EOF
$ nodemon -e .cose --exec 'find workspace/storage/operations -name \*.cose -exec nohup sh -xc "echo {} && (python3 is_on_blocklist.py < {} && POLICY_ACTION=denied python3 enforce_policy.py {}) || POLICY_ACTION=insert python3 enforce_policy.py {}" \;' &
$ mkdir -p "workspace/storage/operations/"
$ timeout 1s scitt-emulator server --workspace workspace/ --tree-alg CCF --use-lro
$ echo "$(cat workspace/service_parameters.json)" \
    | jq '.insertPolicy = "external"' \
    | tee workspace/service_parameters.json.new \
    && mv workspace/service_parameters.json.new workspace/service_parameters.json
$ scitt-emulator server --workspace workspace/ --tree-alg CCF --use-lro &
$ scitt-emulator client create-claim --issuer did:web:example.com --content-type application/json --payload '{"sun": "yellow"}' --out claim.cose
$ scitt-emulator client submit-claim --claim claim.cose --out claim.receipt.cbor
... denied ...
$ scitt-emulator client create-claim --issuer did:web:example.org --content-type application/json --payload '{"sun": "yellow"}' --out claim.cose
$ scitt-emulator client submit-claim --claim claim.cose --out claim.receipt.cbor
$ echo $?
0 (aka inserted)
```

[![asciicast-of-simple-decoupled-file-based-policy-engine](https://asciinema.org/a/572766.svg)](https://asciinema.org/a/572766)

- Sketch of policy engine via loosly coupled file based policy as code cypher query chain follows
- https://hub.docker.com/_/neo4j/

```console
$ docker run --publish=7474:7474 --publish=7687:7687 --env=NEO4J_AUTH=none "docker.io/library/neo4j:5.6.0"
```

- https://github.com/vercel/ncc/issues/892
  - Note: Be nice to open source maintainers when you file bugs, positive sentiment
  - https://asciinema.org/a/572799
    - No dice, also tried with https://github.com/vercel/pkg but raised MODULE_NOT_FOUND on run of `index-18-node`
- https://github.com/updatecli/updatecli-action/pull/100
- https://github.com/updatecli/updatecli
  - Declarative version of what we are looking for in terms of dependency updating / `FROM` rebuild flows. We can make these on event stream trigger via issueops or federated `issue.json` events.

![chaos-for-the-chaos-god](https://user-images.githubusercontent.com/5950433/220794351-4611804a-ac72-47aa-8954-cdb3c10d6a5b.jpg)

- https://www.updatecli.io/docs/automate/jenkins/
- https://www.updatecli.io/docs/automate/github_action/
  - A repo/workflow pair manages the KCP CRDs which run the forge
  - We hook this up to the SCITT receipt issued event stream
    - We feed this all the pinned values referenced within content or content addressed resolved manifest instance within claim.
    - Issue container rebuilds via SBOM analysis for FROM chains.
    - Eventing should cause cascading pinning requests and auto update on policy approval per insert policy.
      - Optionally allow for overlays within claims JSON / CBOR / content
        - MUST apply context aware (optionally adaptive) sandboxing within overlay application process when executed by policy engine.
- https://github.com/updatecli/updatecli/issues/1252
  - `await close(^)`
- https://github.com/vercel
- https://turbo.build/repo/docs/getting-started/add-to-project
- https://turbo.build/repo/docs/core-concepts/monorepos/running-tasks#turborepo-can-multitask
  - Rust based workflow execution, this may fit with aurae nicely
  - https://turbo.build/repo/docs/core-concepts/monorepos/running-tasks#defining-a-pipeline
  - https://turbo.build/schema.json
    - Added to CI/CD Event Federation discussion
- https://www.electronjs.org/docs/latest/tutorial/testing-on-headless-ci
  - Nice xserver capture
- https://github.com/vercel/pkg
- Transparency logs form the basis for our reply/review system
  - This is needed for the alignment reward portion of the prioritizer
- https://docs.kcp.io/kcp/main/developers/using-kcp-as-a-library/
- GUAC -> Embedded KCP -> Alice Should I Contribute?
  - Next add cypher query of GUAC from Python via utils or operations and or sources
- [GUAC Design Doc](https://docs.google.com/document/d/1N5x0HErb-kmCPgG9M8TwBEOGIVU54clqp_X4KhtNJI8/edit#)
  - Graph Assembler, Graph Query Client, Entity Processor will all get receipts from SCITT
    - This way we have capture the chain of system contexts of thoughts. Policy engine on insert allow can kick off required flows via queries to GUAC or pushes to vcs+runners or IPVM or OA execution in Python, etc. via decoupled file based policy engine.
    - When GUAC goes to query we can then schedule for re-query on timer (responses to deadlines) or on event of data populated (SBOM of cypher query FROM rebuild chain, via analysis of SBOMs also added to GUAC with receipts from SCITT).
- https://docs.kcp.io/kcp/main/developers/writing-kcp-aware-controllers/
- The feedback loop between GUAC and SCITT plus federated SCITT events enables dynamic / behavioral analysis.
- Found ingestor as place of interest
- Found sigstore in there
  - Naturally we'll want to add support for SCITT, this must be the place
- Sigstore is seems must be using DSSE documents, whatever that means.
- SCITT uses COSE and CBOR
  - https://github.com/veraison/go-cose
  - https://github.com/veraison/go-cose/blob/99e66609571d0ad4fb9adfc778aed73fb7d55acb/example_test.go
  - CBOR Object Signing and Encryption (COSE): Structures and Process - RFC 9052
  - https://github.com/scitt-community/scitt-api-emulator/blob/a1a3001163611e02c51298e196b056f904ec81ca/postman/claim.cose


```console
$ ./neo4j-community-5.6.0/bin/neo4j console
Directories in use:
home:         /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0
config:       /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/conf
logs:         /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/logs
plugins:      /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/plugins
import:       /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/import
data:         /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/data
certificates: /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/certificates
licenses:     /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/licenses
run:          /tmp/tmp.5CSVHA9QjH/neo4j-community-5.6.0/run
Starting Neo4j.
2023-04-01 06:10:55.732+0000 INFO  Starting...
2023-04-01 06:10:56.102+0000 INFO  This instance is ServerId{b374a83c} (b374a83c-1b0c-4c3c-ab1c-68408611e6e5)
2023-04-01 06:10:56.672+0000 INFO  ======== Neo4j 5.6.0 ========
2023-04-01 06:10:57.505+0000 INFO  Bolt enabled on localhost:0.
2023-04-01 06:10:58.056+0000 INFO  Remote interface available at http://localhost:7474/
2023-04-01 06:10:58.058+0000 INFO  id: D575DD4192F9DF1B5099783C20CED2C04933852B21C43A5FA4F4C1D976C06C79
2023-04-01 06:10:58.059+0000 INFO  name: system
2023-04-01 06:10:58.059+0000 INFO  creationDate: 2023-04-01T04:14:07.939Z
2023-04-01 06:10:58.059+0000 INFO  Started.
```

- TODO
  - [ ] ~~Sleep~~
  - [x] Caffeine
  - [x] Disable tests on push to `alice` branch for now
    - Was hogging runners for docs changes
  - [x] [Example GitHub Action to run Python unittests](https://github.com/intel/project-example-for-python/commit/d62298b3e8b1a6c13df0bb3b9afafbc6193ac697)
  - [x] https://github.com/intel/project-example-for-python/issues/4
  - [x] Post SCITT API Emulator policy PR to mailing list
    - https://mailarchive.ietf.org/arch/msg/scitt/PwcesOR1txbHOIjMhMOt01YWDjo/
  - [ ] neo4j/bolt DFFML operations or source for import/export
    - https://asciinema.org/a/572802
  - [ ] DFFML op for wrapping notebooks
    - https://github.com/securefederatedai/openfl/blob/develop/openfl-tutorials/experimental/Vertical_FL/Workflow_Interface_VFL_Two_Party.ipynb
    - https://github.com/neo4j/graph-data-science-client/blob/main/examples/fastrp-and-knn.ipynb
    - https://github.com/neo4j/graph-data-science-client/blob/main/examples/load-data-via-graph-construction.ipynb
    - https://github.com/neo4j/graph-data-science-client/blob/main/examples/heterogeneous-node-classification-with-hashgnn.ipynb
  - [ ] SCITT instance whos policy makes it act as the OIDC notary proxy. A service that sits in front of an instance which issues claims based on valid OIDC and job_workflow_ref. The instance it submits claims to has the did:web or did:pwq or did:keri in its allowlist. The content address or content of the  receipt is submitted within the claim whose receipt is attached to the releaseasset.json as a property base32 encoded. Upon federation of the releaseasset receipt the receiver now knows upload auth checked out. Insert policy on federation event you create two receipts, first triahing incoming into cobtext localvthen reciot for inclustyoon in context local. thjis way we can traberse back but maintain payload
  - [ ] [Volume 0: Chapter 8: Transport Acquisition](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0008_transport_acquisition.md)
    - [ ] activitypub-starter-kit easier deployment
      - https://github.com/vercel/ncc