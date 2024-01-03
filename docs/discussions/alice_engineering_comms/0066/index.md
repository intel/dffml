# 2022-10-25 Engineering Logs

- [ ] Cleanup progress report transcripts and post within Architecting Alice as numbered files 0000_
- [ ] GitHub Container Registry or Digital Ocean space or something as registry with static content?
  - https://github.com/MrE-Fog/static-container-registry
- [ ] Stream of Consciousness to trigger downstream rebuilds
  - https://github.com/intel/dffml/pull/1420
  - Ensure we show at least one downstream rebuild
    - `dffml`
    - `dffml[all]`
  - Future
    - Enable downstream events for builds of different tags / layers
      within existing dockerfiles and push them (if intermediate rebuilt).
- [ ] Fix DFFML CI
  - https://github.com/intel/dffml/actions/runs/3318045403
    - Not looking good...
    - https://github.com/intel/dffml/pull/1420
- [ ] Fix Alice CI
- [ ] 2ndparty
- [ ] RFCv2
- [ ] Call for contribution again
- [ ] Alice on chain
  - [ ] https://github.com/intel/dffml/discussions/1369#discussioncomment-2683370
  - [ ] Distributed system context store: web3 + manifests
    - [ ] Wonderland: The nickname we give the collective mass of thoughts in existence. This all the data in Alice on chain.
    - [ ] https://github.com/intel/dffml/issues/1377
- [x] Dataflow as class
- [ ] add the dataflow we executed to the chain. The next execution it should load data from some location via overlay to add this top level system context to the hostory of executed contexts. And the top level context should be linked both ways to the orignal external inputs (UCAN?)
- [ ] Cached flows to did chain then to backing storage via default input network as dataflow that does this to did in background. Start with json so they get saved to file. Add identity as input to top level context. Identiy could have parent input objects. such as this is of definition github username, which you could then have an operation that takes github usernames and outputs their SPDXIDs. When that operation SPDXID output is run through the deafult DID input network, a strategic plan (default overlayed dataflow to the default input network) which does this forking stuff. Could have location for user overlays in .local or something. When a context is thought of or hypothesised or executed it will be in the user context herstory. Users can optionally add overlays to their default flows (kind of like systemd). This could enable a user to overlay if im worjing within this cwd for this top level system cobtext run these commands. Alice as shell
  - [ ] long term: fork to save to chain on process exit (can we fork or coredump somehow on atexit?) by default.
- [ ] cve bin tool checker from chain
- [ ] https://gitbom.dev/
- [ ] Fix TODO on watching new contexts in memory orchestrator OR maybe this is fixed via the seperate linage? Probably needs event filtration similar to run_command so by default if not set in kwargs only 
- [ ] Operations and their config as inputs
  - [ ] Unify typing via parent type / primitive as Input parents
  - [ ] Can have operations that filter and old let through Input objects with specific parents or parents in specific order
  - [ ] The config dataflow, the startup on is the same as this new instantiate operations from Input objects. We can add shared config becomes a bunch of input objects. We have something like flow. ‘config_flow’ maybe which is where we’ll do initialization. Actually, lets just re use the main execution. Instantiate operations via an operation that instantiates them. We can then for each operation, use our newfound input filtering operations to form appropriate dependency graphs on order of instantiatation and usage of config objects (when executing in this top level context) we can then pass config and shared config as input objects to build config classes with references to same underlying data in memory. This solves shared config #720
  - [ ] Locality
  - [ ] Operation name
  - [ ] Stub values added as parents to outputs. Structured logs from an operation added as parents to operation outputs
- [ ] Use newfound operations and inputs with stub values
- [ ] Run an overlayed flow with output operations to build c4models of our dataflow based on parent input analysis. Generate architecture diagrams from it.
- [ ] Unify type system with Python’s type system via newfound input parent chains (#188)
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
      - [ ] There new contexts are run through a validity check to ensure all inputs to operations are consumed and all outputs are consumed by strategic plans somewhere.
        - [ ] Provide functionality to audit unused output values.
      - [ ] Gatekeeper and prioritizer models help decide what gets run and when.
    - [ ] top level system context we are executing in takes an input completeness for an organizationally applied strategic plan. Likely this completeness is a situation where we have a property of an `@config` which maps to a definition with something to do with completeness.
  - [ ] Target example around DFFML itself and it's development, and other OSS libs

---

system context includes

- I/O
  - Any cached values
- Prioritizer
  - Strategic plans
    - Some agents will not work with you unless they can run a strategic plan across a system context they are given to to execute to ensure that the system context has active provenance information that tells them to their desired level of assurance (trusted party vouch, attestation as an option)
    - We need to log which plans we execute as a part of the prioritizer using structured metrics or as an output of some kind
  - Gatekeeper
- Dataflow

---

### Note

- If you don't make a threat model, your attacker will make it for you. Daisy she thinks about making but then the rabbit is more interesting and now were down the hole. oops too late, should have made the threat model first. Let's hurry up and make it quickly before we get too deep into Wonderland.
- shouldi, wonder about installing packages. Explain how that increases threat surface.
- write about how we extended shouldi and go into technical details.
- Building markdown docs with mermaid diagrams

---

## Living THREATS.md

Install Alice https://github.com/intel/dffml/tree/alice/entities/alice

Create the `THREATS.md` file

```console
$ alice threats \
    -inputs \
      models/good.json=ThreatDragonThreatModelPath \
      models/GOOD_THREATS.md=ThreatsMdPath
```

We made `auditor_overlay.py` which is a data flow which calls the auditor. We
use `sed` to direct the data flow to run on the path to the threat model from
Threat Dragon used as input.

```console
$ dffml service dev export auditor_overlay:AUDITOR_OVERLAY \
    -configloader yaml \
    | sed -e 's/auditor_overlay:audit.inputs.ltm/ThreatDragonThreatModelPath/g' \
    | tee auditor_overlay.yaml
```

Generate `GOOD_THREATS.md` with auditing overlay.

```console
$ alice threats -log debug \
    -overlay auditor_overlay.yaml \
    -inputs \
      models/good.json=ThreatDragonThreatModelPath \
      models/GOOD_THREATS.md=ThreatsMdPath
```

Generate `BAD_THREATS.md` with auditing overlay.

```console
$ alice threats -log debug \
    -overlay auditor_overlay.yaml \
    -inputs \
      models/bad.json=ThreatDragonThreatModelPath \
      models/BAD_THREATS.md=ThreatsMdPath
```

Dump out to HTTP to copy to GitHub for rendering.

```console
$ (echo -e 'HTTP/1.0 200 OK\n' && cat models/GOOD_THREATS.md) | nc -Nlp 9999;
$ (echo -e 'HTTP/1.0 200 OK\n' && cat models/BAD_THREATS.md) | nc -Nlp 9999;
```