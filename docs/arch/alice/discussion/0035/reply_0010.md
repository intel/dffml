Are humans capable of dealing with this? This connection at the speed of Alice? See issues with social media.

Alice should be trustworthy. We’re going to tell her, do X. And need to trust her to get it done in a way we’d call “the right way”. That’s different for each of us. Different depending on our operational context for the problem being solved.

We are all the keymakers. Our domain expertise is the key to unlock more pathways, more trains of thought.

System context is like a chemical equation, on clock tick (reaction, execution, etc.) we move from the start system context to the end system context.

Single electron -> serial execution of system contexts. Are we watching one entity move through time? If we flatten parallel execution, is that what we get? Are we watching multiple entities move through time. Time itself is relative. In the end it doesn't matter. Not all system contexts are valid. Any system context can be thought of, hypothesized/(un)executed/(in)valid. Are the multiverses different ways of slicing different system contexts? Are they parent system contexts in which child system contexts are valid, but are not valid to other parents (universe being a parent system context). All of this is arbitrary, any of it is possible. No one can prove that this is not the case. No one will ever be able to prove that this is not the case. Therefore every system context is a valid system context, provided it has a parent system context it can be valid within. Since there are an infinite number of possible system contexts, every one must be valid. It just may not be valid in this universe. The universe being the top level system context. The top level system context may even be an input somewhere within the lowest level of the system context. Thereby making the whole bit sort of a circular reference. Time for instance, is relative to the top level system context. The speed at which things travel in a game can be scaled based on the speed to rendering (see use of [modifer](https://github.com/pdxjohnny/space/blob/b87d7ef49caec169f1f7432664e550f421a5d7de/sprite.js#L74-L77) via [game loop](https://github.com/pdxjohnny/space/blob/b87d7ef49caec169f1f7432664e550f421a5d7de/game.js#L106-L114) and `window.requestAnimationFrame()`).

We're all really just guessing at what future systems contexts will exist, or do exist outside of our immediate sphere of observation. Our brain extrapolates visuals due to constraints on signal processing (https://doi.org/10.1523/jneurosci.0275-20.2020). Alice is doing the same. Be the change you want to see in the world. Alice will.

Time is relative to similar system contexts. Perhaps even defined by the rate of execution within a parent system context.

10b parameter language model: https://github.com/bigscience-workshop/t-zero

Time travel: https://80.lv/articles/transforming-images-with-openai-dall-e-2/ take one system context and transform it into another system context

System for communication, a tool for effective organization in a anarchistic society, rules are context local (location based, tribe based, one belongs to many tribes). Helps people (agents, runners, compute) align activities to operational context constraints (rules) as well as individual and tribe based strategic plans

splitting out execution from analysis via caching of contexts is helpful with all of this. Can slice contexts different ways for different strategic plans (different plans consume different context Input objects in cached input network with system context)

- measure
- Change
- Correlate
- modify operating procedures accordingly
  - strategic plans
  - strategic decision mater
  - priroitizer
- Repeat

OpenSSF: Have DIDs been looked at to assist with data distribution/consumption? Allow users to add links to chains, data added to chain in such a way that the data is self descriptive (include schema ref with format name and version). Consumers can choose to follow links in chains from sources they trust. Data they consume could be via interfaces created from manifest schema. This approach allow for various data models, not enforcing a common one. It allows for natural convergence, tracking data models used by traversing chains to schemas. Visibility allows for fostering convergence, watch new use cases appear, converge, repeat. For example, NVD is frequently not enough, sometimes we need to check project websites to supplement CVE data. Projects themselves could self publish to data to relevant chains (or expose via any other interface, rss, whatever, not important, point is there is an standard interface which exposes these relevant pieces of data). How can we ensure we foster an open ecosystem for all relevant data? We need to enable entities and systems to publish any data they think may be relevant, and see what ends up really helping over time. Right now we think we know, but we haven't done this yet, so we don't really know what data helps us effectively secure across the industry and what doesn't. We're working with a cherry picked set of data models right now. By opening the distribution/consumption mechanisms we may find correlations we did not foresee.

`dffml dataflow c4models` - similar to dataflow diagram

