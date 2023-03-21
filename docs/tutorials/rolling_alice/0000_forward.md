# [Rolling Alice: Forward](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_forward.md)

> Copy pastable bits for getting others involved in the project.

### Table Of Contents

- [Upstream](https://github.com/intel/dffml/tree/alice/entities/alice)
- [Rolling Alice](./)
- [Forward](0000_forward.md)
- [Preface](0000_preface.md)
- [Volume 0: Architecting Alice](0000_architecting_alice)
- [Volume 1: Coach Alice](0001_coach_alice)
- [Volume 2: Alice and the Art of Strategy](0002_alice_and_the_art_of_strategy)
- [Volume 3: Alice and the Strategy of Art](0003_alice_and_the_strategy_of_art)
- [Volume 4: Alice and the Health of the Ecosystem](0004_alice_and_the_health_of_the_ecosystem)
- [Volume 5: Alice's Adventures in Wonderland](0005_alices_adventures_in_wonderland)
- [Volume 6: Alice are you Rolling?](0006_alice_are_you_rolling)
- [Volume 7: Through the Looking Glass](0007_through_the_looking_glass)

## What's She Doing?

Alice is our reference maintainer who secures rolling releases.

## One Sentence

Alice is a methodology for secureing rolling releases.

## Elevator Pitch

We are writing a tutorial for an open source project on how we build an AI to work on the open source project as if she were a remote developer. Bit of a self fulfilling prophecy, but who doesn't love an infinite loop now and again. These are the draft plans: https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/ ~~first draft: https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280~~

Essentially we are going to be using web3 (DID, DWN), KCP (kubernetes API server), provenance and attestation, and automl with feature engineering for a distributed data, analysis, control loop. We'll grow contributors into mentors, and mentors into maintainers, and Alice will grow along with us.

The tutorial is how you use the open architecture entity analysis trinity problem solving model within any context, and we’re producing a buddy for you who at the end of the series can follow the methodology in any context or teach anyone how to.

## Alice is Here and Ready for Contribution! Gitter Announcement

- [Alice code](https://github.com/intel/dffml/tree/alice/entities/alice)
- [Rolling Alice: 2022 Progress Reports: July Activities Recap and Alice contribution setup](https://www.youtube.com/watch?v=JDh2DARl8os&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=1)

## Initial Gitter Announcement

> Alice, send the content within this section without this comment to Gitter 2022-05-11 09:00 PDT

We're [DFFML community] building a tutorial series where we as a community collaboratively build an AI software architect (named Alice). These docs https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/ are us trying to get some initial thoughts down so we can rework from there, maybe even re-write everything. We want to make sure we all start looking at the same picture of the future, consolidate all our efforts thus far and thoughts across efforts and individuals.

We have new GsoC mentors joining us and will soon have new students as well! We will publicize plan documents here for all to see, provide feedback on and review. We want to build these documents collaboratively as a team. Those who provide concrete feedback will be listed as reviewers via `Reviewed-by-tags`. Those who submit pull requests to edit the documents will be listed via `Co-authored-by` tags. We will map GSoC projects into this long term effort.

One of goals is to have Alice help us bring us up to the speed of the fully connected development model. To plug into the matrix. By working side by side with us, Alice will hopefully be able to detect when we've done things others on the team have done already and determined to be unsuccessful strategies. If Alice can do this we can all work independently while communicating asynchronously via Alice (our hopefully soon to be new contributor). We will work to make her detect in flight workstreams within a developer's train of thought through reporting of that developer on what they are working on. Alice I'm working on getting an HTTP request from Bob's service. Developer you may not want to do that, Bob's service is down, he told me he is working on fixing it, I can tell you when it's back online if you want.

## Alice: Artificial Life Is Coming Eventually

> Talk Abstract SKU 1

Given the inevitability of distributed AI we ask the question: How do we build it with intention? What would we find if we looked at it's threat model? What if it was it's own threat model? How does it defend against itself and other instances of itself? Most importantly, what would a system look like that we could cohabitate with?

Alice will join us for this talk as we flush out these questions conceptually. via our collective thoughts on what a system would look like that we could cohabitate with. We follow trains of thought to their logical conclusions when making predictions about the future. We implement and validate in order to ensure that a transparent entity with the collective's best interests at heart is ubiquitously adopted.

This talk will build on the talk: Living Threat Models are Better Than Dead Threat Models, presented at AppSecPWN. We'll dive into Alice, aka the Open Architecture, a methodology for communicating with intent with translation of risk mitigation into different operational contexts.

## The Consciousness Folks

> People who are into AI consciousness sort of things

We’re looking at consciousness with Alice aka the Open Architecture. Hoping we can take an open, community based approach to addressing issues with AI in implementation by collaborative development of context applicable policy overlaid onto entities.

Right now we are at the early stages. Please comment in this thread https://github.com/intel/dffml/discussions/1369#discussioncomment-2929904 or let me no directly if you want to be invited to the meeting. Or watch the linked comment for the meeting link.

Just FYI, this is not an official Intel project. Just a loose collection of folks wanting to get together and take action to ensure we can coexist effectively with Alice. We use Alice to describe "the machine" in the general sense. The end result of our work will hopefully be an AGI we can trust. Built with transparency, ethics, and security. One which understands human concepts. Would love to talk sometime if you’re interested.

We have been publicizing our work over technical channels and on twitter and gave a talk at AppSec days PNW which touched on Alice: https://www.youtube.com/watch?v=TMlC_iAK3Rg&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw [Living Threat Models Are Better Than Dead Threat Models By John L. Whiteman and John S. Andersen]. She’s just a dream at this point, nothing more than brainstorming and a pile of non-ML python code. The hope is that if we work together as humanity we can use proper planning to create a better world.

## Security Folks

Ready to bring security to the mind? https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice

Securing the software supply chain is becoming about securing the supply chain of the mind, the developer mind. We need to teach developers, and we'll be teaching developers in a language they understand, code. We'll teach them by teaching Alice how to teach them, along the way we'll build Alice, who will be a developer herself one day.

### Why might security folks want to be involved in the Open Architecture's definition and implemenation?

Anything accessible via the Open Architecture methodology as a proxy can be used to combine external/internal work with programmatic application of context and organizationally aware modifications to those components as they are sourced from an SBOM. This allows us to apply policy universally across static and dynamic analysis. This will allow us to apply techniques such as RBAC based on programming languague agnostic descriptions of policy at any level of granularity at analysis or runtime.

### Supply Chain Security

> CI/CD that goes really fast is effectivly distributed compute.

> [@lorenc_dan](https://twitter.com/lorenc_dan/status/1575090434333810688)
>
> This is the same as banks trading credit default swaps in the early 2000's without understanding the underlying credit risk.
> Software is tight knit and most orgs are using the same OSS, magnifying the risks, which are now existential to the industry and national security.

Holistic context aware risk analysis requires an understanding of a system's architecture, behavoir, and deployment relavent policy.

The [Open Architecture](https://github.com/intel/dffml/blob/alice/docs/arch/0009-Open-Architecture.rst) effort is looking at software description via manifests and data flows (DAGs) with additional metadata added for deployment threat modeling. Dynamic context aware overlays are then used to enable deployment specific analysis, synthesis, and runtime evaluation.

Leveraging the Open Architecture methodology we decouple the description of the system from the underlying execution environment. In the context of discussion around distributed compute we leverage holsitic risk analaysis during compute contract proposal and negotiation.

## Machine Learning

See https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md **TODO** vendor

## RFCv1 Announcement

Here is the first version of Alice aka the Open Architecture and this pull request is a Request For Comments https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice Please Review and provide any and all technical or conceptual feedback! This is also a call for participation if anyone would like to get involved and contribute please comment in the linked pull request or reach out to me directly. Looking forward to working with you all!

## Alignment

> "If we use, to achieve our purposes, a mechanical agency with whose
> operation we cannot interfere effectively … we had better be quite
> sure that the purpose put into the machine is the purpose which we
> really desire." [Norbert Wiener]

- References
  - https://en.wikipedia.org/wiki/AI_alignment#Research_problems_and_approaches

### Convey

> Definition of "convey": "To communicate; to make known; to portray." [Wiktionary]
> Synonyms of "convey": transport

We are working on the Thought Communication Protocol and associated
analysis methodologies (Alice, Open Architecture) so as to enable
iterative alignment of your AI instances to your strategic principles.
Enabling your AI to convey your way.

One of the considerations in our new shared threat model is the way AI conveys
information to us. In the future, automating communication channels (notes ->
phone call) will be the task of AI messengers. If the messenger paints a picture
worth a thousand words, we must ensure our target audiance is seeing the words
that best communicate the message we want them to get, aka, what's the point?
We also want to make sure that if we aren't able to describe the point, if we
have a misscommunication, that our AI has facilities baked in to avoid that
from being a really bad misscommunication.

From our shared threat model perspective, we must ensure we have methodolgies
and tooling baked into AI deployment infra. This way we ensure the AI does not
become missaligned with human concepts once it outgrows them. We must ensure
we can detect, prevent, and course correct from minipulation over any duration
of time from any number of agents.
