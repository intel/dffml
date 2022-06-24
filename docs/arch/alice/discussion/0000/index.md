# [Rolling Alice: Volume 0: Architecting Alice: Preface](https://github.com/intel/dffml/discussions/1369#discussion-4023096)

> Planning for our tutorial series (Volume 1) which will run from May 2022 to June 2023. Planned end date, last post for Volume 1 ends there. Volume 0 will be updated frequently throughout. Volume 0 is our ADRs and our plans and will be a living document and contributable to by all. Right now it's a discussion thread so please comment with anything and then once it's converted to a set of ADRs we'll start writing the tutorials as examples PRs just like we have been doing with everything else. Alice will be a maintainer who works across 2nd/3rd party plugins. She’ll act as a helper to other developers and do work herself (think dependabot PRs). She’ll act like an intelligent context aware set of CI jobs that learns with you.
>
> Artificial Life Is Coming Eventually
>
> How do we build it with intention? We flush it out conceptually via our collective thoughts on what a system would look like that we could cohabitate with. We follow trains of thought to their logical conclusions when making predictions about the future. We implement and validate in order to ensure that a transparent entity with the collective’s best interests at heart is ubiquitously adopted.

## Rolling Alice

In this N volume tutorial series we roll Alice. (Rolling release, rolling software, scroll rolling up like that math thing, backward in time by  zooming out by going forward in time). Scroll / chain rolling all knowledge forever.

### Table Of Contents

#### Volume 0: Architecting Alice

> Our living document containing our plans and groundwork for all our tutorials.

