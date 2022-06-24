# Alice's Adventures in Wonderland

> Blog series

Together we'll build Alice, an Artificial General Intelligence. We'll be successful when Alice successfully maintains a DFFML plugin as the only maintainer for a year. Debugging issues, writing fixes, reviewing code, accepting pull requests, refactoring the code base post PR merge, dealing with vulnerabilities, cutting releases, maintaining release branches, and completing development work in alignment with the plugin's universal blueprint. She will modify, submit pull requests to, and track upstreaming of patches to her dependencies to achieve the cleanest architecture possible. We'll interact with her as we would any other remote developer.

We'll need to build the foundations of Alice's thought processes. Throughout this series, we'll rely heavily on a mental model based on how humans think and problem solve. By the end of this series we'll have ensured Alice has all the primitive operations she requires to carry out the scientific process.

### Terminology

- Universal Blueprint
  - Standard architecture we use to describe anything. Provides the ability to use / reference domain specific architectures as needed to define architecture of whole.
- Think
  - Come up with new data flows and system context input
- Thoughts
  - Data Flows and system context input pairs (these two plus orchestration config we get the whole system context)

### Expectations

Alice is going to be held to very high standards. We should expect this list to grow for a long time (years). This list of expectations may at times contain fragments which need to be worked out more and are only fragment so the ideas don't get forgotten. 

- Alice will maintain a system which allows her to respond to asynchronous messages
  - Likely a datastore with the ability to listen for changes
  - Changes would be additions of messages from different sources (email, chat, etc.)
- Alice should be able to accept a meeting, join it, and talk to you
  - You should be able to have a conversation about a universal blueprint and she should be able to go act on it.

### Alice's Understanding of Software Engineering

We'll teach Alice what she needs to know about software engineering though our InnerSource series. She'll follow the best practices outlined there. She'll understand a codebase's health in part using InnerSource metric collectors.

### Why name it Alice?

You can name it or call it whatever you like. This blog series will call it Alice. Alice will be used to refer to the entity carrying out this job of maintainer. The name Alice will also be used to refer to the AGI in general, the architecture through which one can instantiate arbitrary entities. In effect, the whole bit is arbitrary, and you can call it whatever you like.

The original usage of DFFML was nicknamed George. George analyzed open source dependencies. This was his "job". 

Alice navigates the chaos of Wonderland.