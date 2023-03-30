# Federated Forge Automated Deduplicated Analysis Cross Trust Boundry CD

```console
$ docker-compose up
```

## Sketch Notes

- ActivityPub (future: TransparencyInterop) protos for grpc service / openapi definition
  - On webfinger resolved endpoint for `/inbox`
    - Policy Engine (Prioritizer's Gatekeeper/Umbrella) - Defined via CycloneDX DataFlows
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

## References

- [CI/CD Event Federation codeberg.org/forgejo/discussions#12](https://codeberg.org/forgejo/discussions/issues/12)
- [RFCv4.1: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/748597b37401bd59512bfedc80158b109eadda9b/openssf_metrics.md#openssf-metrics)

## TODO

- [ ] Federated Forge events
- [ ] Policy engine leveraging CycloneDX dataflow format and IPVM execution
- [ ] GAUC emmiter for ActivityPub federated event space
- [ ] Feed build server (melange) on SBOM / Dockerfile `FROM` retrigger events
