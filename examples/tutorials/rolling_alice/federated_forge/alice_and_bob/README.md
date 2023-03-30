# Federated Forge Automated Deduplicated Analysis Cross Trust Boundry CD

To bring up

```console
$ docker-compose up
```

To cleanup

```console
$ docker-compose rm -f
$ sudo git clean -xdf .
```

## Sketch Notes

- Allowlists as dynamic context aware policy as code over provenance of message content
- ActivityPub (future: TransparencyInterop) protos for grpc service / openapi definition
  - On webfinger resolved endpoint for `/inbox`
    - Policy Engine (Prioritizer's Gatekeeper/Umbrella) - Defined via [CycloneDX DataFlows](https://github.com/CycloneDX/specification/pull/194)
      - Upstream
        - GUAC + Cypher queries
      - Overlay
        - https://github.com/intel/cve-bin-tool/issues/2639
        - https://github.com/seedwing-io/seedwing-policy/
      - Orchestrator
        - pr-validation
          - https://code.forgejo.org/forgejo/runner/src/branch/main/cmd/exec.go
        - prod / service batch jobs L0
          - https://github.com/ipvm-wg/spec/pull/8
- KERI backed keys for duplicity detection to reboot web of trust off less robust revocation detection mechanisms
  - Publish `releaseartifact.json` to ActivityPub security.txt/md stream
    - Others who are committing or online cloning a repo watch those streams (schema in content)
- Setup auto prs
  - Rebuild chains based off SBOM as inventory for building cross linkage to determine downstream validation pattern / hypothesized flows and prs-to-prs required to enable execution, the dependency tree of artifacts.
    - https://github.com/intel/cve-bin-tool/blob/main/.github/workflows/sbom.yml
    - https://github.com/renovatebot/renovate
- Mirror webhook event streams into federated forge environment
  - Upstream changes directly to git
    - Publish federated event corresponding to `git ...` action
      - Federate with more servers/services/nodes for availability.
    - Comms over SSI Service/DWN with KERI backed keys ideally rooted to [TEE enclave keys](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-trust-domain-extensions.html)
    - Watch SCITT stream of peers with ephemeral resync when online KERI watcher
      - Require sync before queries to streams, raft?
- Data transforms
  - heartwood --> openapi generator + actogitypub endpoints off cyclonedx -> guac --> cypher mutatuon and ipvm exec chain for analysis --> guac emit activitypub --> forgefed
- Use the SBOM of the cypher query to build the re-trigger flows
  - On query we build and publish SBOM of query, if downstream listeners to they query stream see new system context stream (schema `inReplyTo` or `replies` is query, cache busting inputs if applicable) come in, and similar to a `FROM` rebuild chain that SBOM has not been built, we transform into the manifest which triggers the build, recursively fulfill any dependencies (creating repos with workflows with issue ops or dispatch flows based on upstream and overlays: distro-esq patch-a-package)
    - On complete, federate re-trigger event for original SBOM, publish the same SBOM again
- Hook the write to a given node field to publish schema (can be done in via policy local neo in GraalVM)
  - `SET output.streams.by_schema_shortname.vcs_push = output.streams.by_schema_shortname.vcs_push + {key: n.value}`
- `alice threats listen activitypub -stdin`
  - For now execute with grep and xargs unbuffered for each note from websocket/websocat
  - Alias for dataflow which has ActivityPub based listener (later encapsulate that in dataflow, for now follow self with startkit and others, follow as code)
  - Output via operation which just does `print()` to stdout
    - Publish workflow run federated forge events for each operation / dataflow executed in response
      - Check out their webfinger and inspect the event stream to publish the same way
      - If we still need to use `content` POST to admin endpoint to create new `Note`s
      
## References

- [CI/CD Event Federation codeberg.org/forgejo/discussions#12](https://codeberg.org/forgejo/discussions/issues/12)
- [RFCv4.1: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/748597b37401bd59512bfedc80158b109eadda9b/openssf_metrics.md#openssf-metrics)

## TODO

- [x] Forges intialized for Alice and Bob
- [ ] Federated Forge events
- [ ] Policy engine leveraging CycloneDX dataflow format and IPVM execution
- [ ] GAUC emmiter for ActivityPub federated event space
- [ ] Feed build server (melange) on SBOM / Dockerfile `FROM` retrigger events
