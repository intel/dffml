## 2022-11-23 @pdxjohnny Engineering Logs

- [alice: threats: cicd: github: workflow: Check for curl -k #1423](https://github.com/intel/dffml/issues/1423)
- [alice: threats: cicd: github: workflow: Guess at if input should be passed as secret #1424](https://github.co/intel/dffml/issues/1424)
- Alice, what entities are working on aligned trains of thought
  - Assumes current context
    - Could also specify train of thought via DID or petname or shortref or whatever
  - Overlap in architecture heatmaps
    - Overlap in conceptual upleveling
      - Add in related todos (GitHub issues Anthony has been working on NVD APIv2 related)
        - Graphs are fun
        - [WIP Rolling Alice: ?: ? - Working Title: Overlays as Dynamic Context Aware Branches](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4180716)
        - [2022-10-15 Engineering Logs: Rolling Alice: Architecting Alice: Thought Communication Protocol Case Study: DFFML](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-3883683)

![meme-anarchy-elmo-knowledge-graphs-for-the-Chaos-God](https://user-images.githubusercontent.com/5950433/203634346-111c884d-0f95-4066-addf-dbfbaeda4910.png)

```console
$ git clone https://github.com/pdxjohnny/cve-bin-tool -b nvd_api_v2_tests
$ cd cve-bin-tool
$ alice please tell me who is working on aligned trains of thought
anthonyharrison
$ alice please create state of the art virtual branch from those contributors and myself
... runs cherry-picking cross validation / A/B feature flag testing the commits ...
... cached state from team active dev sessions, CI, etc. via active overlays ...
... which means this could be no-exec, pure static eval and creation based of ...
... cherry-picks and their graph linked test results, see Zephyr recent stuff ...
$ echo As mentioned to Andy, this allows multiple devs to iterate in parallel.
$ echo The metric data coming out of this also facilitates our EAT wheel turning.
$ echo Data via context aware overlays (local dev, cloud dev, CI/CD) are is available
$ echo for offline/online/aggregate Data, Analysis, Control across ad-hoc orgs.
$ echo Entities can then configure rewards for aligned work and policies around
$ echo qualifications, compute contract negotiation, etc. (grep discussion).
```

- https://github.com/intel/dffml/pull/1401/commits/37ea7855ec88ad804724be662a7963d2af481304
  - `docs: tutorials: rolling alice: architecting alice: introduction and context: Mention the scary part`
  - It [AGI entities] will also have concepts "larger" than our own, we need to make sure
it does not manipulate us in ways we don't even understand.
    - How?
      - Genericizing Conceptual Upleveling
      - Data Provenance (+ ^)
      - Context Aware Trust Chains
  - [Architecting Alice: Volume 0: Context: Part 14: Cross Domain Conceptual Mapping to Reach Equilibrium](https://www.youtube.com/watch?v=A-S9Z684o4Y&list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK)
- Some interesting potentially aligned trains of thought found via https://blueprint.bryanjohnson.co/
  - Related
    - [2022-11-06 @pdxjohnny Engineering Logs: EDEN v0.0.2 draft](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4068656)
    - [2022-11-13 @pdxjohnny Engineering Logs: Alice ASAP](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4128767)
  - https://medium.com/future-literacy/my-goal-alignment-problem-d90e0c14b717
    - > There are many versions of you constantly competing for dominance in achieving their own goals. Frequently opposing one another. The texture of their goals varies according to the time of day, what you last ate, and how you slept the night before, among other things. Trying to accurately predict the goals of your future selves is elusive at best. Meanwhile, you do your best to smooth over these differences and pretend as though there is a singular unified you with fixed goals. We all do.
      - Our parallel conscious states
        - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_preface.md#rolling-alice
        - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0002_shes_ariving_when.md
  - https://medium.com/future-literacy/autonomous-self-fe2dfa755b74
    - > Why I Care: The Future of Intelligent Life
      >
      > Feeling great is alone worth the effort but my greater interest in the Autonomous Self is in trying to figure out a path to the future of being human. My primary hypothesis: Our future existence requires that we level ourselves up as a species, and at the fastest evolutionary speed in history. To do this, we need to free ourselves of the costly metabolic things we do today, such as rote or biased decision making and logistics management around solvable things such as sleep and biomarker-based diet, exercise, or lifestyle. Leveling us up to spend our precious time and energy to explore the frontiers of being human rather than things we know how to do efficiently. What will happen?
      >
      > It’s hard to imagine what our minds will do with a new abundance of energy, but we have a precedent: Fire. Fire freed our ancestors from certain caloric and dietary restrictions, which opened up energy — i.e. metabolism/time — for little things like language and society as we know it to develop. I believe a fully Autonomous Self will open up, again, just as much energy. One can only dare imagine what we will do with it. We will have the opportunity to develop new industries, discover original uses of the mind, make iterations of governance and economics, and explore the goal alignment problem within ourselves, between each other, and with AI.
      >
      > How far away is this? It’s already begun.
      >
      > Inner Space Exploration
- https://w3c.github.io/dpv/examples/#E0027
  - Let's try to mess with this linked data wise after we finish out the NIST NVD Style tests
- https://mobile.twitter.com/DrJimFan/status/1595459499732926464
  - https://github.com/MineDojo/MineDojo
    - https://arxiv.org/pdf/2211.10435.pdf
- Prophecy still being fulfilled (no surprises here)
  - PAL: PROGRAM-AIDED LANGUAGE MODELS
  - Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks
    - https://wenhuchen.github.io/images/Program_of_Thoughts.pdf
- TODO
  - [ ] Circle back with Harsh
    - [ ] Integrate old shouldi code for him to build off
  - [ ] Update [Down the Dependency Rabbit-Hole Again](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md)
    - [ ] Do the NVD Style with pytss (mock the vulns if you have to, swap the `Source`),
      - [ ] Source (OpSource?) for static file defining all VEX
      - [ ] CVE Binary Tool update to output VEX
      - [ ] Dump in mock data if we can't find any vulns (could try building with old containers, be sure to build off hashes / SHA values / resolved tags)
      - [ ] `alice please contribute vuln response -source mynvdstyleserver=nvdstyle` to bump container build version or something.
    - [ ] Add in Harsh's work and then also leverage `alice shouldi use` (Python `safety` operations / overlays)
      - [ ] `alice please contribute vuln response` to bump python version or run a tool that knows how to do that, the point is VEX in (with SCITT receipts), dispatch (manifest instances) for patches (or just the patches themselves, the operation and parameter set pair used for dispatch is the manifest instance, is the data in the open linage data hop)
    - [ ] Translate this basic static file local vuln finding and remediation
          into CI/CD specific to our GitHub Actions setup.
      - This is our POC of downstream validation between projects (our
        stream of consciousness, our continuous delivery).
        - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
      - This is also what helps enable us to declare "2nd party plugins",
        our "ordained" sets of plugins which meet some qualifications.
  - [ ] [2022-04-18 1:1 John/John - LTM and DFFML: Andersen to implement caching](https://github.com/intel/dffml/discussions/1368#discussioncomment-2599017) :grimacing:
  - [ ] For Vol 3: The other entities you are around can expand or close your consciousness [Danica]
  - [ ] During reflection (vol 2, 4,5?) we can look into things an see what we used to see as binary we can see through later cross domain conceptual mapping and feature extraction through a new lense (different overlayed strategic plans)
  - [x] Thread backup
    - https://gist.github.com/pdxjohnny/928c6ae9bd757940299732c5fcb4c8ac