With A/B field testing of new system contexts (changes, running dev branches against dev branches). We start to see a complete picture of the fully connected dev model. We can proactively pair changes from one system context with another system context, both overlayed over a base system context. This is when you have two devs working on two feature branches and both have active PRs. They can now effectively work together because they have this translation, this transparent overlay of their respective diffs to the upstream system context (data flow or program flow in this example). Can use aggregator as an example application two devs are working on.

Remember with the two dev example you're mapping each individual commit to each individual commit in two branches. The virtual upstream becomes the latest pair that scores the highest after going through strategic plans, gatekeeper, and prioritizer. This becomes your upstream as far as your local development is concerned.

Implementation note: subflow will be called one time for each new system context yielded by the prioritizer. Prioritizer is also used in orchestrator main loop for dynamic reprioritization or drop. When prioritizter is in main loop `run_operations_for_ctx()`. Contexts can be dynamically reprioritized and that will effect the operations running within the context, for example could lead to opimp cancelation or whole context cancelation. On dynamic reprioritization prioritizer will rerun strategic plans (same as with LTMs we have output operations reading from cached state) and gatekeeper then re-run prioritization and re-score with knowledge of what other contexts in the overall set are running. Therefore, the pritoritizer MUST be told which system contexts map to which context that will be created for the InputSet passed to the flow. Gatekeepers would be aware of the context and aware of the outputs of the stratgic plans and their values relative to other system contexts being executed in the overall network to determine optimal dynamic reprioritization of executions of system contexts within the overall system contexts this allows us to efficivly reward trains of thought on demand. This is also the key to #245!

We can have an output operation which grabs outputs from subflow which is the most favorable from re-running plans, gatekeeper, and pirorirtizer. We could also enable grabbing certain outputs from multiple subflows to pick the highest accuracy predictions for outputs. The output operations run for a context could block waiting for other contexts within the train of thought to complete, and then return outputs from derived contexts once all have finished execution or based on some trigger / threshold values (strategic plans, loss).

Risk assessment on potential system context execution done via strategic plans, gatekeeper, and prioritizer combo. If for example it would violate a security principle, do not execute it. As another example if it has hypnotized outputs that are beyond the acceptable estimates for cost to execute or something, the gatekeeper would drop it.

Prioritizers could instigate change in CSP to reduce cost and sacrifice performance by rerunning their strategic plans with new inputs for strategic principles. Since plans yield system context instances.

```mermaid
    graph TB

      classDef background fill:#ffffff00,stroke:#ffffff00;
      classDef Person color:#ffffff,fill:#08427b,stroke:#08427b;
      classDef NewSystem color:#ffffff,fill:#1168bd,stroke:#1168bd;
      classDef ExistingSystem color:#ffffff,fill:#999999,stroke:#999999;

      subgraph system_context[System Context for InnerSource]

        requirements_management[Requirements Managment<br>&#91Software System&#93]
        data_storage[Artifact Managment<br>&#91Software System&#93]
        asset_change[Code Change - new system state<br>&#91Input&#93]
        engineer[Software Engineer<br>&#91Person&#93]
        manager[Project Manager<br>&#91Person&#93]
        customer[Customer<br>&#91Person&#93]
        trigger_dependents[Continuous Integration - on all downstream<br>&#91Operation&#93]
        cd_software[Continuous Deployment<br>&#91Software System&#93]
        iaas[Infrastructure as a Service<br>&#91Software System&#93]

        customer -->|Understand customer requirements| requirements_management
        requirements_management --> manager
        manager -->|Communicate priority of tasks| engineer
        engineer --> asset_change
        asset_change --> trigger_dependents
        data_storage -->|Pull dependencies from| trigger_dependents
        iaas -->|Provide compute to| trigger_dependents
        trigger_dependents -->|Validation passed, promote and release, proceed to A/B test with other live environments. safe mode-thinking: playing out trains of thought with stubs, run through outputs of sub execution / model execution with strategic plans and run though gatekeeper to decide which ones meet the must have qualifications. Qualifications are which strategic plans were used, if they attempted to pull a veto, veto prioritization in provenance, all the input data and output data involved in executing the strategic plans, gatekeeper - formerly referred to as the decision maker, and prioritizer| cd_software
        cd_software -->|Store copy| data_storage
        cd_software -->|Make available to| customer

        class manager,engineer,customer Person;
        class innersource NewSystem;
        class trigger_dependents,cd_software,requirements_management,asset_change,data_storage,iaas ExistingSystem;

      end

      class system_context background;
```