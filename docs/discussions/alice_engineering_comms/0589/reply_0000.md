## 2024-04-09 @pdxjohnny Engineering Logs

- https://github.com/dockur/windows
- https://asciinema.org/a/653113
  - > Please write a whitepaper on the data centric fail safe architecture for artificial general intelligence known as the Open Architecture. Please include how SCITT and federation help multiple instances communicate securely
- https://rook.io/docs/rook/latest-release/Getting-Started/Prerequisites/prerequisites/#ceph-prerequisites
- https://github.com/knative/eventing/pull/7783
- https://knative.dev/docs/getting-started/first-source/
  - https://github.com/ruromero/cloudevents-player
  - https://github.com/ruromero/cloudevents-player/blob/main/deploy/knative.yaml
  - https://github.com/knative/docs/tree/afebc069984231ce3effd139bc8b9a31c3af1e91/code-samples/eventing/github-source
    - knative github event source to activitypub
      - activitypub event source
    - SCITT federation consume from activitypub
- https://github.com/openai/openai-python/blob/main/helpers.md#assistant-events
- https://platform.openai.com/docs/assistants/tools/knowledge-retrieval

```json
{
    "$defs": {
        "WritePaperSectionContent": {
            "properties": {
                "comments": {
                    "description": "LLM comments on why this section is relevant",
                    "title": "Comments",
                    "type": "string"
                },
                "section_number": {
                    "description": "Section number is integers with `.` as delimiter",
                    "examples": [
                        "1.1.1"
                    ],
                    "title": "Section Number",
                    "type": "string"
                },
                "slug": {
                    "description": "The key for which this object is the value within the parent object",
                    "title": "Slug",
                    "type": "string"
                },
                "text": {
                    "description": "The content for this section. This should be at least 500 words",
                    "title": "Text",
                    "type": "string"
                },
                "title": {
                    "description": "The title for this sub-section",
                    "title": "Title",
                    "type": "string"
                }
            },
            "required": [
                "slug",
                "title",
                "text",
                "comments",
                "section_number"
            ],
            "title": "WritePaperSectionContent",
            "type": "object"
        }
    },
    "properties": {
        "brief": {
            "description": "LLM comments on why this section is relevant, could be the content of the prompt used to generate the section",
            "title": "Brief",
            "type": "string"
        },
        "section_number": {
            "description": "Section number is integers with `.` as delimiter",
            "examples": [
                "1.1.1"
            ],
            "title": "Section Number",
            "type": "string"
        },
        "slug": {
            "description": "The key for which this object is the value within the parent object",
            "title": "Slug",
            "type": "string"
        },
        "subsections": {
            "additionalProperties": {
                "$ref": "#/$defs/WritePaperSectionContent"
            },
            "title": "Subsection objects",
            "type": "object"
        },
        "title": {
            "description": "The title for this sub-section",
            "title": "Title",
            "type": "string"
        }
    },
    "required": [
        "slug",
        "title",
        "brief",
        "section_number",
        "subsections"
    ],
    "title": "WritePaperSection",
    "type": "object"
}
```

- TODO
  - [x] #1552
  - [ ] Have agent which writes papers use sources and re-read and re-edit it's work until it's complete / detailed enough per original instructions. It seems to only grab a few points and hallucinate a lot (it re-defines SCITT to another acronym).
    - [ ] Respond to Nicole
    - [x] [open-architecture.json](https://github.com/intel/dffml/files/14929926/open-architecture.json)
    - [ ] https://github.com/intel/dffml/pull/1553
      - [ ] Explore depth of field mapping. Tell me what I'm thinking based on these notes (On Mind Control early sections): predict train (most likely branch in hypothesized graph of thoughts) of thought. Use bullet point indentation to indicate paths taken, use order of edits of list items (unstructured markdown parser) to indicate times those branches were explored, use this to build known graph nodes in graph / tree of thoughts - analogy of agent workload ID in SCITT policy engine + relay phase plan - token issuance compounds on approved workloads
        - [ ] Instead of `write paper` ask it to output a code reviewer prompt (and thread/chat memory) for DFFML reviewer job using the docs / it's analysis of the strategic principles and how a code reviewer should view changes in alignment with them.
          - [ ] Incorporate threat modeling
        - [ ] Research for `write paper`
        - [ ] Research for technology propesctive tree branches (VMaaS, CaaS, faas/serverless -> web3 (ipvm), knative, enok, cloudflare workers (v8), cloudfoundry/coolify/heroku style (Procfiles))
          - knative and web3 are going in the right direction because they build an N+1 stack layer using patterns learned from < N stack layers. The others are not because 
  - [ ] ~~Play with https://github.com/coollabsio/coolify (as opposed to knative)~~
    - Pusher API needed
  - [x] 🌲🏹🎯🌲
  - [ ] knative activitypub event source for knative SCRAPI SCITT federating function
    - Federation as OOB (first heartwood) style sync of `workspace/storage/`
  - [ ] knative llmproxy accept cloud events
    - https://github.com/knative/docs/blob/main/code-samples/eventing/parallel/multiple-branches/
    - https://github.com/knative/docs/tree/main/code-samples/eventing/parallel/mutual-exclusivity
    - https://github.com/knative/docs/blob/afebc069984231ce3effd139bc8b9a31c3af1e91/code-samples/eventing/helloworld/helloworld-python/README.md#recreating-the-sample-code
    - We can probably do a github actions workflow -> knative eventing transform to swap the initial policy engine implementation out for knative eventing based execution of an AI agent langgraph flow