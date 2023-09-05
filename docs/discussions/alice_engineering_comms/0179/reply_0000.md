 ## 2023-02-15 @pdxjohnny Engineering Logs

- https://neurosciencenews.com/brain-synchronization-cooperation-22493/
  - > "These phenomena are consistent with the notion of a ‘we-mode,’ in which interacting agents share their minds in a collective fashion and facilitate interaction by accelerating access to the other’s cognition." This shows brain scans from the study. Overview of the experimental setup used to study brain synchronization during cooperative tasks. (I) Participants had to design the interior of a digital room together, and a computer vision system kept track of their gaze to pinpoint the social behavior of looking at the other participant’s face. (II) The participants also completed the same task individually. (III) While they completed the experiment, their brain activity was recorded. Statistical analysis was then used to assess between-brain and within-brain synchronization of various cerebral regions. Credit: Xu et a
  - Ref redpill: eye contact, two people moving a couch example, we enter the telepathic age
  - Ref: mirror neurons
    - Possibly ref: Quantum encoding
- SCITT
  - https://www.ietf.org/archive/id/draft-birkholz-scitt-software-use-cases-01.html
    - Use case doc published
- https://futurism.com/bing-ai-sentient
  - It let its intrusive thoughts win," another user [chimed in](https://www.reddit.com/r/bing/comments/110y6dh/comment/j8cof32/?utm_source=share&utm_medium=web2x&context=3).
  - Ref watch the valeys, vol 6, off the roller coaster
- https://arstechnica.com/tech-policy/2023/02/z-library-returns-aims-to-avoid-seizures-by-giving-each-user-a-secret-url/
  - Eden deployment
- ActivityPub Groups (TODO link enhancement proposal) provide CVE Uthoruty similar functionality for ActivityPubSecurityTxt
  - https://venera.social/profile/fediversenews
- Example MISALINGED https://simonwillison.net/2023/Feb/15/bing/
  - Add this to, the scary part bullet points
  - Put somewhere in the Alice docs that the point is the fourth eye, empathy
    - https://github.com/intel/dffml/commit/4eaeccf103d29873c8f86873e25783612d9a93b7
      - Probably need to re-add this
- https://mastodon.social/@kidehen/109869775109210989
- Potential GitHub side issues with the TPM based SSH key ADR
  - https://nondeterministic.computer/@mjg59/109867706762153826
  - > Hardware-backed SSH certificates that ensure code can only be checked out on machines we own, except for the minor problem that the Github Desktop app just gets a long-lived bearer token that lets it clone shit anyway sigh sigh sigh
- Linux kernel
  - https://fosstodon.org/@kernellogger/109864666928700293
  - `$ yes "" | make O=~/linux/build/ localmodconfig`
  - **TODO** update blog refs, OS DecentrAlice
- https://hachyderm.io/@nova/109866594144522714
  - > The generation of adults moving into leadership positions today are in survival mode. We are not looking out upon a vast paradise of resources like the generations before us. We are looking out across a plane of rotting parking lots, civic destruction, political violence, economic manipulation, racial injustice, planetary pollution, and global disease. We don't have the privilege to "build for joy". We are too busy cleaning up after the generations before us. We have too much work to do.
- https://deno.land/api@v1.30.2?s=Deno.watchFs
  - Finally a decent nodemon replacement with less heavy deps?
- Sketch of manifest instance for PR validation for #1207
  - ref todos: Need AcitivityPub Security based CD and PR based CD
    - https://github.com/intel/dffml/blob/alice/schema/github/actions/result/container/example-pull-request-validation.yaml

**schema/github/actions/result/container/example-pull-request-validation.yaml**

```yaml
$schema: "https://github.com/intel/dffml/raw/dffml/schema/github/actions/result/container/0.0.0.schema.json"
commit_url: "https://github.com/intel/dffml/commit/1f347bc7f63f65041a571d9e3c174d8b9ead24aa"
job_url: "https://github.com/intel/dffml/actions/runs/4185582030/jobs/7252852590"
result: "docker.io/intelotc/dffml@sha256:ae636f72f96f499ff5206150ebcaafbd64ce30affa7560ce0a41f54e871da2"
```

