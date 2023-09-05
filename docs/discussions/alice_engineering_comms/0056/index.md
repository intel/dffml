# 2022-10-15 Engineering Logs

- http://blockexplorer.graft.network/
- Async Comms
  - Examples
    - At 07:34 -7 UTC @pdxjohnny started drafting the tutorial: `Rolling Alice: Coach Alice: You are what you EAT!`
      - Others with the GitHub discussions thread loaded in their browser (at least on desktop) will see updates soon after he edits comments and replies in the thread.
      - Possible aligned tutorial sketch follows: `Rolling Alice: Architecting Alice: Thought Communication Protocol Case Study: DFFML`
      - We will combine GitHub Actions on discussion edit trigger with [`scripts/dump_discussion.py`](https://github.com/intel/dffml/blob/ed4d806cf2988793745905578a0adc1b02e7eeb6/scripts/dump_discussion.py)
      - We will replicate this data to DIDs and run DWN `serviceEndpoint` s as needed.
        - system context as service endpoint or executed locally if sandboxing / orchestrator policy permits.
          - See early architecting Alice Engineering Log lossy cached streams of consciousness for more detail
            - https://www.youtube.com/playlist?list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK
       - We will attest data using reusable workflows, OIDC, and sigstore
       - We will run more rekor / fulcio instances
       - We will network via webrtc and DERP
       - We will write orchestration operations / data flows / overlays and use data flow as class to leverage them via double context entry pattern (or some other way to do that).
       - We will see the same effect, but in a more DID based way with abstract implementation / infra
         - This will be mentioned as being a follow on to the tutorial: `Rolling Alice: Architecting Alice: Stream of Consciousness`
           - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
         - Alice will filter by updates relevant to the downstream receiver of events based on their current state, context, etc.
           - https://twitter.com/SergioRocks/status/1580545209678454784
             - > !["Because Jade had more uninterrupted Deep Work time than Brayan. Those 4 interruptions that Brayan suffered amounted for an actual loss of 3 hours of productive work on the tasks assigned to him." Sergio Pereira](https://pbs.twimg.com/media/Fe85fdaXgAEhe4_?format=png)
         - She will notify or etc. as appropriate based off prioritizer's thoughts on 
           -  **TODO** implement the prioritizer concept as another tutorial
         - Similar to "Bob Online" or "Alice Online" message from webhook based tutorial but ran through data flow / overlayed logic to determine relevance and what to do / say. Also it's now including Decentralized Web Nodes and DIDs. Possible next step / future in this (aligned clusters) train of thought would be:
           - KERI encapsulation over arbitrary channels
           - NLP to summarize git log changes
             - Hook up to git log
           - CI integration to serialize to sensible information format
         - Eventually Alice will be able to tell us whatever we want to know.
           - In the future (current date 2022-10-15), when you want to know something
             about Alice, she'll be able to tell you, because she knows about her
             own codebase, and she has solid foundations for security and trust and
             alignment with your strategic principles / values. She's a trustworthy
             messenger, the Ghost in the shell.
           - See discussion thread (or the thread dump in `docs/arch/alice/discussion`)
             - https://github.com/intel/dffml/tree/alice/docs/arch/alice/discussion
               - `$ git log -p --reverse -p -- docs/arch/alice/discussion`
             - https://github.com/intel/dffml/discussions/1369