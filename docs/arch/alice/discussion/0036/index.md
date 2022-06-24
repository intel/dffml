Plan:

- [ ] Dataflow as class
- [ ] Fix TODO on watching new contexts in memory orchestrator
- [ ] Subflow input parents
  - [ ] Locality 
- [ ] prioritizer
  - [ ] statigic plans (similar to dataflow as class method output grabbers)
  - [ ] gatekeeper
- [ ] Inventory
- [ ] Creation based on datatypes
  - [ ] Input to dataclass field mappings
  - [ ] Quicker syntax for dataflow definition
- [ ] Have strategic plan models predict what inputs and outputs will exist to reach desired output metrics
  - [ ] Alice create threat model of code base
    - [ ] strategic plan for threat model completeness
      - [ ] keeps suggesting new system contexts, or incentivizing creation of new system contexts by other strategic plans so as to drive up completeness metric
      - [ ] New contexts are created by finding different sets of operations connected differently via flow modifications where applicable
    - [ ] top level system context we are executing in takes an input completeness for an organizationally applied strategic plan. Likely this completeness is a situation where we have a property of an `@config` which maps to a definition with something to do with completeness.
  - [ ] Target example around DFFML itself and it's development, and other OSS libs