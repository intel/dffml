## 2022-09-27 @pdxjohnny Engineering Logs

- Install plugin with subdirectory from commit from git
  - `python -m venv .venv`
  - `source .venv`
  - `python -m pip install --upgrade setuptools pip wheel`
  - `python -m pip install --upgrade "git+https://github.com/intel/dffml@17ccb5b76f261d2725a64528e25669ef97920d70#subdirectory=entities/alice"`
    - pypi proxy is how we enable manifest BOM component swap out for downstream validation within 2nd party CI setup (workaround for dependency links issue)
      - References
        - https://github.com/intel/dffml/pull/1207
        - https://github.com/intel/dffml/pull/1061
        - https://github.com/intel/dffml/discussions/1406#discussioncomment-3676224

```
$ dffml version
dffml 0.4.0 /src/dffml/dffml 5c89b6780 (dirty git repo)
dffml-config-yaml 0.1.0 /src/dffml/configloader/yaml/dffml_config_yaml 5c89b6780 (dirty git repo)
dffml-config-image not installed
dffml-config-jsonschema 0.0.1 /src/dffml/configloader/jsonschema/dffml_config_jsonschema 5c89b6780 (dirty git repo)
dffml-model-scratch not installed
dffml-model-scikit not installed
dffml-model-tensorflow not installed
dffml-model-tensorflow-hub not installed
dffml-model-vowpalWabbit not installed
dffml-model-xgboost not installed
dffml-model-pytorch not installed
dffml-model-spacy not installed
dffml-model-daal4py not installed
dffml-model-autosklearn not installed
dffml-feature-git 0.3.0 /src/dffml/feature/git/dffml_feature_git 5c89b6780 (dirty git repo)
dffml-feature-auth not installed
dffml-operations-binsec not installed
dffml-operations-data not installed
dffml-operations-deploy not installed
dffml-operations-image not installed
dffml-operations-nlp not installed
dffml-operations-innersource 0.0.1 /src/dffml/operations/innersource/dffml_operations_innersource 5c89b6780 (dirty git repo)
dffml-service-http not installed
dffml-source-mysql not installed
```

- Encourage and coordinate collaborative documentation of strategy and implementation as living documentation to help community communicate amongst itself and facilitate sync with potential users / other communities / aligned workstreams.
- SCITT
  - https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md
    - https://github.com/ietf-scitt/use-cases/pull/18
- Stream of Consciousness
  - Decentralized Web Node and Self-Sovereign Identity Service
    - https://github.com/TBD54566975/ssi-service/tree/main/sip/sips/sip4
    - https://forums.tbd.website/t/sip-4-discussion-dwn-message-processing/137
    - https://github.com/TBD54566975/ssi-service/pull/113
      - Gabe approved 17 minutes ago
        - Chaos smiles on us again
      - https://github.com/TBD54566975/ssi-service/blob/3869b8ef2808210201ae6c43e2e0956a85950fc6/pkg/dwn/dwn_test.go#L22-L58
        - https://identity.foundation/credential-manifest/
          - > For User Agents (e.g. wallets) and other service that wish to engage with Issuers to acquire credentials, there must exist a mechanism for assessing what inputs are required from a Subject to process a request for credential(s) issuance. The Credential Manifest is a common data format for describing the inputs a Subject must provide to an Issuer for subsequent evaluation and issuance of the credential(s) indicated in the Credential Manifest.
            >
            > Credential Manifests do not themselves define the contents of the output credential(s), the process the Issuer uses to evaluate the submitted inputs, or the protocol Issuers, Subjects, and their User Agents rely on to negotiate credential issuance.
            > 
            > ![image](https://user-images.githubusercontent.com/5950433/192642680-627f9da6-ebb1-45b6-9872-7202e8b3fcaf.png)
          - In our distributed compute setup, credential issuance is the execution (which we had been looking at confirming the trades of via the tbDEX protocol, no work has been done on that front recently from DFFML side)
          - What they refer to as a "Credential Manifest" is similar to what we refer to as an "Manifest Instance".
            - https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md
        - `SpecVersion` has all the properties we require of Manifests (see `$schema`) so we can indeed classify a "Credential Manifest" as a Manifest.
          - Alignment looking strong!
          - > ![image](https://user-images.githubusercontent.com/5950433/192644284-3cf55d65-ca00-4c25-98fa-babf1bfd945d.png)
      - https://github.com/TBD54566975/ssi-service/pull/113/files#diff-7926652f7b7153343e273a0a72f87cb0cdf4c3063ec912cdb95dc541a8f2785dR62