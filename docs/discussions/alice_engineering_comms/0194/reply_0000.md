## 2023-03-02 @pdxjohnny Engineering Logs

- Some example execution protection rings
  - System Management Mode
  - Root
  - Userspace
  - Sandboxed (v8)
- Wardly maps of hardware security strength as a commodity
  - TPM (most widely deployed)
    - https://www.tomsguide.com/news/billions-of-pcs-and-other-devices-vulnerable-to-newly-discovered-tpm-20-flaws
  - TXT
    - We frequently skip talking about this in this thread to avoid too much acronym soup, but TPMs are only good for https://github.com/intel/dffml/tree/alice/docs/arch/0007-A-GitHub-Public-Bey-and-TPM-Based-Supply-Chain-Security-Mitigation-Option.rst, aka tying keys into known hardware, without TXT (at least as we've been talking about them here). We just usually either talk about TPMs or TDX in this thread to illustrate the ends of the spectrum.
    - Trusted eXecution exTensions and Boot Guard combined with also a TPM (or a virtual equivalent) enables attested compute (by way of Secure Boot)
      - https://edk2-docs.gitbook.io/understanding-the-uefi-secure-boot-chain/secure_boot_chain_in_uefi/intel_boot_guard
      - https://www.chromium.org/developers/design-documents/tpm-usage/#attesting-device-mode
        - > [Attesting TPM-Protected Keys](https://www.chromium.org/developers/design-documents/tpm-usage/#attesting-tpm-protected-keys)
If an RSA private key has been generated in the TPM and has always been non-migratable, then the key may be certified by a key that has been verified as an Attestation Identity Key (AIK). No key, including any AIK, is certified unless the user or device-owner has consented to remote attestation of his or her device. A certified key credential gives very strong assurance that the key is protected by a Chrome Device TPM.
          > 
          > [Attesting Device Mode](https://www.chromium.org/developers/design-documents/tpm-usage/#attesting-device-mode)
At boot time, the read-only firmware extends TPM PCR0 with the status of the developer and recovery mode switches. The value of PCR0 can later be quoted using a key that has been verified as an Attestation Identity Key (AIK). The quote, in combination with the AIK credential, gives assurance that the reported PCR0 value is accurate. While assurance of the PCR0 value is very strong, assurance that this correctly reflects the device mode is weaker because of the reliance on read-only firmware to extend PCR0. It is nonetheless useful for reporting policy compliance. This PCR0 quote is not available outside of Chrome OS unless the user or device-owner has consented to remote attestation of the device.
  - SGX
  - TDX (least widely deployed)
- https://android.googlesource.com/platform/external/avb/+/master/README.md
- https://developer.android.com/training/articles/security-key-attestation
- https://ci.spdk.io/
  - ActivityPub integration
  - https://spdkci.intel.com/job/autotest-spdk-v23.01-LTS-vs-dpdk-main/152/
- https://berkeley-deep-learning.github.io/cs294-131-s19/
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/managing-a-branch-protection-rule
- https://github.com/opencontainers/image-spec/blob/main/manifest.md
  - Image command sequence to in-toto
  - Attestation as build arg
  - Still eventually #1426
- https://docs.github.com/en/actions/using-workflows/triggering-a-workflow#accessing-and-using-event-properties
  - Example of bots managing pinning
- Mirror of CI/CD actions can be executed with same manifest instance pattern for increased performance

```console
$ curl -fL https://vcs.activitypub.securitytxt.dffml.chadig.com/push/outbox/ > outbox@push@vcs.activitypub.securitytxt.dffml.chadig.com
$ jq .orderedItems[].id < outbox\@push\@vcs.activitypub.securitytxt.dffml.chadig.com | wc -l
3931
$ jq -r '.orderedItems[] | [{(.id): (.object.content)}] | .[] | add' < outbox\@push\@vcs.activitypub.securitytxt.dffml.chadig.com | jq -R --unbuffered '. as $line | try (fromjson | .) catch $line'
$ jq -r '.orderedItems[] | [{(.id): (.object.content)}] | .[] | add' < outbox\@push\@vcs.activitypub.securitytxt.dffml.chadig.com | jq -R --unbuffered '. as $line | try (fromjson | .workflow_job) catch $line'
$ jq -r '.orderedItems[] | [{(.id): (.object.content)}] | .[] | add' < outbox\@push\@vcs.activitypub.securitytxt.dffml.chadig.com | jq -c -R --unbuffered '. as $line | try (fromjson | .workflow_job) catch $line' | jq -s | python3 -c "import sys, pathlib, json, yaml; print(yaml.dump(json.load(sys.stdin)))"
```

```yaml
- check_run_url: https://api.github.com/repos/intel/dffml/check-runs/11733499326
  completed_at: '2023-03-03T04:30:59Z'
  conclusion: success
  created_at: '2023-03-03T03:58:07Z'
  head_branch: main
  head_sha: 4241b49975cf364b540fc0ad961cde58e2c89623
  html_url: https://github.com/intel/dffml/actions/runs/4320093439/jobs/7539975999
  id: 11733499326
  labels:
  - ubuntu-latest
  name: test (operations/nlp, 3.7)
  node_id: CR_kwDOCOlgGM8AAAACu179vg
  run_attempt: 1
  run_id: 4320093439
  run_url: https://api.github.com/repos/intel/dffml/actions/runs/4320093439
  runner_group_id: 2
  runner_group_name: GitHub Actions
  runner_id: 16
  runner_name: GitHub Actions 16
  started_at: '2023-03-03T04:26:41Z'
  status: completed
  steps:
  - completed_at: '2023-03-03T04:26:42.000Z'
    conclusion: success
    name: Set up job
    number: 1
    started_at: '2023-03-03T04:26:40.000Z'
    status: completed
  - completed_at: '2023-03-03T04:30:57.000Z'
    conclusion: success
    name: Complete job
    number: 21
    started_at: '2023-03-03T04:30:57.000Z'
    status: completed
  url: https://api.github.com/repos/intel/dffml/actions/jobs/11733499326
  workflow_name: Tests
```

- https://api.github.com/users/pdxjohnny/received_events
  - This looks like good rebroadcast material
- https://www.rabbitmq.com/cli.html
- We want to transform from ActivityPub incoming event (`@context|$schema` from node `inReply(d)To`) into event stream for alternate execution by worker nodes attached to context local message queue.
- Job URL -> hash -> mapping of lookup results from job URL as content address which resolves to results in oras.land
  - Just add the job URL hash as a tag and resolve via pulling that tag from the registry
- https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/rabbitmq.html
- https://docs.celeryq.dev/en/stable/tutorials/task-cookbook.html
- https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#using-celery-with-django
- We can enable ActivityPub as a database for celery and then we have parity between GitHub Actions as execution environment for ideation and prototyping compute. Then we have standard protocol and library to manage task queue execution based on inputs as schema/context inReplyTo events.
  - We can then run fully decoupled
- https://gvisor.dev/docs/tutorials/knative/
  - Wait we're supposed to be doing KCP almost forgot
- Run some live ones in https://github.com/cloudfoundry/korifi via `dffml-service-http`
  - Demo similar job URL hash as registry tag based addressing of results within registry
  - Enable sending of AcivityPub events directly (later) or indirectly via proxy nodes (first, activitypub starter kit.
- https://ci.spdk.io/results/autotest-nightly/builds/1935/archive/crypto-autotest/build.log

```yaml
- completed_at: '2023-03-03T04:30:59Z'
  conclusion: success
  created_at: '2023-03-03T03:58:07Z'
  head_sha: 4241b49975cf364b540fc0ad961cde58e2c89623
  html_url: https://ci.spdk.io.deployed.at.example.com/public_build/autotest-spdk-master-vs-dpdk-main_1754.html
  id: 1754
  labels:
  - list
  - of
  - overlays
  - on
  - dffml.overlays.alice.shouldi.contribute
  name: alice.shouldi.contribute
  status: completed
  steps:
  - completed_at: '2023-03-03T04:26:42.000Z'
    conclusion: success
    name: Run scan
    number: 1
    started_at: '2023-03-03T04:26:40.000Z'
    status: completed
  url: https://vcs.activitypub.securitytxt.dffml.chadig.com/push/posts/40aeeda3-6042-42ed-8e32-99eff9bd8ef4
  workflow_name: Alice Should I Contribute?
```

![knowledge-graphs-for-the-knowledge-god](https://user-images.githubusercontent.com/5950433/222981558-0b50593a-c83f-4c6c-9aff-1b553403eac7.png)

- So no matter where you're executing, all the reporting and eventing is the same, because we are loosely coupled.
  - We can do `fromjson` in jq or we can do more advanced xargs chaining on the websocket for ad-hox dev work
  - We can shot from the activitypub inbox receiver to a message queue for integration with existing celery
  - This way we sidestep all rate limiting except for when we have to preform write events to GitHub
  - Otherwise we always read GitHub data from cypher queries over the reboardcast data
    - We can also have listeners which reboardcast the resolved contents of content address style broadcast data (the top level, so if this sees a container image uri broadcast, it would be pulling it down and maybe rebroadcasting the `results.yaml` or whatever is they transform needed to rebroadcast that data.
    - This is our onramp into the linked data space, eventually KERI for backing comms security
- https://linkeddatafragments.org/
- http://query.linkeddatafragments.org/#query=&resultsToTree=false&queryFormat=graphql
- https://gist.github.com/rubensworks/9d6eccce996317677d71944ed1087ea6
- https://github.com/comunica/jQuery-Widget.js/blob/master/config/config-default.json
- We need to turn the stream into something we can query using cypher or graphql-ld
- https://swordapp.github.io/swordv3/swordv3.html
- https://oras.land/blog/gatekeeper-policies-as-oci-image/
- https://github.com/project-zot/zot
- Okay if we can make the KERI SCITT instance use the OCI upload/download spec and then align the telemetry and registry federation protocols
  - Look into existing registry federation protocol if exists
- https://s3hh.wordpress.com/2022/10/27/oci-based-linux/
  - Similar goals to OS DecentrAlice
- https://github.com/project-machine/mos/releases/tag/0.0.7
- https://github.com/opencontainers/distribution-spec/blob/main/spec.md#endpoints
- https://github.com/opencontainers/distribution-spec/issues/388
  - Have we thought about federation protocols / APIs? To enable registries to propagate uploaded content within a network of registries? Looking to come up to speed on any existing discussion if that's been touched on. Thank you!
  - References
    - https://github.com/opencontainers/distribution-spec/blob/main/spec.md#endpoints
      - Looked here for relevant paths here but not seeing anything that looks like it's for notifications / inbox style eventing
    - https://github.com/sapcc/keppel
    - https://github.com/ietf-scitt/use-cases/issues/14
      - Hoping we can align to similar federation protocols across transparency services and container registries so event stream consumers can work with the same protocol for each (ActivityStreams/Pub?)
- https://conformance.opencontainers.org/
- https://vsoch.github.io/django-oci/docs/getting-started/auth
- https://vsoch.github.io/django-oci/docs/getting-started/testing
- https://github.com/opencontainers/distribution-spec/issues/110#issuecomment-708691114
- https://github.com/sapcc/keppel
- https://github.com/sapcc/keppel/blob/master/docs/api-spec.md#post-keppelv1authpeering
  - Looks like they have their own spec for federation, maybe we can implement with ActivityPub?
    - Maybe we can leverage the existing APIs similar to the /admin endpoint and just add in the activitypub endpoints for activitystreams / linked data notifications
- https://github.com/sapcc/keppel/blob/master/docs/example-policy.yaml
- We can take one manifest and make it into another one for execution via a different mechanism
  - Similar to the CLI overlays
    - https://github.com/intel/dffml/blob/c82f7ddd29a00d24217c50370907c281c4b5b54d/entities/alice/alice/please/contribute/recommended_community_standards/cli.py#L60-L72
  - This is also similar to how we can decouple TODO logging from content for `alice please log todos`
    - Operation to generate TODO body
    - Operation for logging the TODO (write to GitHub)
  - Similar to a mutation of the propagated event into something context local relevant
    - Yes this vuln affects due to instance policy relevant threat model overlays or not
- https://github.com/opencontainers/image-spec/blob/main/artifact.md
- Manifest for CLI command

**schema/alice/shouldi/contribute/github-com-omnilib-aiosqlite.json**

```json
{
    "@context": "https://github.com/intel/dffml/raw/alice/schema/schema/alice/shouldi/contribute/0.0.0.schema.json",
    "repo_url": "https://github.com/omnilib/aiosqlite"
}
```

- As container build

**schema/image/container/build/alice-shouldi-contribute-results-github-com-omnilib-aiosqlite.json**

```json
{
    "@context": "https://github.com/intel/dffml/raw/alice/schema/github/actions/build/images/containers/0.0.0.schema.json",
    "include": [
        {
            "branch": "alice",
            "build_args": "[[\"REPO_URL\", \"https://github.com/omnilib/aiosqlite\"]]",
            "commit": "ca92bfae5092bce908b70f6b5e0afbe242ce7a5b",
            "dockerfile": "entities/alice/scripts/alice-shouldi-contribute-results.Dockerfile",
            "image_name": "alice-shouldi-contribute-results-github-com-omnilib-aiosqlite",
            "owner": "intel",
            "repository": "dffml"
        }
    ]
}
```

- https://codeberg.org/fediverse/fep
- Open Source scanning flow
  - Upload manifest to registry
    - Federation event (send to follower /inbox)
      - content: `https://github.com/opencontainers/image-spec/raw/v1.0.1/schema/image-manifest-schema.json`
        inReplyTo: activitypub extensions for security.txt post URL for content `activitypubsecuritytxt`
      - content: container image uri uploaded
        inReplyTo: activitypub extensions for security.txt post URL for content `https://github.com/opencontainers/image-spec/raw/v1.0.1/schema/image-manifest-schema.json`
  - Downstream listener (aka delve into [config dict](https://intel.github.io/dffml/main/contributing/codebase.html?highlight=config+dict#config))
    - Federation event (send to follower /inbox)
      - content: `https://github.com/intel/dffml/raw/alice/schema/github/actions/build/images/containers/0.0.0.schema.json`
        inReplyTo: activitypub extensions for security.txt post URL for content `activitypubsecuritytxt`
      - content: `<extracted content(?)>`
        inReplyTo: activitypub extensions for security.txt post URL for content `https://github.com/intel/dffml/raw/alice/schema/github/actions/build/images/containers/0.0.0.schema.json`
  - Downstream listener
    - Republish watched `inReplyTo` schema into job/message queue
      - RabbitMQ
    - Message queue delivers to worker nodes
      - Kaniko job waiting for celery queue for image to build
        - Exit after rebuild and have orchestration manage respawn
        - https://github.com/cloudfoundry/korifi
- https://github.com/opencontainers/distribution-spec/blob/main/extensions/_oci.md
  - Could discover federation opportunities via this or security.txt/md valid Actor as URL in file as well
- https://github.com/google/go-containerregistry/tree/d7f8d06c87ed209507dd5f2d723267fe35b38a9f/pkg/v1/remote#structure
  - > ![](https://github.com/google/go-containerregistry/raw/d7f8d06c87ed209507dd5f2d723267fe35b38a9f/images/remote.dot.svg)
- https://github.com/opencontainers/image-spec/blob/v1.0.1/manifest.md
  - > The third goal is to be [translatable](https://github.com/opencontainers/image-spec/blob/v1.0.1/conversion.md) to the [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec).
    - Does this mean we can send to https://aurae.io/quickstart/ ?
    - https://github.com/opencontainers/image-spec/blob/v1.0.1/schema/image-manifest-schema.json
      - https://opencontainers.org/schema/image/manifest
    - https://github.com/aurae-runtime/aurae/blob/3bb6d4c391ec6945436f941299a46c9a83168729/examples/pods-cri-nginx.ts#L57
    - https://github.com/aurae-runtime/aurae/blob/42972181b624a76b6888d1b0079a7f21c34bfb31/api/cri/v1/release-1.26.proto#L1086-L1096
    - https://github.com/aurae-runtime/aurae/commit/47dabf1414678626bd8a432fdf20fdbc6bdf49dc
- https://github.com/intel/dffml/blob/80e773712897a2fa2fb93e6abd4f852302adb79f/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md#checklist
- https://github.com/cloudfoundry/korifi/blob/63fece8d987b09744ea435bccf9af08813bc0611/HACKING.md#deploying-locally
- https://carvel.dev/blog/getting-started-with-ytt/
- Need helm and kubectl and etc.
- https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
- https://github.com/cloudfoundry/cli/wiki/V8-CLI-Installation-Guide#installers-and-compressed-binaries

```console
$ git clone --depth=1 https://github.com/cloudfoundry/korifi
$ cd korifi/
$ echo We should start mentioning which commit we pulled by checking it out after chdir
$ git checkout 63fece8d987b09744ea435bccf9af08813bc0611
$ curl -L https://carvel.dev/install.sh | K14SIO_INSTALL_BIN_DIR=$HOME/.local/bin bash
$ curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
$ curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
$ chmod +x kubectl
$ mkdir -p ~/.local/bin
$ mv ./kubectl ~/.local/bin/kubectl
$ kind delete cluster --name korifi-alice-shouldi-contribute || true
Deleting cluster "korifi-alice-shouldi-contribute" ...
$ ./scripts/deploy-on-kind.sh korifi-alice-shouldi-contribute --debug --verbose
$ (cd $(mktemp -d); curl -sfL "https://packages.cloudfoundry.org/stable?release=linux64-binary&version=v8&source=github" | tar zxv && chmod 755 cf{,8} && mv cf{,8} ~/.local/bin/)
```

- activitypub groups spec/fep
  - https://codeberg.org/fediverse/fep/src/branch/main/feps/fep-1b12.md
- https://socialhub.activitypub.rocks/t/fep-5624-per-object-reply-control-policies/2723/34
  - > i think the current state of talks is to have an Accept activity for each activity, and this gets used as the replyApproval for the third-party observer to verify, but beyond that, there is no specified mechanism for how replies get approved logically. it may be manual, it may be automatic based on some criteria (or not). you could totally have an application feature where replies from certain people get automatically approved, and from anyone else it goes to a sort of “reply request” UI similar to follow requests. you could add or remove people to the “auto-approve” list as you pleased.
- https://codeberg.org/fediverse/fep/src/branch/main/feps/fep-cb76.md
- https://codeberg.org/fediverse/fep/src/branch/main/feps/fep-2e40.md#example-create-fep-term-eventsource
  - Event source itself is similar to discovery of the /admin/websocket endpoint
- FEP-400e: Publicly-appendable ActivityPub collections
- https://forgefed.org/
- https://codeberg.org/fediverse/delightful-activitypub-development#user-content-forge-federation
- https://f3.forgefriends.org/structure.html
- https://codeberg.org/fediverse/delightful-activitypub-development#bridges
- https://forgejo.org/2023-02-27-forgejo-actions/
- https://codeberg.org/forgejo/runner
- https://forum.forgefriends.org/t/about-the-friendly-forge-format-f3/681
  - > ForgeFed is an [ActivityPub](https://www.w3.org/TR/activitypub/) extension. ActivityPub is an actor-model based protocol for federation of web services and applications.
- https://codeberg.org/forgejo/forgejo/issues/59
  - [FEAT] implement federation #59
- These folks know what's up
- https://git.exozy.me/a?tab=activity
  - https://git.exozy.me/a/website/src/commit/4672ed271dead5fdf8be7efc05e964c70924d7e9/content/posts/abusing-systemd-nspawn-with-nested-containers.md
- https://codeberg.org/earl-warren?tab=activity
- https://codeberg.org/dachary?tab=activity
- https://codeberg.org/forgejo/forgejo/issues/363
  - Where is the best place to discuss federation of CI? Maybe in the spec repo? Shall I just throw up a pull request on that GitLab with the schema? We're interested in folks rebroadcasting their GitHub webhooks, etc. into the ActivityPub space so as to enable live at HEAD in poly repo envs (to help secure rolling releases).
    - Related: https://github.com/ietf-scitt/use-cases/issues/14
    - Related: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-5178869
- https://codeberg.org/forgejo-contrib/forgejo-helm/issues/89#issue-257034
- https://codeberg.org/forgejo/runner/issues/4#issue-255815
- https://repos.goffi.org/libervia-backend/file/tip/CONTRAT_SOCIAL_en
- https://dream.public.cat/pub/dream-data-spec
- TODO
  - [ ] poly repo live at HEAD
    - [ ] Pin main branch issue ops via pull request after release / auto branch is cut and container image sha is known.
      - [ ] Auto merge
      - [ ] (Skip this and just commit and push to start)
    - [ ] https://github.com/jef/conventional-commits-release-action
  - [ ] Example of `alice threats listen activitypub -stdin`
    - Base flow just helps us take file representations of 
  - [x] Respond to Carina
  - [ ] https://github.com/intel/dffml/blob/80e773712897a2fa2fb93e6abd4f852302adb79f/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md#checklist
    - Still a good checklist
  - [ ] https://socialhub.activitypub.rocks/t/fep-5624-per-object-reply-control-policies/2723
    - Bingo!