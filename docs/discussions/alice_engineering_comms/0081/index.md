 # 2022-11-09 Engineering Logs

- Workstreams
  - [ ] Knowledge graph sharing (basics)
    - [ ] Provide queriable data via? JSON-LD static file serves to start?
      - [ ] Implement initial dumps to chosen format via DFFML plugin patches for first integration.
    - [ ] Query via GraphQL-LD (https://github.com/comunica/comunica)
    - [ ] Data security from [SCITT](https://scitt.io)
    - [ ] Identity from probably github.com/user.keys or keybase or QR code (HSM on phone) or other (overlayed?) methods.
  - [ ] Distributed Execution
    - [ ] Sandboxing
      - [ ] Overlays (next phase parsers) for `policy.yml` to define what are acceptable sandboxing criteria (annotation to the chosen orchestrator, aka the sandboxing method / manager during execution).
        - Overlays to parse more types of available sandboxing mechanisms and determine how much we like them or not.
    - [ ] Reference implementation of content addressable compute contract execution using Decentralized Identifier, Verifiable Credential, and Decentralized Web Node based for layer 7/8?.
  - [ ] Entity Analysis Trinity
    - [ ] Static Analysis
      - [ ] Need to understand dependencies
    - [ ] Living Threat Models
      - [ ] `THREATS.md` talks about and includes maintainance / lifecycle health (recommended community standards at minimum). 
        - Related: https://github.com/johnlwhiteman/living-threat-models/issues/1
    - [ ] Open Architecture
      - [ ] Conceptual upleveling of dependencies into architecture via static overlay with architecture or overlay to synthesize.
  - [ ] Feedback loop
    - [ ] Stream of Consciousness
      - #1315
        - https://github.com/w3c/websub
        - https://youtu.be/B5kHx0rGkec
          - 12 years, this has existed for 12 years, how am I just now finding out about this.
          - we want this but callbacks supported as data flows / open architecture / use webrtc to call back.
          - http://pubsubhubbub.appspot.com/
    - [ ] Implement Gatekeeper (`get_operations()`/`gather_inputs()`)
      - [ ] Overlays / schema extensions for `policy.yml` which prioritizer
            understands how to leverage.
    - [ ] Implement Prioritizer (`get_operations()`/`gather_inputs()`)
  - [ ] Interfaces
    - [ ] Keeping GitHub workflows up to date
      - Usages of reusables templated and updated on trigger from upstream
        or template or within context config modifications.