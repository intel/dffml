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

Alice should be ready able to to analyze projects (repo or set of repos) and present threat models on those projects. She will create a slide deck by making a system context that gets executed to produce a PDF of the slides. The slides will use inputs from the threat model data. Threat models will be created as hybrid reStructuredText and markdown Sphinx sites (for mermaid diagrams rendering on GitHub by default, allow for using markdown). Ideally we’ll be able to have Alice read the content of the report (which will not be copied verbatim to slides, only graphics for each section will be copied to slides) while giving a presentation of the slide deck. 

This is in preparation for our upcoming second and third party plugin support. We'll later look to create CI jobs which keep the threat model documents up to date within each repo.

## Plan

shouldi is ripe for expansion. Let's see if we can pick a set of repos and make sure Alice can create basic threat models on them via pure static analysis. Build an SBOM, run CVE Bin Tool against it. Traverse dependency trees to get all installed modules. Map network functions to dependencies. Guess what activities are happening based off of functionalities of underlying stdlib libraries where used. In fact, we’ll be patching CVE Bin Tool to add support for checking more than one language effectively merging aspects of shouldi into cve-bin-tool. The goal is to leverage dffml for output plugin support and scanning overlays for organizational policies.

Our first step is to know what we're looking at, Python projects to start.
What are all their dependencies?

- https://github.com/intel/dffml/issues/596
  - https://github.com/anthonyharrison/sbom4python !!!
    - We should attempt to build a mermaid diagram via constructing a dataflow from the sbom of a project and then rendering it using the `dffml dataflow diagram` command or similar. We should start with known packages like `flask`, and classify using mappings of known packages to their function (HTTP server). Later we can do automated discovery of mappings based on deeper analysis.
    - https://www.youtube.com/watch?v=TMlC_iAK3Rg&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&t=2494s
      - https://github.com/johnlwhiteman/living-threat-models/blob/main/demo/ALICE.rst
  - https://github.com/anthonyharrison/lib4sbom
  - https://www.youtube.com/watch?v=D9puJiKKKS8&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&t=871s

## Notes

- Future
- TODO
  - [ ] Incude deps in `THREATS.md` / `alice threats`
