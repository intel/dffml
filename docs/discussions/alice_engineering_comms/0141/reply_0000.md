## 2023-01-08 @pdxjohnny Engineering Logs

- https://huggingface.co/blog/rlhf
- https://github.com/alexander0042/pirateweather/blob/main/docs/API.md
  - DWN version of this
    - [2023-01-07 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4621717)
      - https://gist.github.com/csuwildcat/2ac6ebf4c581c5df143c32fa4911850e/revisions
  - SARIF as a forecast data blob
- https://issues.apache.org/jira/browse/GROOVY-8843
- https://github.com/CarperAI/Algorithm-Distillation-RLHF/pull/3/files#diff-3d1a95badf0f44566edebceb970d462b38ac59025e9cb5144461c0ca1f95b0c8R115
  - This looks similar to the #1369 talk about rolling dffml.Stage
  - https://honglu.fan/posts/fmlang-env/fmlang-env/
- https://docs.oasis-open.org/sarif/sarif/v2.0/csprd01/sarif-v2.0-csprd01.html
- First pass all SBOM and VEX/VDR for comms channels, SARIF as part of VDR message body contents, ideally with VC for SCITT receipt. Finish cve bin tool pr
- https://huggingface.co/blog/intro-graphml
- https://huggingface.co/blog/clipseg-zero-shot
  - This might help with our what software is the same via our software DNA to image encoding methods, ir just reuse the layers
- https://hachyderm.io/@kat_kime/109652239958849080
  - Many people talking about trust required
  - We are trying to enable a closed loop for trust for software developers to understand their own projects, what they can trust (should you really dump that dep? Or did dynamic sandboxing results cached elsewhere in your org say that it violates policy at runtime, aka backdoored coin miners and ransomware? You wouldn't know that type of thing by bumping the dep by hand, you'd almost for sure get pwned and now your dev box got pwned.
    - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#what-is-alice
- ``ensure_`` functions into (bellow) which can then be overlayed as desired
  via CLI or via install of ad-hoc blank package with only entry_points.txt to
  enable them as desired.
  - alice_test.shouldi.contribute.bom_v0_0_0
    - We communicate via VEX/VDR threads to post "replys" to SBOMs where
      SCITT receipt for VDR/VEX allows us to traverse to roots of trust.
    - Decentralized async supply chains are all you need. (lock acquired)
      - https://gist.github.com/csuwildcat/2ac6ebf4c581c5df143c32fa4911850e/revisions
      - This is why it's important that your AI convey the way you want it to convey
      - This is related to values stream mapping, which is related to VDR, which is related to the compute contract negotiation within conceptual bounds stuff. This is what forms the basis for the dynamic sandboxing, that local feedback loop on the Entity Analysis Trinity in Behavioral Analysis where we are "thinking" of more ideas to try while we're in execution mode. More data to add to the knowledge graph (same as we do with static analysis).
      - Via data transformations between formats we are able to build a holistic picture of our software development lifecycle. These graphs can then be analyzed in relation to each other to understand where development practices differ across projects. This helps us understand which developers know and can introduce best practices in other projects. With our AI agents that might be what hardware is really good at this compute contract (aka who has hardware accelerated memory tagging VM isolated FFMPEG?).
        - Trust then comes into play when we look at past data in the prioritizer.
          - If we see that FFMPEG has a large attack surface with a record of exploitation via VEX/VDR, we will choose to schedule on the VM memory tagging node for extra assurance that if the box gets popped during decode, we detect and discard the output. We can tie in threat model data to make that decision. This is not always happening at runtime. Most of the time it is happening via static analysis. We are just giving example situations which could using the Open Architecture be audited across environments due to the use of the intermediate representation allowing for interpretation of the knowledge graph. So what we're really saying is if we put items in the knowledge graph with the evolving list of properties in the Manifest ADR, and check alignment to that ADR via Alice DAC loop, then we can understand how complete our understanding of our knowledge graph is.
- Future
  - [ ] Base container for shouldi off of mega-linter container to wrap and or explore data flow integration there.
    - We want to have the graph and past data (which Alice does) because this is important to helping users understand their posture over time. We could run mega-linter via similar wrapping techniques as well, but we loose on granularity that way.