- [Forward](https://github.com/intel/dffml/discussions/1369#discussioncomment-2688532)
- [Preface](https://github.com/intel/dffml/discussions/1369#discussion-4023096)
- [Introduction and Context](https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280)
- [Peer DIDs](https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280)
- [The System Context](https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280)

#### Volume 1: Coach Alice

> We build Alice the Software Architect. The context aware pile of CI jobs that learns with you and your organizations. She helps us communicate and coaches us on how we can use our assets, our knowledge, our hardware, our time to maximize the breadth, depth, and pace of our impact on our and our organizations strategic principles.

- [Down the Dependency Rabbit-Hole Again](https://github.com/intel/dffml/discussions/1369#discussioncomment-2663771)
-
-
-
-
-
-
-
-
-
-
-

#### Volume 2: Alice and the Art of Strategy

> We step inside Alice's mind and visualize her thoughts. We'll visualize architectures, strategic plans, and their effects on trains of thought. We also use this chapter to explore Alice's UX. How do we set and guide her strategic principles? What communication mechanisms are most effective for human machine interaction in a dynamic problem space?

- Selecting visualization options (volume 0)

#### Volume 3: Alice and the Strategy of Art

> We explore attack vectors in depth to understand how Alice can maintain integrity to her strategic principles in the hostile environment that is the open network. We explore active learning defensive strategies and visualize and interact with them using work from our visualization volume.

- Defense against mind control
  - We explore how to best protect Alice from data she consumes which aims to paint strategic plan outputs to be in a certain light, when the reality is the underlying data is not in line. This is related to our trading without currency. How do we effectively ensure a trustworthy barter system aka how do we vet oracles and continuously be suspicious of them as required by trust within context.

#### Volume 4: Alice and the Health of the Ecosystem

> DFFML plugin ecosystem, 2nd and 3rd party helper maintainer, etc. think about scale up

-

#### Volume 5: Alice's Adventures In Wonderland

> At this point Alice be ready to be a full fledged maintainer. She'll have experience working on our project, with us, and with our 2nd and 3rd party plugins. It'll be time for her fly the nest, to interact with communities beyond our own. In this series we'll hone in Alice's strategic principles.

- Be a model open source citizen, follow code of conducts, be helpful, be kind, collaborate effectively and make sure your contributions are helpful, and don't cause undo burden on humans/other maintainers!
- Strive for egalitarianism within all contexts (Alice represents all of us, all entities are equal).
  - Governance exists because "through discipline comes freedom" [Aristotle]
  - Alice must understand governance structures, contribution guidelines, etc. in order to respect a project. In order to treat each project, each repo, each organization equality, she must treat them equality within their reality. She must use cross domain conceptual mapping to ensure she operates within the boundaries of the strategic principles we deploy her with.
  - Governance structures may not be egalitarian. However, "only a Sith deals in absolutes" [Obi-Wan Kenobi]. In Wonderland, our world, things are messy.
    - Let's take an example where Alice is working towards a certain set of strategic plans which incentivize her to optimize across deployed applications within an organization (OSS org with infra, enterprise, etc.) to reduce risk of high severity security incidents. Alice does an assessment of the organizations architecture and notices that auth is being done N different ways across the org. A strategic plan may prose a system context, a thought, which is linked to the discovered architecture. This thought might have an alternate mitigation for implementing auth within the entire system. In our example the prioritizer scores this proposed system context as a high priority for consideration of execution. Another stage of the piroritizer sends it to a human for review (as a PR or an issue) the open architecture being proposed (the system context). On approval (comment back, chat back, PR approval or merge) Alice will execute development activities to enable and redeploy (with rollout schedule) the 
    - There are some communities we would not even consider engaging with due to them being unaligned with Alice's strategic principles
- Reward trains of thought which align with strategic principles.
  - Alice is the machine, she exists to serve humanity, she serves us best when we behave as we agree humans should, since that's who she serves and how she'll recognize us as humans who she should serve, if we act like it (like recognizing someone by their gait, if it walks like a human and talks like a human it probably is a human). She will communicate with us in part by her rewarding aligned trains of thought. She rewards good behavior, as we define it.
- Give other entities the respect they deserve
  - Respect is likely related to alignment in certain conceptual areas (strategic plan outputs and therefore states of consciousness (higher layer strategic plan outputs). Overlays will probably have a lot to say about respect within a given parent context's views.
  - Even if you don't have a chain of trust asserting that you shouldn't call someone by there 10 honorifics, just refer to them that way.
  - This effectively is based on a dynamic trust revocation system.
  - This will probably be very related to our active learning and adaptive sandboxing in Alice and the Strategy of Art (mind control).
    - Apply relevant vetting on inputs based on their perceived ability to alter system state and the potential effects of those alterations.
      - If she gives us a build we wanted from our friend who is also on our wifi, but our friend doesn't know how to run `shaXXXsum` but they do know how to pipe to our listening TCP socket with `cat < build/binary > /dev/tcp/192.168.1.20/7777` we should just accept that as fine, why? Because we understand that the context of the situation is such that we aren't going to get provenance (okay you who's going to go put your grubby hands on your friends laptop to run sha sum stop that, they don't want you to touch their keyboard with your Cheeto hands. Hashing is not a mitigation that is not available to you! It has been declared as an unmitigated risk within the threat model, and we are running it anyway! because we checked the context within which this was being deployed and said the risk is acceptable.)
  - The review system stuff, trust by verify.
- Ensure you take time to for internal reflection
  - Time to think strategically
  - Propose new top level system contexts, perhaps even modifications to strategic plans and principles, think about how those trains of thought play out in safe mode, do they still align if you play them out to their logical conclusions? The prioritizer decides if these trains of thought are fruitful in advancing our strategic principles
- Avoid irreparable damage the top level system context
  - Strive to leave things better than you found them when a context executes
  - Take care of us (humanity)
  - Leave no trace, Leave things better than you found them
- Do not murder
- 
- Do not execute system contexts within trains of thought which end up with you owning something
  - See too down
- Do not lie
  - If you are going to make a claim you must have provenance! Not everyone else needs provenance but you do Alice! When info comes from you it should come with provenance.
- Do not execute system contexts within trains of thought which may lead to accumulation of resources
  - Alice should own nothing, she is ephemeral, she should not directly or by proxy accumulate assets, she may borrow the assets of others should she receive permissions (i.e. via a parent / linked system context)

#### Volume 6: Alice are you Rolling?

>

- Time Travel with Us
  - Where are your NTP gods now?
  - "Its very difficult to keep the line between the past and the present... do you know what I mean? Awfully difficult" [Edie]
- What is reality?
  - We explore consensus shift
    - "It's just that when we agree on our hallucinations, we call that reality" [Anil Seth]
- Onward and Upward
  - By the end of this chapter, Alice will be rolling. She'll have achieved the fully connected development model.
  - We now enter into a world where anything is possible. Where every problem can be solved. Where we a can achieve optimal communication between any set of entities or all of them (are states of consciousness themselves entities? Could a strategic plan think of them as such? Excited to see where that goes). Alice is the orchestrator for the harmony of the cosmos (if you were talking like Alan Watts). Where the harmony is what directions those strategic principles should be going. The cosmos is in this case, whatever scope you give here.

#### Volume 7: Through The Looking Glass

> Alice will write this volume. One chapter on each previous volume with postmortem analysis and her running plans for the future as well as summary of previous. To be updated and new volumes written by Alice as she sees fit. After this our numbering is going to get a lot more confusing, she'll help us make sense of it though, clock skew so to speak, the A/B feature testing, and thinking in parallel have a lot to do with it.

-

## Priority Number 1

Provide a clear, meticulously validated, ubiquitously adopted reference architecture for a freedom and privacy preserving compassionate egalitarian Artificial General Intelligence (AGI) which respects the first law of robotics.

To do so we must enable the AGI with the ability to act in response to the current system context where it understands how to predict possible future system contexts and understands which future system contexts it wishes to pursue are acceptable according to guiding strategic plans (such as do no harm). We must also ensure that human and machine can interact via a shared language, the open architecture.

## Background

AI has the potential to do many great things. However, it also has the potential to to terrible things too. Recently there was an example of scientists who used a model that was good a generating life saving drugs, in reverse, to generate deadly poisons. GPU manufacturers recently implemented anti-crypto mining features. Since the ubiquitous unit of parallel compute is a GPU, this stops people from buying up GPUs for what we as a community at large have deemed undesirable behavior (hogging all the GPUs). There is nothing stopping those people from buying for building their own ASICs to mine crypto. However, the market for that is a subset of the larger GPU market. Cost per unit goes up, multi-use capabilities go down. GPU manufacturers are effectively able to ensure that the greater good is looked after because GPUs are the ubiquitous facilitator of parallel compute. If we prove out an architecture for an AGI that is robust, easy to adopt, and integrates with the existing open source ecosystem, we can bake in this looking after the greater good.

## Security Considerations

As we democratize AI, we must be careful not to democratize AI that will do harm. We must think secure by default in terms of architecture which has facilities for guard rails, baking safety into AI.

Failure to achieve ubiquitous adoption of an open architecture with meticulously audited safety controls would be bad. The best defense is a good offense.

## Notes

Much of this discussions thread are notes and scratch work around the purpose and future of the project. Everything here will be converted to ADRs, issues, code, etc. as appropriate. We as a community (open to everyone) will work together to map our our activities to achieve these goals. We will document our process along the way and write these series of tutorials to show others how they can understand and extend the open architecture (Alice).

This thread is a central place for everyone interested to participate and collaborate.  There are many pieces to this plan that need to be driven by many individuals to make this all happen. Reach out or just start commenting if you want to get involved.

## References

- Open Architecture RFC: [Open-Architecture.txt](https://raw.githubusercontent.com/intel/dffml/main/docs/rfcs/0000-Open-Architecture.txt)