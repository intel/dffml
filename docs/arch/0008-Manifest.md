# Manifest

Manifests allow us to focus less on code and more on data.
By focusing on the data going into and out of systems. We can achieve standard
documentation of processes via a standard interface (manifests).

Our manifests can be thought of as ways to provide a config class with it's
parameters or ways to provide an operation with it's inputs.

Similar to an OpenAPIv3 spec.

References:

- JSON Schema

  - https://json-schema.org/learn/getting-started-step-by-step

  - https://schema.org/

  - https://www.schemastore.org/json/

- Credential Manifest

  - Aligned concept

  - https://identity.foundation/credential-manifest/

- Manifest Shim (parser and validator for manifests)

  - https://github.com/intel/dffml/pull/1273

## Validating

Install jsonschema, and pyyaml python modules

- https://python-jsonschema.readthedocs.io/en/latest/
- https://pyyaml.org/wiki/PyYAMLDocumentation

```console
pip install pyyaml jsonschema
```

Write a manifest

**manifest.yaml**

```yaml
$schema: https://intel.github.io/dffml/manifest-format-name.0.0.2.schema.json
pipeline_runs:
  - git:
      repo: https://github.com/intel/dffml.git
      file: dffml/__init__.py
      branch: main
```

This is how you convert from yaml to json

```console
$ python -c "import sys, pathlib, json, yaml; pathlib.Path(sys.argv[-1]).write_text(json.dumps(yaml.safe_load(pathlib.Path(sys.argv[-2]).read_text()), indent=4) + '\n')" manifest.yaml manifest.json
```

Write the schema

**manifest-format-name.0.0.2.schema.json**

```json
{
    "$id": "https://intel.github.io/dffml/manifest-format-name.0.0.2.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "description": "An example manifest referencing Python files within Git repos",
    "properties": {
        "$schema": {
            "type": "string",
            "enum": ["https://intel.github.io/dffml/manifest-format-name.0.0.2.schema.json"]
        },
        "pipeline_runs": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/pipeline_run"
            },
            "minItems": 1,
            "uniqueItems": true
        }
    },
    "additionalProperties": false,
    "required": [
        "$schema",
        "pipeline_runs"
    ],
    "definitions": {
        "pipeline_run": {
            "type": "object",
            "properties": {
                "git": {
                    "$ref": "#/definitions/git_repo_python_file"
                }
            },
            "additionalProperties": false,
            "oneOf": [
                {
                    "required": [
                        "git"
                    ]
                }
            ]
        },
        "git_repo_python_file": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "pattern": "\\.git$"
                },
                "branch": {
                    "type": "string"
                },
                "file": {
                    "type": "string",
                    "pattern": "\\.py$"
                }
            },
            "additionalProperties": false,
            "required": [
                "repo",
                "branch",
                "file"
            ]
        }
    }
}
```

Example below validates, checking status code we see exit code 0 which means
success, the document conforms to the schema.

```console
$ jsonschema --instance manifest.json manifest-format-name.0.0.2.schema.json
$ echo $?
0
```

## Writing

Suggested process (in flux)

- Make sure you can run the jsonschema validator

  - TODO Validation micro service

- Look at existing problem space

  - What data is needed? This likely will becomes the inputs of a dataflow,
    or an operation, or config.

  - Write first draft of what a valid manifest would be

- Write schema based off initial manifest

  - Do not include fields for future use. Only include what you currently intend
    to use for each version

    - Instead, create a new format name and new schema. If we stick to the rule
      of if you have the data you have to act on it, there is never any if A then
      B situations. If you want a different outcome, you create different manifest.
      This helps keep architectures loosely coupled
      https://medium.com/@marciosete/loosely-coupled-architecture-6a2b06082316

    - We also decided that we could potentially combine manifests. This allows for
      you to use the data you wanted, but just keep it sperate and make the decision
      to combine the equivalent of adding variables purely as conditional on use of data.
      This way if the data is present, it is always used!

    - By ensuring that data present is always used, we can begin to map manifests to
      dataflows, in this way, we can check the validity of a dataflow simply by ensuring
      all manifest data is used as an input or config.

      - As such, a passing validity check ensures we have a complete description of a
        problem. We know all the inputs and system constraints (manifests), and we are
        sure that they will be taken into account on execution (dataflow run).

  - Each field with a `type` MUST have a `description`

- Write ADR describing context around creation and usage of manifest

  - The ADR should describe how the author intends the manifest to be used

  - Treat the ADR + manifest like a contract. If something
    accepts the manifest (valid format and version, see shim)
    it is obligated to fulfil the intent of the ADR. The consumer
    MUST return an error response when given a manifest if it
    cannot use each piece of data in the manifest as directed by
    the ADR and descriptions of fields within the manifest schema.

  - The `Intent` section of the ADR should describe how you want manifest
    consumers to use each field.

## ADR Template

```rst
my-format-name
##############

Version: 0.0.1
Date: 2022-01-22

Status
******

Proposed|Evolving|Final

Description
***********

ADR for a declaration of assets (manifest) involved in the process
of greeting an entity.

Context
*******

- We need a way to describe the data involved in a greeting

Intent
******

- Ensure valid communication path to ``entity``

- Send ``entity`` message containing ``greeting``
```
