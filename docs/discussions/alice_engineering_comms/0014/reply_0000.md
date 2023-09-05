## 2022-08-30 @pdxjohnny Engineering Logs

- SCITT
  - Responded to review from Henk
    - Questions around meaning of term "file-based"
      - The intent of using the term "file-based" was to have an example working with a static serialized form rather than working with a dynamic abstraction layer such as HTTP.
    - Updated both lines based on Henk's feedback into one line which addresses the core concern around ensuring the documentation is complete so we end up with a higher likelihood of solid implementations.
      - > HTTP-based REST API for Request-Response Interactions including a critical mass of examples as implementation guidance
    - https://github.com/ietf-scitt/charter/pull/21#pullrequestreview-1089717428
- Game plan
  - [x] `alice please contribute`
  - [x] Contribution ready
  - [ ] Demo on stream of how write install and publish a third party overlay
    - Have the overlay be a function which outputs a return type of `ContributingContents` and takes the name of the project given in a `CITATIONS.cff` file of the CONTRIBUTING example.
    - https://github.com/johnlwhiteman/living-threat-models/blob/c027d4e319c715adce104b95f1e88623e02b0949/CITATION.cff
    - https://www.youtube.com/watch?v=TMlC_iAK3Rg&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=5&t=2303
    - https://github.com/intel/dffml/blob/9aeb7f19e541e66fc945c931801215560a8206d7/entities/alice/alice/please/contribute/recommended_community_standards/contributing.py#L48-L54
  - [ ] Demo on stream how to write install and contribute a 1st/2nd party overlay, the same code just not third party, from start to finish.
  - [ ] `alice shouldi contribute`
    - [ ] Support caching / import / export dataflows
    - [ ] Support query in easy way (graphql)
    - [ ] Support joining with previous runs / more sets of data
  - [ ] Contribute the data OpenSSF cares about to their DB via applicable joins and queries
     - [ ] Email Christine and CRob
