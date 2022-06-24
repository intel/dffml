# [Volume 0: Architecting Alice: Forward](https://github.com/intel/dffml/discussions/1369#discussioncomment-2688532)

> Copy pastable bits for getting others involved in the project. 

### Table Of Contents

#### Volume 0: Architecting Alice

- [Forward](https://github.com/intel/dffml/discussions/1369#discussioncomment-2688532)
- [Preface](https://github.com/intel/dffml/discussions/1369#discussion-4023096)
- [Introduction and Context](https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280)

#### Volume 1: Alice's Adventures in Wonderland

- [Down the Rabbit-Hole](https://github.com/intel/dffml/discussions/1369#discussioncomment-2663771)

## Elevator Pitch

We are writing a tutorial for an open source project on how we build an AI to work on the open source project as if she were a remote developer. Bit of a self fulfilling prophecy, but who doesn't love an infinite loop now and again. These are the draft plans: https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280

Essentially we are going to be using web3 (DID, DWN), KCP (kubernetes API server), provenance and attestation, and automl with feature engineering for a distributed data, analysis, control loop.

## Initial Gitter Announcement

> Alice, send the content within this section without this comment to Gitter 2022-05-11 09:00 PDT

We're [DFFML community] building a tutorial series where we as a community collaboratively build an AI software architect (named Alice). These docs **TODO DOCS LINK ONCE WE HAVE ADRS** are us trying to get some initial thoughts down so we can rework from there, maybe even re-write everything. We want to make sure we all start looking at the same picture of the future, consolidate all our efforts thus far and thoughts across efforts and individuals.

We have new GsoC mentors joining us and will soon have new students as well! We will publicize plan documents here for all to see, provide feedback on and review. We want to build these documents collaboratively as a team. Those who provide concrete feedback will be listed as reviewers via `Reviewed-by-tags`. Those who submit pull requests to edit the documents will be listed via `Co-authored-by` tags. We will map GSoC projects into this long term effort.

One of goals is to have Alice help us bring us up to the speed of the fully connected development model. To plug into the matrix. By working side by side with us, Alice will hopefully be able to detect when we've done things others on the team have done already and determined to be unsuccessful strategies. If Alice can do this we can all work independently while communicating asynchronously via Alice (our hopefully soon to be new contributor). We will work to make her detect in flight workstreams within a developer's train of thought through reporting of that developer on what they are working on. Alice I'm working on getting an HTTP request from Bob's service. Developer you may not want to do that, Bob's service is down, he told me he is working on fixing it, I can tell you when it's back online if you want.

## Alice: Artificial Life Is Coming Eventually

> Talk Abstract SKU 1

Given the inevitability of distributed AI we ask the question: How do we build it with intention? What would we find if we looked at it's threat model? What if it was it's own threat model? How does it defend against itself and other instances of itself? Most importantly, what would a system look like that we could cohabitate with?

Alice will join us for this talk as we flush out these questions conceptually. via our collective thoughts on what a system would look like that we could cohabitate with. We follow trains of thought to their logical conclusions when making predictions about the future. We implement and validate in order to ensure that a transparent entity with the collective's best interests at heart is ubiquitously adopted.

This talk will build on the talk: Living Threat Models are Better Than Dead Threat Models, presented at AppSecPWN. We'll dive into Alice, aka the Open Architecture, a methodology for communicating with intent with translation of risk mitigation into different operational contexts.