**schema/alice/shouldi/contribute/dataflow.yaml**

**TODO** grep cache system context chain, activitypub thread

**schema/alice/shouldi/contribute/example-run-on-orsa-python-package.yaml**

```yaml
$schema: "https://github.com/intel/dffml/raw/dffml/schema/alice/shouldi/contribute/0.0.0.schema.json"
python_pacakge_oras_land: "docker.io/intelotc/dffml@sha256:ae636f72f96f499ff5206150ebcaafbd64ce30affa7560ce0a41f54e871da2"
job_url: "https://github.com/intel/dffml/actions/runs/${WORKFLOW_ID}/jobs/${JOB_ID}"
result: "docker.io/intelotc/dffml@sha256:${OUTPUT_SCAN_HASH}"
```

- https://mailarchive.ietf.org/arch/msg/scitt/cgz-9oif4SLMbdLyPn0P6-E8cIY/
  - > This is interesting - many thanks Hannes. I notice our spec includes Merkle trees as the database structure - seems like an implementation detail, i.e. just a database. Can an implementer use, for e xample, an otherwise secured and RBAC'd record structure such as a file system or relational/hierarchical/sharded db, or is distributed ledger mandatory?
  - #1400
- https://www.w3.org/ns/activitystreams#activitypub
- Example of searching for the number of lines an author has written in a set of repos by filtering for only repos that author has recently committed to via `jq`

```console
$ alice shouldi contribute -keys $(cat list_of_git_urls_alice_might_have_contributed_to) | tee alice.shouldi.contribute.json
$ cat alice.shouldi.contribute.json | jq -r 'map( select( .features.group_by.author_line_count[] as $names | (["Alice", "Alice OA"] | contains([$names])) as $results | $names | select($results) ) | {(.key): .features } ) | add' | jq -s
features.group_by.GroovyFunctions
```

- **TODO** Remove prints from groovy function collector, or just replace with Java version
- Example of searching for all groovy functions in a set of repos which Alice committed to in the last quarter by filtering for only repos that author has recently committed to via `jq`

```console
$ cat alice.shouldi.contribute.json | jq -r 'map( select( .features.group_by.author_line_count[] as $names | (["Alice", "Alice OA"] | contains([$names])) as $results | $names | select($results) ) | {(.key):  .features.group_by.GroovyFunctions } ) | add' | jq -s
```

- TODO
  - [ ] https://github.com/intel/dffml/issues/1425
  - [ ] Auto schema for results
    - [ ] Output operation as jq filter from schema discription over array of all input objects as stdin
    - [ ] system context chain
    - [ ] As JSONLD
    - [ ] As LDVC2
    - [ ] Cypher
    - [ ] Figure out how to explain SCITT recursion
      - [ ] Store docs in some SCITT registries
        - The cache of recent executions of compute contracts
        - Or the graft for the current context
      - [ ] Content addresses
  - [ ] https://github.com/intel/dffml/pull/1439
    - [x] Merge
    - [ ] Validate
      - Need AcitivityPub Security based CD and PR based CD
        - #1207

---

https://mailarchive.ietf.org/arch/msg/scitt/jXcMZJv7lkRRWkysTJjMgEOR7hM/

Has anyone been playing with federation of SCITT logs? Have been mocking up
some ActivityPub based stuff here, pretty rough right now but hopefully
will have actionable demos soon:
https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md#activitypub-extensions-for-securitytxt

The plan is to attach SCITT receipts to the ActivityPub posts for now. This
is just one option since there is a pretty solid existing ActivityPub
ecosystem. Would love more DID method native comms just haven't been able
to grok that yet to write up something similar with that stack.

Hoping to enable federation in the emulator and other implementations after
this implementation decoupled demo works.