- TODO
  - [ ] Organization
    - [ ] Daily addition by Alice to engineering log following template
      - [ ] Addition of old TODOs yesterday's logs
  - [ ] Export end state of input network / dump everything used by orchestrator
    - [ ] pickle
    - [ ] JSON
  - [ ] Ensure import works (check for state reset in `__aenter__()`, we probably need a generic wrapper to save the memory ones which populates after the `__aenter__()` of the wrapped object.
  - [ ] GraphQl query of cached state using strawberry library or something like that
  - [ ] Example docs for how to run a flow, then merge with static data as the start state for the cache and then query the whole bit with graphql
- TODO
  - [ ] How to Publish an Alice Overlay
  - [ ] How to Contribute an Alice Overlay
  - [ ] Rolling Alice: 2022 Progress Reports: August Status Update
  - [ ] Rolling Alice: 2022 Progress Reports: August Activities Recap

---

### How to Publish an Alice Overlay

- Metadata
  - Date: 2022-08-30 10:00 UTC -7
- Docs we are following
  - https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
  - https://github.com/intel/dffml/tree/alice/entities/alice#recommend-community-standards
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0002_our_open_source_guide.md

### How to Contribute an Alice Overlay

- Metadata
  - Date: 2022-08-30 10:00 UTC -7


### Rolling Alice: 2022 Progress Reports: August Status Update

- Metadata
  - Date: 2022-08-30 16:28 UTC -7
- https://www.youtube.com/watch?v=THKMfJpPt8I&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=9
- https://docs.google.com/presentation/d/1WBz-meM7n6nDe3-133tF1tlDQJ6nYYPySAdMgTHLb6Q/edit?usp=sharing
- https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866
  - Progress report transcripts
- Hello entities of the internet!
- We're building Alice, an Open Artificial General Intelligence, we invite you to join us.
- Today is Alice’s unbirthday. I’m going tell you a little bit about Alice and the Open Architecture and give a brief status update on where we’re at and how you can get involved.
- Who is Alice?
  - Alice will be our developer helper and one day a developer herself. She helps us understand and preform various parts of the software development lifecycle.
  - We currently extend her by writing simple Python functions which can be distributed or combined in a decentralized way.
  - She is built around a programming language agnostic format known as the Open Architecture.
  - Eventually we will be able to extend any part of her in any language, or have parts be driven by machine learning models.
- What is the Open Architecture?
  - It's the methodology that we use to interpret any domain specific description of architecture.
  - We are developing the open architecture so that we can do a one hop on analysis when looking at any piece of software from a security or other angle.
  - Having this generic method to describe any system architecture allows us to knit them together and assess their risk and threat model from a holistic viewpoint.
- Why work on the Open Architecture?
  - We want this to be a machine and human interpretable format so that we can facilitate the validation of the reality of the code as it exists in it's static form, what it does when you execute it, and what we intend it to do.
  - Intent in our case is measured by conference to and completeness of the threat model, and therefore also the associated open architecture description.
- The entity analysis Trinity
  - The entity analysis Trinity helps us conceptualize our process. The points on our Trinity are Intent, Dynamic Analysis, and Static Analysis.
  - By measuring and forming understanding in these areas we will be able to triangulate the strategic plans and principles involved in the execution of the software as well as it's development lifecycle.
  - We use the Trinity to represent the soul of the software.
- What happens when we work on Alice?
  - We build up Alice's understanding of software engineering as we automate the collection of data which represents our understanding of it.
  - We also teach her how to automate parts of the development process, making contributions and other arbitrary things.
  - Over time we'll build up a corpus of training data from which we'll build machine learning models.
  - We will eventually introduce feedback loops where these models make decisions about development / contribution actions to be taken when given a codebase.
  - We want to make sure that when Alice is deciding what code to write and contribute, that she is following our organizationally applicable policies. As outlined maybe in part via our threat model.
- Who is working on Alice?
  - The DFFML community and anyone and everyone who would like to join us.
  - Our objective is to build Alice with transparency, freedom, privacy, security, and egalitarianism as critical factors in her strategic principles.
- How does one get involved?
  - You can get involved by engaging with the DFFML community via the following links
  - Every time we contribute new functionality to Alice we write a tutorial on how that functionality can be extended and customized.
    - We would love if you joined us in teaching Alice something about software development, or anything, and teaching others in the process.
    - It's as easy writing a single function and explaining your thought process.
    - The link on the left will take you to the code and tutorials.
  - We are also looking for folks who would like to contribute from by brainstorming and thinking about AI and especially AI ethics.
    - The link on the right will take you a document we are collaboratively editing and contributing to.
- Now for a status update. (Progress to date)
  - Alice can make contributions, we've laid the foundations for the automation of the software development process.
  - Our next step is to help her understand what she's looking at, what is the code, how can she use the source Luke?
- Plans
  - As such our top priorities right now are
    - Ensuring the contribution process to what exists (`alice please contribute`) is rock solid.
    - Building out and making `alice shouldi contribute` accessible and ready for contribution.
    - Engaging with those that are collecting metrics (https://metrics.openssf.org) and ensuring our work on metric collection bears fruit.
  - Following our engagement on the metric collection front we will preform analysis to determine how to best target further `alice please contribute` efforts and align the two with a documented process on how we select high value targets so that others can pick up and run with extending.
  - Participating organizations in parallel begin automated outreach via Alice please contribute
  - Later we'll get into more details on the dynamic analysis portion of the Trinity, where we'll work, over time, across many program executions of the code we are working on, to understand how it's execution maps to the work that we're doing via our understanding of what we've done (`please contribute`) and what we we're doing it on (`alice shouldi contribute`).
- Unused
  - Alice's contribution docs have live for about a month. We're currently focused on making sure the contribution process works and is clear. Any and all feedback is appreciated.
  - After we're sure that Alice's contribution docs are solid we'll begin focus on her data mining capabilities.
  - We are building the entity at the center of the software/ entity analysis Trinity, Alice.
    - The `alice please contribute` command falls under the Static Analysis point on the trinity.
    - The Open Architecture, IETF SCITT, Web5, SBOM and other formats are all are used or plan to be used in top portion, Intent.
    - We are building the entity using the architecture. The intermediate and serialized forms of the Open Architecture will be use the represent the findings of our static and dynamic analysis.
- TODO
  - [x] Slide Deck

### Rolling Alice: 2022 Progress Reports: August Activities Recap

- Metadata
  - Date: 2022-08-30 10:00 UTC -7