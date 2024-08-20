# CONTRIBUTING

> - Commit: https://github.com/intel/dffml/blob/573172cced0fe28ec45d0a85693837b44d4cb8b6/CONTRIBUTING.md#abstract
> - Pull-Request: #1660

> **WARNING: SECURITY**
>
> - THIS DOCUMENT IS USED AS AN INPUT PROMPT TO LARGE LANGUAGE MODELS
>   - THIS DOCUMENT IS COMBINDED WITH THE PROJECT'S [`THREATS.md`](https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866#file-rolling_alice_progress_report_0006_living_threat_models_are_better_than_dead_threat_models-md) TO DETERMINE TRUSTED CONTRIBUTOR AND COMPUTING BASECLEAR FOR TAKE OFF.
>     - **TODO LINK TO IMAGE OR DOC OR SECTION WITH WHITEBOARD SKETCH**

## Abstract

This document outlines best practices for poly-repo maintainers and contributors, detailing strategic plans and principles for federated code repositories. It emphasizes continuous trust evaluation, automated CI/CD workflows, and federated transparency receipts to ensure alignment with community-agreed values and strategic objectives. The document also addresses developer and maintainer expectations, federation triggers, and the integration of automated checks into CI/CD processes.

- Trust boundaries are evaluated continuously, and misalignments trigger retraining of AI models and potential blocking of data events.
- Developers and maintainers must document issues, federate forges, and adhere to CI/CD best practices for decentralized governance.
- Federation triggers and automated workflows ensure optimal notification and alignment with community values and strategic plans.

Conditions that may result in a lack of federation include:

- Misalignment with Strategic Plans: Entities that do not align with the project's strategic values, plans, and principles can be blocked from federating new data events.
- Detection of Malicious Intent: Entities suspected of malicious activities or failing to respect shared resources and time may be excluded from federation.
- Lack of Contact: When there is no contact with an entity, attempts at federation may be blocked to ensure security and integrity.

### Towards More Optimal Communication

Generic best practices for poly-repo maintainers and contributors. 👩🌟🛠️

