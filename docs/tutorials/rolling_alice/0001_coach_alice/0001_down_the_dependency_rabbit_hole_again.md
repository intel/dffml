# [Volume 1: Chapter 1: Down the Dependency Rabbit-Hole Again](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md)

> 2022 tutorials. This tutorial is TODO
> Related:
> - https://github.com/dffml/dffml-pre-image-removal/tree/shouldi_dep_tree

### Table Of Contents

- [Upstream](https://github.com/intel/dffml/tree/alice/entities/alice)

#### Volume 0: Architecting Alice

- [Forward](https://github.com/intel/dffml/discussions/1369#discussioncomment-2688532)
- [Preface](https://github.com/intel/dffml/discussions/1369#discussion-4023096)
- [Introduction and Context](https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280)

#### Volume 1: Coach Alice

- [Down the Dependency Rabbit-Hole Again](https://github.com/intel/dffml/discussions/1369#discussioncomment-2663771)

DFFML has been lacking public threat model documentation. It's important the main package, all the plugins, and the environment resulting from every tutorial and example be thoroughly validated for security. This means we need to understand the security posture of those environments. A [Threat Model](https://owasp.org/www-community/Threat_Modeling) identifies assets, threats, and mitigations. It's a document we want to keep up to date so end users know what kind of security guarantees they have about their environment, and what trade offs or considerations they should be aware of. In the spirt of automating our documentation validation, we should also automate our the creation and validation of threat models associated with the environments produced as a result of our documentation. Therefore we will spend the month of May teaching Alice her first skill, threat modeling!

This month we'll only be able to scratch the surface of what Alice would need to know to create complete threat models. As we end our month we'll talk about how we'll measure that completeness in a future tutorial, and how we'll leverage concurrency and parallelism to raise the value of our completeness over time as Alice learns more about her new skill.

## Target

By July 1st, Alice should be ready to analyze projects (repo or set of repos) and present threat models on those projects. She will create a slide deck by making a system context that gets executed to produce a PDF of the slides. The slides will use inputs from the threat model data. Threat models will be created as hybrid reStructuredText and markdown Sphinx sites (for mermaid diagrams rendering on GitHub by default, allow for using markdown). Ideally we’ll be able to have Alice read the content of the report (which will not be copied verbatim to slides, only graphics for each section will be copied to slides) while giving a presentation of the slide deck. 

This is in preparation for our upcoming second and third party plugin support. We'll later look to create CI jobs which keep the threat model documents up to date within each repo.

## Plan

shouldi is ripe for expansion. Let's see if we can pick a set of repos and make sure Alice can create basic threat models on them via pure static analysis. Build an SBOM, run CVE Bin Tool against it. Traverse dependency trees to get all installed modules. Map network functions to dependencies. Guess what activities are happening based off of functionalities of underlying stdlib libraries where used. In fact, we’ll be patching CVE Bin Tool to add support for checking more than one language effectively merging aspects of shouldi into cve-bin-tool. The goal is to leverage dffml for output plugin support and scanning overlays for organizational policies.

Let's then expand upon that and add dynamic analysis.

## People

- John Whiteman was planning on writing collectors and analyzing AST
- Michael could help us generate PDFs from Sphinx sites
- 

## Checklist

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
