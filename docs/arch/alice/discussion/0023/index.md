# Alice's Adventures in Wonderland - Introduction and Context

> Introduction and Context to Tutorial series - May 2022

## Engineering Logs

- [Architecting Alice: Volume 0: Context](https://youtube.com/playlist?list=PLtzAOVTpO2jaHsS4o-sDzDyHEug-1KRbK)

### Table Of Contents

- [Introduction](https://github.com/intel/dffml/discussions/1369#discussioncomment-2603280)
- [Chapter I: Down the Rabbit-Hole](https://github.com/intel/dffml/discussions/1369#discussioncomment-2663771)

Together we'll build Alice. We'll be successful when Alice successfully maintains a codebase as the only maintainer for a year. Debugging issues, writing fixes, reviewing code, accepting pull requests, refactoring the code base post PR merge, dealing with vulnerabilities, cutting releases, maintaining release branches, and completing development work in alignment with the plugin's universal blueprint. She will modify, submit pull requests to, and track upstreaming of patches to her dependencies to achieve the cleanest architecture possible. We'll interact with her as we would any other remote developer.

We'll need to build the foundations of Alice's thought processes. Throughout this series, we'll rely heavily on a mental model based on how humans think and problem solve. By the end of this series we'll have ensured Alice has all the primitive operations she requires to carry out the scientific process.

We'll follow along an adapted version of Lewis Carroll's classic, Alice's Adventures in Wonderland. We take one chapter at a time, 12 chapters, 12 months, to build Alice. Next year at this time she'll begin maintenance of a repo. We'll spend the next year visualizing her thought processes and understanding how we can interact with her to extend her capabilities while she's on the job. Each quarter throughout the year we'll survey the user community of the repo she's been maintaining to get their feedback on her performance. Finally, we'll decide based on the feedback, what Alice's next adventures will be. More time in software Wonderland? Or off to learn about something new.

### What is Alice?

Alice is an architecture for code that will write and maintain itself based off of a standard description of architecture, a universal blueprint. As such Alice is both an AI software architect and the AI software's architecture itself. The universal blueprint is universal because it's intuitive enough that anyone can begin using it quickly after the correct way of communicating to that individual is established via some communication method (spoken language, visual of some kind, text, etc.). This universal blueprint is an abstraction layer between descriptions of architecture within different domain specific representations for subcomponents as required to fully describe the system.

This universal blueprint (system context) is an integral part of creating a shared language for meaning and intent between humans and an Artificial General Intelligence. The goal is to provide an architecture and implementation for independent entities which act in accordance with guiding strategic plans/blueprints. This architecture must be safe and secure by default, scalable, and easily extensible.

- InnerSource is where we learn what Alice should consider to be quality code

- CI/CD is where we learn how Alice can run and deploy code

- Supply Chain Security is how we learn how Alice can create a compute network suitable for various edge deployment scenarios. Edge deployment scenarios being the usage of all assets she has at her disposal. This is where she'll be comprehending security.

The end goal is to create a software architect, Alice. She will consult on existing projects to provide analysis of their architectures and properties such as maintainability, provide guidance for developer workstream prioritization to achieve strategic business goals, and write and maintain codebases herself, accepting contributions from external contributors.

### Terminology

- Universal Blueprint
  - Standard architecture we use to describe anything. Provides the ability to use / reference domain specific architectures as needed to define architecture of whole.
- Think
  - Come up with new data flows and system context input
- Thoughts
  - Data Flows and system context input pairs (these two plus orchestration config we get the whole system context)

### Expectations

Alice is going to be held to very high standards. We should expect this list to grow for a long time (years). This list of expectations may at times contain fragments which need to be worked out more and are only fragment so the ideas don't get forgotten. 

- Alice should be able to work on any project as a remote developer
  - She should be able to make changes to projects following the branch by abstraction methodology
  - When she works on a github issue she'll comment what commands she tries and what files she modifies with diffs
- Alice will maintain a system which allows her to respond to asynchronous messages
  - Likely a datastore with the ability to listen for changes
  - Changes would be additions of messages from different sources (email, chat, etc.)
- Alice should be able to accept a meeting, join it, and talk to you
  - If Alice notices conversation getting off topic, she could interject to ask how it relates, and then update references in docs to that effect.
  - You should be able to have a conversation about a universal blueprint and she should be able to go act on it.
  - She should be able to analyze any codebase you have access to live and build and walk you through architecture diagrams
  - Alice build me a linux distro with these versions of these applications deploy it in a VM in QEMU, show me the screen while it's booting. Then give me control of it via this meeting. ... Okay now snapshot and deploy to XYZ CSP.
    - She should figure out how to validate that she has a working linux distro by overlaying discovered tests with intergration tests such as boot check via qemu serial.
  - Alice, spin up ABC helm charts and visualize the cluster (viewing in an AR headset)
  - Alice, let's talk about the automating classification web app included in the example.
    - Alice, give us an overview of the threats on our database, deploy the prod backup to a new environment. Attempt to exploit known threats and come up with new ones for the next 2 weeks. Submit a report and presentation with your findings. Begin work on issues found as you find them.
  - What are our biggest tome syncs between issue creation to delivery of fix to associated users?
- We should be able to see Alice think and understand her trains of thought
  - If Alice is presenting and she estimates thinking of the correct solution will take longer than a reasonable time her next word is expected by to keep regular conversational cadence, she should either offer to brainstorm, work through it and wait until it makes sense to respond, maybe there are situations where the output is related to saving someone's life, then maybe she interupts as soon as she's done thinking. Provided she didn't detect that the train of thought which was being spoken about by others was not of higher prioritiy than her own (with regards to lifesaving metrics).

### Alice's Understanding of Software Engineering

We'll teach Alice what she needs to know about software engineering though our InnerSource series. She'll follow the best practices outlined there. She'll understand a codebase's health in part using InnerSource metric collectors.

Alice will see problems and look for solutions. Problems are gaps between the present system capabilities and desired system capabilities or interpretations of outputs of strategic plans which are unfavorable by the strategic decision maker or the prioritizer.

### Naming

You can name it or call it whatever you like. This blog series will call it Alice. Alice will be used to refer to the entity carrying out this job of maintainer. The name Alice will also be used to refer to the AGI in general, the architecture through which one can instantiate arbitrary entities. In effect, the whole bit is arbitrary, and you can call it whatever you like.

Being that Alice is the nickname for both our an entity and the architecture in general. Alice when used in reference to the architecture is a stand in for the the technical term for the architecture. Not sure what the right technical term is right now. Maybe something like: data centric fail safe architecture for artificial general intelligence.

The original usage of DFFML was nicknamed George. George analyzed open source dependencies. This was his "job". 

Alice's Adventures in Wonderland is in the public domain, which is a great reason to leverage it for reuse. It's all over the place, just massive chaos, nothing makes sense. Alice navigates the chaos.

Also, in cryptography Alice and Bob are already commonly used names. So there's some shared understanding in the community that Alice is the name of a theoretical entity.

Also when George got a name people started liking him a lot more, talking positively about him, making quips about him. It's just more fun to give the inanimate object a name. Or a personality, oh George doesn't like that repo! I'm sure Alice would agree that things are a lot more interesting when inanimate objects have names and personalities.