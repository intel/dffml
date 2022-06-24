# Alice Learns to Threat Model

> Tutorial developed May 2022

DFFML has been lacking public threat model documentation. It's important the main package, all the plugins, and the environment resulting from every tutorial and example be thoroughly validated for security. This means we need to understand the security posture of those environments. A [Threat Model](https://owasp.org/www-community/Threat_Modeling) identifies assets, threats, and mitigations. It's a document we want to keep up to date so end users know what kind of security guarantees they have about their environment, and what trade offs or considerations they should be aware of. In the spirt of automating our documentation validation, we should also automate our the creation and validation of threat models associated with the environments produced as a result of our documentation. Therefore we will spend the month of May teaching Alice her first skill, threat modeling!

This month we'll only be able to scratch the surface of what Alice would need to know to create complete threat models. As we end our month we'll talk about how we'll measure that completeness in a future tutorial, and how we'll leverage concurrency and parallelism to raise the value of our completeness over time as Alice learns more about her new skill.

## Target

By June 1st, Alice should be ready to analyze projects (repo or set of repos) and present threat models on those projects. She will talk to a slide deck she creates by making a system context that gets executed to produce a PDF of the slides. The slides will use inputs from the threat model data. Threat models will be created as hybrid reStructuredText and markdown Sphinx sites (for mermaid diagrams rendering on GitHub by default, allow for using markdown). Alice will read the content of the report which will not be copied verbatim to slides, only graphics for each section will be copied to slides.

This is in preparation for our upcoming second and third party plugin support. We'll later look to create CI jobs which keep the threat model documents up to date within each repo.

## Plan

shouldi is ripe for expansion. Let's see if we can pick a set of repos and make sure Alice can create basic threat models on them via pure static analysis. Build an SBOM, run CVE Bin Tool against it. Traverse dependency trees to get all installed modules. Map network functions to dependencies. Guess what activities are happening based off of functionalities of underlying stdlib libraries where used.

Let's then expand upon that and add dynamic analysis.

## People

- John Whiteman was planning on writing collectors and analyzing AST
- Michael could help us generate PDFs from Sphinx sites
- 

## Checklist

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