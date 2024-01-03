- Roadmap recap - Stream of Consciousness - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
  - [ ] https://github.com/ietf-scitt/use-cases/pull/18
    - [x] https://github.com/scitt-community/scitt-api-emulator/pull/27
    - [ ] SCITT API Emulator Federation pull request
  - [ ] SCITT DFFML [InputNetwork](https://github.com/intel/dffml/blob/7d381bf67a72fe1ecb1012393d5726085564cb0e/dffml/df/memory.py#L283-L765)
    - [ ] https://github.com/chroma-core/chroma
    - [ ] https://huggingface.co/spaces/ludwigstumpp/llm-leaderboard
- https://www.youtube.com/watch?v=1EL03Pl4oL4&list=RDEMwZ9tKHt9iT5CWajVqMu11w&index=12

```json
{
  "$id": "https://example.com/alice.shouldi.contribute.cicd.component.1.0.0.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "required": ["claim"],
  "properties": {
    "claim": {
      "type": "object",
      "required": ["untagged"],
      "properties": {
        "untagged": {
          "type": "object",
          "minProperties": 1,
          "patternProperties": {
            "^.*$": {
              "type": "object",
              "required": ["features"],
              "properties": {
                "features": {
                  "type": "object",
                  "anyOf": [
                    {
                      "required": [
                        "alice.shouldi.contribute.cicd:cicd_action_library"
                      ]
                    },
                    {
                      "required": [
                        "alice.shouldi.contribute.cicd:cicd_jenkins_library"
                      ]
                    }
                  ],
                  "properties": {
                    "alice.shouldi.contribute.cicd:cicd_action_library": {
                      "type": "object",
                      "required": ["result"],
                      "properties": {
                        "result": {
                          "type": "boolean",
                          "enum": [true]
                        }
                      }
                    },
                    "alice.shouldi.contribute.cicd:cicd_jenkins_library": {
                      "type": "object",
                      "required": ["result"],
                      "properties": {
                        "result": {
                          "type": "boolean",
                          "enum": [true]
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```