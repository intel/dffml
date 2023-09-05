## 2023-01-05 Alfredo/John Chat

> @agalvare: we also need a voting mechanism, and a way for other to train it

https://github.com/intel/dffml/blob/alice/docs/arch/alice/discussion/0023/reply_0022.md this plus the ATProto means we are piggybacking off of "social network". This way humans and AI and work together.

> The smart contract is able to make its own decisions based on learned experience (models) so as to continue to operate until its strategic goals are meet. As measured by oracle data ordained from trusted parties as is applicable to context. Where chains of trust are established via Peer DIDs between entities and data for provenance. Leveraging verifiable credentials (opencert) for review system to measure risk in absence of attestation.

We "reply" to "posts" where a post is an AIs idea which we might execute in CI/CD and the reply contains the "review" with how well some grading AI thinks that execution (within CI) aligns to the goals of the prompt (validate X).


---

https://github.com/w3c/cogai/pull/47

> We think about an entity (Alice is our reference entity) as being in a set of parallel conscious states with context aware activation. Each context ideally forms a chain of system contexts or train of thoughts by always maintaining provenance information ([SCITT](https://scitt.io/), [GUAC](https://security.googleblog.com/2022/10/announcing-guac-great-pairing-with-slsa.html)). She thinks concurrently in the existing implementation where she is defined mostly using the Open Architecture, which is language agnostic focused on defining parallel/concurrent flows, trust boundaries, and policy. The current execution of orchestration is done via Python, but is indented to be implemented in whatever language is desired.
> 
> Alice doesn't use any machine learning yet, but later we can add models assist with automation of flows as needed.
>
> Alice's architecture, the [Open Architecture](https://github.com/intel/dffml/tree/alice/docs/arch/0009-Open-Architecture.rst), is based around thought. She communicates thoughts to us in whatever level of detail or viewed through whatever lens one wishes. She explores trains of thought and responds based on triggers and deadlines. She thinks in graphs, aka trains of thought, aka chains of system contexts. She operates in parallel, allowing her to represent N different entities.

The "thinking in parallel" means we'd run multiple models (such as nanoGPT) and then choose the best result of them by the deadline.