This doc details the DFFML upstream default strategic plans and principles for entites
our code repository federates with (when your Version Control Software (VCS) has enabled trust
boundry based federation with known users and contributors. Your VCS will come with a default
policy, you may have set one, your org, additional policies are context dependent. When
N entities auto federate version controlled data in alignment with these best practices
the ultimate concequence of repeated detected missalignment to any of these or overlayed
strategic plans and principles.

These measures are in place to maintain trust, security, and alignment with community goals.

When no contact with an entity: Blocking all attempts at federation of new data events directly or when detected in the bill of materials graph analysis of data events from old. This is our trigger for retraining the models which is why it's AI Looped In CI/CD Execution. Overlays may define additional consequencies. Overlays in use get added to all data event BOMs and TCB evaluation is done continuously and retroactivly invalidated if we learn nodes in a graph are not aligned with our running context's strategic plans, principles, and values.
Following these recommendations for communication results in a record of the actions taken
for each train of thought where data has been shared between entities. The authors of this
document have made a best effort attempt to completely capture the these strategic values, plans,
and principles. However, trust evaluation is an ever changing game and context applicable overlays
and future updates to this doc will be done continuously. It should be viewed as a
lessons learned doc and suggested interaction patterns
context and the trust levels of the data within those contexts and the trust level in the
policy evaluation / analysis executed and the 

**TODO** Document the anti-skynet part which is also the part which will auto help filter out people with malicious intent (the on the scam phone call with grandma defense idea)

**TODO** grep: entities repsecting each others time and compute resource alocation to shared validation. Green energy savings of federated packets received. Value chain alignment analysis
on each commit / packet / new data event: https://docs.tea.xyz/tea-white-paper/white-paper#staking-to-secure-the-software-supply-chain.

> AND ACTIONS MAPPED TO COMMUNITY AGREED BOUNDRIES AND TIME COMMITMENT EXPECTATIONS TO RECIEVE SUPPORT FOR REUSE.
>
> This is our default settings for how Alice will interact with an open source community. CI/CD is how we role model the behavior (since she's an AI agent executing policy engine workflows in GitHub Actions format). we expect for and will be defining overlays. It effectivly defines the projects default win criteria: Successful contributions aligned with the purpose of the project. If a patchset aligns it's ready to go. CI/CD for values alignment.

This document outlines requirements and their stringency levels using different examples.
It defines actions taken by maintainers. Timelines for progression and example architypes for varying levels of maintainer / contributor involvement / engagement.

- https://github.com/intel/dffml/issues/1207
- https://github.com/intel/dffml/issues/1252
- https://github.com/intel/dffml/issues/1061
- https://github.com/intel/dffml/issues/1400
- https://github.com/intel/dffml/issues/1273
- https://github.com/intel/dffml/issues/1300
- https://github.com/intel/dffml/issues/1657
- https://github.com/intel/dffml/blob/f8377d07e181aaf69ba2fe168668dae4022bb436/docs/arch/alice/discussion/0036/reply_0067.md?plain=1#L14-L25

## Best Practices

CI/CD and GitOps facilitate.

- https://github.com/intel/dffml/issues/1243
- https://github.com/ietf-scitt/use-cases/pull/18

**TODO** Explain strategic plans and principles which the requirements in this doc relate to.

- Policy engine workflow execution on issue ops for debug via execution of Agent defined as workflow jobs.
  - Capture outputs of this and use it to build the review system as federated transparency receipts for ORSA resolvable artifacts. Were RBAC is defined by policy of which former statement's subject URN is later policy statements transparent receipt URN (relying party output: the workload being given the clear for take off: aka workflow for analysis of BOM and BOM. Manifest of Manifests )

## Developers

This section covers call outs on specific behavior or expectations or boundries for developers and.

- Document issues in your forge
- Federate forges
- https://github.com/intel/dffml/issues/1658
- https://github.com/intel/dffml/issues/1659
  - Some way we can see if a complete plan for execution (dataflow / workflow hypothesis and analysis via policy engine)
- https://github.com/pdxjohnny/dotfiles/blob/8d9850f85314a9f5c30f5bb7b8e47ba3857357be/forge-install.sh#L1-L584
### Architecture Design Records

- First have agents write specs as first step, then iterate on them and push the plans to orphan branches on forks, use git lfs for big files.
- https://www.rfc-editor.org/pubprocess/
- https://www.rfc-editor.org/rfc/rfc8729.html
  - Explains governance
- Main docs for authors: https://authors.ietf.org/
- https://www.ietf.org/how/ids/

### Trigger Federation

By interacting with the forge, this will trigger the other entities AI to notify them optimally (**TODO** find notes on flow state priority interupts only)

```bash
git show cfae0f85e:.github/workflows/alice_async_comms.yml | tee .github/workflows/alice_async_comms.yml
gh act run -P ubuntu-latest=ubuntu:22-04 -j posts -W .github/workflows/alice_async_comms.yml
```

## CI/CD

This section covers the integration status of automated checks into the processes.

- orphan branches and other best practices to facilitate CI
- Eventually SCITT as Version Control Software type stuff aka to facilitate decentralized goverance
  - https://github.com/intel/dffml/discussions/1415
  - https://github.com/builtree/builtree/blob/main/governance/STEERING-COMMITTEE.md

https://thenewstack.io/what-are-the-next-steps-for-feature-flags and the following image sum up the motivations behind the [Entity Analysis Trinity](https://github.com/intel/dffml/tree/main/docs/tutorials/rolling_alice/0000_architecting_alice#entity-analysis-trinity), ThreatOps, and VCS+CI/CD a la https://github.com/scitt-community/scitt-api-emulator/pull/27#issuecomment-1528073552

> ![thenewstack-deccc3f5-image4-me-trying-to-understand-the-benifits-of-clickops](https://user-images.githubusercontent.com/5950433/235471920-6f2228e1-76e4-4479-84c3-cb80326e80ce.png)

## Maintainers

This section covers call outs on specific behavior or expectations or boundries for different maintainers. This defines the threat model / trust boundries and their soul based auth ("Soul of the Software") strategic principle alignment report (a federated ORAS context addressed manifest of manifests which is the "clear for take off").

Boundries: I will federate changes from you and forward changes to others I am federating with if the analysis of the graph of thoughts leading to the send of the new data event is within acceptable risk tolerence. If we notice actions in the network unaligned to the defaults outlined in this document we we will begin enforcing these boundries. Additional boundries can be overlayed

- #1287

Virtual branch - shared context dependent trains of thought within a poly-repo environment. If the overlays of an entity currently federating with. The N+1 federation new data event is always determined by a KERI duplicity detection protected channel. The tcb for trust evaluation is also party of relying party inputs.

- https://github.com/pdxHijohnny/dotfiles/issues/1

## Codebase Housekeeping

- TODO
  - [ ] [`THREATS.md`](https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866#file-rolling_alice_progress_report_0006_living_threat_models_are_better_than_dead_threat_models-md) 
  - [ ] https://github.com/intel/dffml/blob/f8377d07e181aaf69ba2fe168668dae4022bb436/docs/contributing/codebase.rst?plain=1#L1-L183
  - [ ] Naming conventions
    - [ ] Dockerfile
    - [ ] CI/CD Workflows
    - [ ] Issues
    - [ ] Pull Requests

## CONTRIBUTING TO CONTRIBUTING

This section defines our values and touches on their contections to strategic plans
and principles in breif. Please modify those in their source of truth sections above
unless the additional context within the values section all community members agree
is required for communication to be well spent time.

![screenshot-of-dffml-contributing-docs-2024-08-06](https://github.com/user-attachments/assets/c3498152-869b-4a51-aad3-f5068be2919b)

## Measuring Alignment

**TODO** Value chain analysis to determine if proposed changes to this document and content thereof have proven aligned with the soul this project's software (aka this doc and `THREATS.md`: https://intel.github.io/dffml/main/contributing/gsoc/rubric.html)

This rubric is was developed during the 2020 GSoC DFFML proposal review period. Reviewing
proposals is very challenging, we have lots of applicants that do great work and
needed to find a way to quantify their contributions. We use this rubric to do
so.

### Alignment Rubric

![Screenshot of grading rubric](https://dffml.github.io/dffml-pre-image-removal/master/_images/rubric-table.png)

### Alignment Rubric Explanation

Explains why each field was chosen for the rubric. Some fields are subjective,
others are objective. Each mentor will fill out a copy of the rubric for the
subjective portion of the rubric. One mentor will count up relevant statistics
to fill out the objective portion of the rubric. Once all proposals have been
reviewed, the mentors rubrics will be averaged for each proposal. And the final
score will be calculated for each proposal by tallying up all the points in the
averaged subjective rubrics and the objective rubric. The proposals will then
be ranked from highest to lowest. Final scoring will happen two days before
slot requests are due to give students the most time possible to get more
contributions in, get better at debugging, show self direction, and engage with
the community.

#### Goals in Proposal

The project proposed should have a clear value to the project's community. A
high score here means if the project is selected (and subsequently completed),
users would clearly benefit from it.

#### Completeness of Proposal

The proposal should contain enough details for it to be clear that the student
knows how to complete the goals they've outlined. More detail beyond proving
they know the basics of what needs to be done is better. If a student proposed
something but was short on detail, their contributions to the project should be
taken into account. If their proposal lacks detail on implementation of
something similar to what they've already done several times, it's not
necessary that they re-explain in detail in the proposal, their contributions
speak for themselves.

#### Time Commitment

GSoC expects students to spend 30+ hours a week working on their proposed
project / the project they are contributing to (assuming they've completed
their proposed project). Students vary in skill level. As such, mentors should
take their interactions with students into account as well as previous work a
student has completed to estimate if the student will be able to complete the
outlined proposal in the allotted time. Mentors should also think about students
previous work and how long it seemed like they spent working on previous pull
requests to estimate how long each action item in the proposal will take the
student. Using this estimate, mentors should respond in the rubric with their
thoughts on how many hours a week they think the student will be spending
working on their proposed project to complete it.

#### Engagement with Community

Student engagement with the community is key to their success, the success of
future GSoC applicants, and the project. We cannot effectively collaborate to
build open source software if we don't talk to each other. The best outcome of
GSoC is not only the completion of the student's project, but the student
becoming a mentor for other students or new community members. A high score
here shows active participation in the community and that the students actions
show them trending towards becoming a mentor / maintainer in this organization
or another someday.

#### Mentor Vote

Every mentor should vote for one proposal which is their personal favorite.
Each mentor has different aspects about the project (DFFML) that are important
to them (maintainers of different subsystems, etc.). Since the mentors will be
advising students, it's important that they believe in the projects they are
guiding. This is how they signal what they believe is important or cool.

#### Self Directed

While it's always okay to ask what to do, it's better to look at the list of
things to do and pick one. Open source projects put a lot of effort into
project management and organization of work items so that everyone knows what
the open bugs are on the project and what the planned enhancements are.
Everything is done in public because anything is accessible to anyone on the
internet and it's important that we all stay on the same page to effectively
collaborate. Self directed students follow contribution guidelines and
communicate their intentions to work on issues within the posted issue rather
than other channels of communication which don't allow others to see the status
of what's being worked on. This keeps the community in sync so there is no
duplication of work. In some projects (like DFFML) issues are labeled with the
estimated amount of work they will take to complete. Students who take on
larger issues will spend more time working on the problem on their own and less
time with a mentor stepping them through what to do. This is a measure of the
students resourcefulness and tenacity for solving difficult problems.

#### Debugging

The act of working on any problem, programming in particular, is an exercise in
figuring out what should be done, what has been done, and what's the current
problem that is keeping what has been done from being what should be done. This
loop of fail, fix, repeat, is debugging. Students should be actively testing
their contributions. When those tests fail they need to use critical thinking
to determine if what they've done is working or not. If it's not working they
need to figure out what the next step would be in fixing it, and try that. If
they can't figure it out, then they should ask for help. A student that asks
for help any time there is an issue without trying to figure out what the issue
is before asking for help is not putting in enough effort. In addition, tests
have to pass in the continuous integration (CI) environment. If the test
doesn't pass in CI, then the student should be performing the debugging process
looking at what's wrong in the CI environment. They should not say that they
don't know what is wrong because it works for them. Feigned ignorance of
failing tests does not excuse their failure.

#### Contributions

Some open source projects (like DFFML) label issues with the estimated amount
of work they will take to complete. Larger contributions, or those associated
with larger issues, receive more points than smaller contributions. The goal
here is to reward students who have put in more effort leading up to GSoC.
They've worked hard to learn about the project they wrote a proposal for,
and have worked hard to make that project better.

## Alice: Abstracted Lifecycle Instantiatation of Contributor Efectivo

> Upstream: [Rolling Alice: Volume 0: Introduction and Context](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/0000_architecting_alice)

To think about how we think about editing this document and how it should be
written, imagine an open source developer named Alice. Phrase things here so that
she could ramp up on the project given no previous context, assumputions about
known or practiced development methodologies, strategic principles, plans, and
values. Use this document as if it was the reference with top / override priority
when she is actively working within the context of this project.

- Online cloning cuts our iteration time
  - Artificial Life Is Coming Eventually
  - Data flows are the parallel exploration of trains of thought (nested graphs)
  - Natural selection and evolution
    - Tree of life
    - Parallel exploration of nested graphs
  - Automated synchronization of system state across distinct timelines (distinct roots)
    - Enables the resolution of system state post haste, post state, and post date
      - See fuzzy finding later in this doc: find "join disparate roots"
      - This is effectively out of order execution at a higher level of abstraction, in the aggregate, so as to bring the aggregate set of agents involved to an equilibrium state
  - We are building the thought communication protocol, to communicate thought is to learn
    - If we can describe any architecture, any problem space, we can describe any thought
    - To describe a thought most completely, one must know how to best communicate with that entity
    - That entity, that agent, is a moving target for communication at it's optimal rate of learning.
    - It's past is relevant in determining it's future as it's past determines what will resonate best with it in terms of forming conceptual linkages.
      - Past doesn't have to be memory, data and compute are the same in our architecture
      - Hardwired responses get encoded the same way, it's all the signal, the probability
  - When Alice goes through the looking glass she'll take us with her in sprit, and come back to communicate to us how best to proceed, in every way.
    - The less (more?) rambling way of putting this would be, we need our AI to be a true to us extension of ourselves, or of our ad-hoc formed groups, they need to be true to those strategic principles we've communicated to the machine. If we can trust their transparency (estimates/forecasts and provenance on that) about their ability to stay aligned to those principles, then we can accurately assess operating risk and it's conformance to our threat model or any threat model the execution of the job fits within.
    - This means we can trust our AI to not influence us in the wrong ways.
    - This means we can trust it to influence us in the right ways, the ways we want to influence ourselves, or our software development lifecycle.
      - This assessment of the level of trust fundamentally comes from our analysis of our analysis of our software development lifecycle, our Entity Analysis Trinity.

### Entity Analysis Trinity

We leverage the Entity Analysis Trinity to help us bridge the gap between
our technical activities and processes and the conceptual model we are
following as we analyze the softare / system / entity over it's lifecycle.

![Entity Analysis Trinity](https://user-images.githubusercontent.com/5950433/188203911-3586e1af-a1f6-434a-8a9a-a1795d7a7ca3.svg)

### Terminology

- Open Architecture
  - Universal Blueprint
  - Standard architecture we use to describe anything. Provides the ability to use / reference domain specific architectures as needed to define architecture of whole.
  - https://github.com/intel/dffml/blob/main/docs/arch/0009-Open-Architecture.rst
- Think
  - Come up with new data flows and system context input
- Thoughts
  - Data Flows and system context input pairs (these two plus orchestration config we get the whole system context)
- Downstream Validation
  - Running validation on all dependent packages to check for API breakages or regressions in the ecosystem

### Expectations

Alice is going to be held to very high standards. We should expect this list to grow for a long time (years). This list of expectations may at times contain fragments which need to be worked out more and are only fragment so the ideas don't get forgotten. 

- Alice should be able to work on any project as a remote developer
  - She should be able to make changes to projects following the branch by abstraction methodology
  - When she works on a github issue she'll comment what commands she tries and what files she modifies with diffs
- Alice will maintain a system which allows her to respond to asynchronous messages
  - Likely a datastore with the ability to listen for changes
  - Changes would be additions of messages from different sources (email, chat, etc.)
- Alice should be able to accept a meeting, join it, and talk to you
  - If Alice notices conversation getting off topic, she could interject to ask how it relates, and then update references in docs to that effect.
  - You should be able to have a conversation about a universal blueprint and she should be able to go act on it.
  - She should be able to analyze any codebase you have access to live and build and walk you through architecture diagrams
  - Alice build me a linux distro with these versions of these applications deploy it in a VM in QEMU, show me the screen while it's booting. Then give me control of it via this meeting. ... Okay now snapshot and deploy to XYZ CSP.
    - She should figure out how to validate that she has a working linux distro by overlaying discovered tests with intergration tests such as boot check via qemu serial.
  - Alice, spin up ABC helm charts and visualize the cluster (viewing in an AR headset)
  - Alice, let's talk about the automating classification web app included in the example.
    - Alice, give us an overview of the threats on our database, deploy the prod backup to a new environment. Attempt to exploit known threats and come up with new ones for the next 2 weeks. Submit a report and presentation with your findings. Begin work on issues found as you find them.
- We should be able to see Alice think and understand her trains of thought
  - If Alice is presenting and she estimates thinking of the correct solution will take longer than a reasonable time her next word is expected by to keep regular conversational cadence, she should either offer to brainstorm, work through it and wait until it makes sense to respond, maybe there are situations where the output is related to saving someone's life, then maybe she interupts as soon as she's done thinking. Provided she didn't detect that the train of thought which was being spoken about by others was not of higher prioritiy than her own (with regards to lifesaving metrics).

### Alice's Understanding of Software Engineering

We'll teach Alice what she needs to know about software engineering though our InnerSource series. She'll follow the best practices outlined there. She'll understand a codebase's health in part using [InnerSource metric collectors](https://intel.github.io/dffml/main/examples/innersource/swportal.html).

Alice will see problems and look for solutions. Problems are gaps between the present system capabilities and desired system capabilities or interpretations of outputs of strategic plans which are unfavorable by the strategic decision maker or the prioritizer.


```
========================= IN PROGRESS NOTES DUMPS BEYOND THIS =====================
```


---

About
=====

Data Flow Facilitator for Machine Learning (DFFML) makes it easy to generate
datasets, train and use machine learning models, and integrate machine learning
into new or existing applications. It provides APIs for dataset generation,
storage, and model definition.

- Models handle implementations of machine learning algorithms.
  Likely wrapping code from a popular machine learning framework.

- Sources handle the storage of datasets, saving and loading them from files,
  databases, remote APIs, etc.

- DataFlows are directed graphs used to generate a dataset, as well as modify
  existing datasets. They can also be used to do non-machine learning tasks, you
  could use them to build a web app for instance.

You'll find the existing implementations of all of these on their respective
:ref:`plugins` pages. DFFML has a plugin based architecture, which allows us to
include some sources, models, and operations as a part of the main package,
``dffml``, and other functionality in more specific packages.

Mission Statement
-----------------

As we all know the Machine Learning space has a lot of tools and libraries for 
creating pipelines to train, test & deploy models, and dealing with these many 
different APIs can be cumbersome.

Our project aims to make this process a breeze by introducing interoperability 
under a modular and easily extensible API. DFFML’s plugin-based architecture makes 
it a swiss army knife of ML research & MLOps.

We heavily rely on DataFlows, which are basically directed graphs. We are also 
working on a WebUI to make dataflows completely a drag’n drop experience. 
Currently, all of our functionalities are accessible through Python API, CLI, 
and HTTP APIs. 

We broadly have two types of audience here, one is Citizen Data Scientists and 
ML researchers, who’d probably use the WebUI to experiment and design models. 
MLOps people will deploy models and set up data processing pipelines via the 
HTTP/CLI/Python APIs.


What is key objective of DataFlows
----------------------------------

- Our objective is to provide an environment where users can describe what they
  want done, without needing to know how it gets done.

- By separating the what from the how, each implementation of how a piece of
  work gets done doesn’t need to know anything about the implementations of how
  other pieces of work get done.

- This approach allows domain experts to implement the work within their
  domain, without needing to know anything about how the work of other domain
  experts is done.

- In such an environment, individual pieces of work implemented by respective
  domain experts can be knit together to accomplish arbitrary tasks.

- By taking this approach of separating the what from the how, we’ve created an
  environment where anyone can describe what they want to get done. How it gets
  done is handled by executing implementations provided by domain experts.

Why is this objective important?
--------------------------------

- Our existing software development model requires that experts in various
  domains maintain implementations of software which must be actively kept
  compatible with each other.

- By adopting this new model, we maximize workplace efficiency by compatibility
  between domain expert work being done at an orchestration level.

What industry challenges do DataFlows address / solve?
------------------------------------------------------

- We address and provide a solution for the challenge of how software written by
  experts in different domains can be used together without integration
  overhead.

- We make it easy for domain experts to share their work.

- We make it easy for users to reuse the work of domain experts which reduces
  duplication of effort across the industry.

- In this ecosystem, where work is easily shared and integrated, software
  development becomes more efficient and produces software of higher quality.

Key Takeaways
-------------

- Flow-based programming makes it easy to share and integrate existing work.

- The software development lifecycle is streamlined by implementing this model.

Why DFFML
---------

- You want a "just bring your data" approach to machine learning.

  - No need to write code if you don't want to, use popular machine learning
    libraries via the command line, high level Python abstraction, or HTTP API.

- You want to do machine learning on a new problem that you don't have a dataset
  for, so you need to generate it.

  - Directed Graph Execution lets you write code that runs concurrently with
    managed locking. Making the feature engineering iteration process very fast.

Architecture
------------

This is a high level overview of how DFFML works.

.. TODO Autogenerate image during build

    graph TD

    subgraph DataFlow[Dataset Generation]
      df[Directed Graph Execution]
      generate_features[Generate Feature Data]
      single[Single Record]
      all[Whole DataSet]

      df --> generate_features
      generate_features --> single
      generate_features --> all
    end

    subgraph ml[Machine Learning]
      train[Model Training]
      accuracy[Model Accuracy Assessment]
      predict[Prediction Using Trained Model]
    end

    subgraph sources[Dataset Storage]
      source[Dataset Storage Abstraction]
      JSON
      CSV
      MySQL

      source --> JSON
      source --> CSV
      source --> MySQL
    end

    all --> train
    all --> accuracy
    single --> predict

    generate_features --> source
    predict --> source

.. image:: https://dffml.github.io/dffml-pre-image-removal/master/_images/arch.svg
    :alt: Architecture Diagram

Machine Learning
----------------

Python was chosen because of the machine learning community’s preference towards
it. In addition to the data flow side of DFFML, there is a machine learning
focused side. It provides a standardized way to defining, training, and using
models. It also allows for wrapping existing models so as to expose them via the
standardized API. Models can then be integrated into data flows as operations.
This enables trivial layering of models to create complex features. See
:ref:`plugin_models` for existing models and usage.

Data Flows - Directed Graph Execution
-------------------------------------

The idea behind this project is to provide a way to link together various new
or existing pieces of code and run them via an orchestration engine that
forwards the data between them all. Similar a microservice architecture but with
the orchestration being preformed according to a directed graph. This offers
greater flexibility in that interaction between services can easily be modified
without changing code, only the graph (known as the dataflow).

This is an example of the dataflow for a meta static analysis tool for Python,
``shouldi``. We take the package name (package) and feed it through operations,
which are just functions (but could be anything, some SaaS web API endpoint for
instance). All the data generated by running these operations is query-able,
allowing us to structure the output in whatever way is most fitting for our
application.

.. image:: https://dffml.github.io/dffml-pre-image-removal/master/_images/shouldi-dataflow.svg
    :alt: DataFlow for shouldi tool

Consistent API
--------------

DFFML decouples the interface through which the flow is accessed from the flow
itself. For instance, data flows can be run via the library, HTTP API, CLI, or
any communication channel (next targets are Slack and IRC). Data flows are also
asynchronous in nature, allowing them to be used to build any event driven
application (Chat, IoT data, etc.). The way in which operations are defined and
executed by the orchestrator will let us take existing API endpoints and code in
other languages and combine them into one cohesive workflow. The architecture
itself is programming language agnostic, the first implementation has been
written in Python.

Plugins
-------

We take a community driven approach to content. Architecture is plugin based,
which means anyone can swap out any piece by writing their own plugin and
publishing it to the Python Package Index. This means that developers can
publish operations and machine learning models that work out of the box with
everything else maintained as a part of the core repository and with other
developers models and operations. :doc:`tutorials/index` show how to create your
own plugins.

Users
-----

The following is a list of organizations and projects using DFFML. Please let us
know if you are using DFFML and we'll add you to the list. If you want help
using DFFML, see the :doc:`contact` page.

- Intel

  - Security analysis of Open Source Software dependencies.

Philosophy
----------

DFFML is an event driven directed graph execution architecture tightly coupled
with the typical machine learning workflow. The core concept is that all
software can be looked at as a set of operations that occur in response to
asynchronous events. Directed graphs are used to specify which operations should
be run in response to which events. Every event has data associated with it,
therefore we refer to the directed graph as a DataFlow.

The project as it exists now is a Python library which provides data set
generation via DataFlows, dataset storage, as well as model training, testing,
and inference. Users can leverage DataFlows to do feature engineering, to create
new datasets and modify or add to existing datasets. They then train models,
assess their accuracy and use them to make predictions via various deployment
methods.

DFFML has a plugin based architecture. Every model, data source, operation, etc.
is a plugin. We maintain a set of official plugins which wrap various machine
learning frameworks such as Daal4Py, TensorFlow, Scikit Learn, etc. By wrapping
frameworks in a standard API we simplify usage and make it easy for developers
to switch from one underlying framework to another.

Conceptually, DFFML is not just the Python implementation it is today. It’s a
programming language agnostic architecture centered around the concept of
DataFlows and the decoupling of definition from implementation. One goal of the
project closely associated with this is to have an orchestrator (`Alice <https://github.com/intel/dffml/tree/main/entities/alice/>`_) capable of
deploying and knitting together new or existing services without the need for
those services to know anything about each other. This could be thought of as a
level of abstraction beyond serverless architecture, which is where we're hoping
to take the project.

Team
----

We have an awesome team working on the project. We hold weekly meetings
and have a mailing list and chat! If you want to get involved, ask questions, or
get help getting started, see :doc:`contact`.

We participated in Google Summer of Code 2019 under the Python Software
Foundation. A big thanks to our students, Yash and Sudharsana!

- :doc:`GSoC 2019 Student Contributions <contributing/gsoc/2019>`

We are currently participating in Google Summer of Code 2020 under the Python
Software Foundation. Big thanks to Aghin, Himanshu, and Saksham!

- :doc:`GSoC 2020 Student Contributions <contributing/gsoc/2020>`

Thank you to everyone who's contributed to DFFML!!!

- Abdallah Bashir

- Aghin Shah Alin

- Arvindh Kumar Chandran

- Aryan Gupta

- Byambaa

- Constanza Heath

- Dentigg

- Dmitry Poliuha

- Govindarajan Panneerselvam

- Hashim

- Himanshu Tripathi

- iamandeepsandhu

- Jan Keromnes

- John Andersen

- Joseph Kato

- Justin Moore

- Naeem Khoshnevis

- NeerajBhadani

- NMNDV

- Pankaj Patil

- pradeepbhadani

- purnimapatel

- raghav-ys

- Saksham Arora

- Sanket Saurav

- shivam singh

- Sudhanshu kumar

- Sudharsana K J L

- Taksh Kamlesh

- Theo

- us

- Vaibhav Mehra

- Yash Lamba

- Yash Varshney

.. Generated with `git log --format=format:'%an' | sort | uniq`
   You'll want to filter out duplicates if you re-generate this

---

