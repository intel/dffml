## 2023-12-01 @pdxjohnny Engineering Logs

- https://chromium.googlesource.com/chromium/chromium/+/refs/heads/trunk/chromeos/attestation/attestation_flow.cc
- https://github.com/slsa-framework/slsa-github-generator/blob/62a6671ba95c18cf73102bda18ec523e39dc7ab2/internal/builders/generic/attest.go#L81C30-L81C51
- https://github.com/in-toto/scai-demos/tree/main/.github/actions
- https://slsa.dev/spec/v1.0/provenance
- https://search.sigstore.dev/?logIndex=33351527

```json
{
    // Standard attestation fields:
    "_type": "https://in-toto.io/Statement/v1",
    "subject": [...],

    // Predicate:
    "predicateType": "https://slsa.dev/provenance/v1",
    "predicate": {
        "buildDefinition": {
            "buildType": string,
            "externalParameters": object,
            "internalParameters": object,
            "resolvedDependencies": [ ...#ResourceDescriptor ],
        },
        "runDetails": {
            "builder": {
                "id": string,
                "builderDependencies": [ ...#ResourceDescriptor ],
                "version": { ...string },
            },
            "metadata": {
                "invocationId": string,
                "startedOn": #Timestamp,
                "finishedOn": #Timestamp,
            },
            "byproducts": [ ...#ResourceDescriptor ],
        }
    }
}

#ResourceDescriptor: {
    "uri": string,
    "digest": {
        "sha256": string,
        "sha512": string,
        "gitCommit": string,
        [string]: string,
    },
    "name": string,
    "downloadLocation": string,
    "mediaType": string,
    "content": bytes, // base64-encoded
    "annotations": object,
}

#Timestamp: string  // <YYYY>-<MM>-<DD>T<hh>:<mm>:<ss>Z
```


```yaml
_type: https://in-toto.io/Statement/v1
subject:
  - name: pkg:npm/sigstore@2.1.0
    digest:
      sha512: >-
        90f223f992e4c88dd068cd2a5fc57f9d2b30798343dd6e38f29c240e04ba090ef831f84490847c4e82b9232c78e8a258463b1e55c0f7469f730265008fa6633f
predicateType: https://slsa.dev/provenance/v1
predicate:
  buildDefinition:
    buildType: https://slsa-framework.github.io/github-actions-buildtypes/workflow/v1
    externalParameters:
      workflow:
        ref: refs/heads/main
        repository: https://github.com/sigstore/sigstore-js
        path: .github/workflows/release.yml
    internalParameters:
      github:
        event_name: push
        repository_id: '495574555'
        repository_owner_id: '71096353'
    resolvedDependencies:
      - uri: git+https://github.com/sigstore/sigstore-js@refs/heads/main
        digest:
          gitCommit: 26d16513386ffaa790b1c32f927544f1322e4194
  runDetails:
    builder:
      id: https://github.com/actions/runner/github-hosted
    metadata:
      invocationId: >-
        https://github.com/sigstore/sigstore-js/actions/runs/6014488666/attempts/1
```