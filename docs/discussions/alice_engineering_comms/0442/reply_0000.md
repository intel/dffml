## 2023-11-05 IETF 118 Hackathon Day 2

- A.J. is having issues with OpenAPI spec
  - [2023-03-23 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/blob/alice/docs/discussions/alice_engineering_comms/0217/reply_0000.md)

```console
$ npx swagger-cli bundle docs/openapi/openapi.yml -o docs/openapi/openapi.json --dereference
```

- A.J. was wondering about the NVD v2 API code
  - https://github.com/intel/cve-bin-tool/blob/44b5e990657a43535365585e7a392921107a2fad/cve_bin_tool/data_sources/nvd_source.py#L356-L394
- Harold was doing SBOM for ML models in SCITT
  - Talk of the CycloneDX PRs
- A.J. says there is a NIST AI working group
  - Harold seems to be the only technical contact there
- Abusing SHA in content type for detached COSE payloads via SHA in media type parameters after multiple suffixes for ML models
- Henk
  - "The other day I spotted an albino Dalmatian"
  - https://github.com/slsa-framework/slsa/issues/975
  - https://github.com/slsa-framework/slsa/issues/985
  - https://openssf.org/blog/2023/10/20/slsa-tech-talk-highlights/
  - https://docs.guac.sh/guac-ontology/
    - has_id is not really an ontology
    - John guesses it's because it's neo4j-ish
    - https://docs.guac.sh/graphql/#topological-definitions
      - CVE_CERTIFY_VULN
        - Edge
        - Needs two nodes
  - Henk approves of Use Case of GUAC as firewall event loops
  - https://docs.google.com/presentation/d/11cycDxYaoZpuG144pR6atI1_zk2CfZOWlNO_f_HhhyE/edit#
- 40 minutes until slides for what we accomplished need to be done
- Ned has landed! He's going to sleep

[![asciicast](https://asciinema.org/a/619381.svg)](https://ascinema.org/a/619381)

- https://github.com/scitt-community/scitt-examples/pull/2
- Orie: KeyTrans is DIDs but useful
- CaddyProxy resumable uploads as spec