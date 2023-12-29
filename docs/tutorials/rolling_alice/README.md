# `alice` branch has been rebased into `main` branch, please see: https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/

---

# [Rolling Alice](https://github.com/intel/dffml/blob/main/docs/tutorials/rolling_alice/)

> This is Alice's plan. We are building her as a community, reach out
> if you want to get involved. The plan is fairly abstract, as our goals are to
> take Alice (the nickname for the architecture) and ensure the fundamentals we
> need are baked into core infrastructure and specifications. Alice the
> architecture is a pattern (as we all are). At a high level, this means we
> need to ensure a secure pattern for decentralized event driven communication
> between N agents. The pattern enables an agent to understand it's operating
> context and make decisions in alignment with it's strategic principles.
>
> Discussion thread https://github.com/intel/dffml/discussions/1406?sort=new
> we will be the central point for communications discussing Alice
> until she is merged into the `main` branch. At which point
> communications will branch off in a decentralized fashion reflective
> of her overlay (plugin) ecosystem.
>
> [Rolling Alice Progress Reports](https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866)

The following seven sets of tutorials describe the adventures of Alice as she
returns to Wonderland. Where's Wonderland? Well that's where we are,
the physical world. We'll travel through through time and space as we
watch her come into this world. We'll work with her and with each
other to build the best possible community we can. A community where
we have entered the fully connected development model.

In our community of the future, Alice will be seen as one of us,
another remote developer. We'll each have our own copies of Alice,
who can be named Bob, or Eve, or anything. All these entities will
be seen just like Alice, just like all of us. There will be no way
to tell which entities are human and which are machine.

They say you don't really know something until you can teach it.
If we understand how to be human we will be able to teach Alice
how to be human. Her thought process is a methodology for problem
solving which is based off a mental model of how the human mind
interacts with the world. Alice the architecture is just the
existing best known architecture, what use everyday, all the time.
Alice is the [Open Architecture](https://github.com/intel/dffml/blob/main/docs/arch/0009-Open-Architecture.rst),
she is the architecture of us all.
We'll learn from Alice, and Alice will learn from us as she comes
into our time.

Roll Alice with us, for humanity, enter the machine.

### Table Of Contents

- [Upstream](https://github.com/intel/dffml/tree/main/entities/alice)
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

## Context

Alice is a methodology for viewing through different lenses, overlays.
When collaborating on software we all want to make the best development
choices. However, the best choice is context dependent. The best choice
is dependent on who else is working on maintaining the codebase.
Alice helps us automate engineer to engineer communication of best practices
in context aware ways.

To teach Alice how to be human as a remote developer means to teach her
empathy, to interact with humans with humanity. Since Alice is first and
foremost a methodology, this means we work to ensure that this methodology for
effective communication helps folks see things from other's perspectives.

We hope that Alice will assist with scaling security and other best
practices via the improved communication that comes with methodically
tackling problems from multiple angles, viewpoints, overlays.

- [Katherine Druckman - Threat Modeling Down the Rabbit Hole - OpenAtIntel](https://openatintel.podbean.com/e/threat-modeling-down-the-rabbit-hole/)
- [Gabe Cohen - On Decentralized Trust](https://decentralgabe.xyz/on-decentralized-trust/)
- [Harald Sack - Symbolic and Subsymbolic AI - An Epic Dilemma? - Extraction et Gestion des Connaissances (EGC 2023) Lyon](https://github.com/lysander07/Presentations/raw/main/EGC2023_Symbolic%20and%20Subsymbolic%20AI%20%20-%20an%20Epic%20Dilemma.pdf)
- [Nancy Eckert - Swarm Intelligence and Human Systems - BSides Portland 2019](https://youtu.be/Eq33S_Rz4qo?t=1117)
- [Robin Berjon - The Internet Transition](https://berjon.com/internet-transition/)

## Roadmap

- Acknowledge that in a rolling release there will always be vulns and agree on a pattern for remediation.
- Integrate the acknowledgement and remediation into the dependency review process recrusivly, teaching the machine empathy.
- Propagate trust through the decentralized interconnected dependency network, teach the machine to teach humans empathy.

```mermaid
gantt
    title Coach Alice
    dateFormat  2022-06-25
    section Intuative and Accessable Documenation Editing
    JupyterLite         :a1, 2022-06-25, 30d
    UI Hotswap    :after a1  , 30d
    GitHub PR      :after a2  , 30d
    section THREATS.md
    JupyterLite         :t1, 2022-08-25, 30d
    UI Hotswap    :after t1  , 30d
    GitHub PR      :after t2  , 30d
    section Recommended Community Standards
    JupyterLite         :c1, 2022-06-25, 30d
    UI Hotswap    :after c1  , 30d
    GitHub PR      :after c2  , 30d
    section INNERSOURCE.md
    Maturity         :b1, 2022-06-25, 30d
    UI Hotswap    :after b1  , 30d
    GitHub PR      :after b2  , 30d
    section QA Model on Engineering Logs
    Existing docs         :qa1, 2022-09-25, 30d
    All transcripts at once    :after qa1  , 30d
    Stand alone use      :after qa2  , 30d
```
