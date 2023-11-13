## 2023-10-16 @pdxjohnny Engineering Logs

- [OpenVEX WG 2023-10-16](https://docs.google.com/document/d/1C-L0JDx5O35TjXb6dcyL6ioc5xWUCkdR5kEbZ1uVQto/edit#heading=h.7vfzsvcxys2j)
  - Took notes
  - Talked about https://github.com/openvex/spec/issues/9
  - In two weeks we'll talk about what OpenVEX's plans are with regards to notification
  - Survey might tell us how people are doing for advertisement
  - Some folks plan on inserting statements into containers
  - People would like to have a webpage and post a line on a webpage
  - Brandon agrees with Puerco about using dedicated channels for each type of data
    - (After meeting note): That could of course be done, it's just that if you're going to add it to the transparency service's log anyway you might as well not duplicate the event
- [SCITT Architecture Milestone 4: IETF 118](https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/milestone/4)
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/79 [multiple-instances](https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues?q=is%3Aopen+is%3Aissue+label%3Amultiple-instances)
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/19 [Registration Policy](https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues?q=is%3Aopen+is%3Aissue+label%3A%22Registration+Policy%22)
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/87
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/11 [terminology](https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues?q=is%3Aopen+is%3Aissue+label%3Aterminology)
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/14 [RBAC-ABAC](https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues?q=is%3Aopen+is%3Aissue+label%3ARBAC-ABAC)
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/36
  - https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/98
- OpenSSF AI/ML
  - > [MVSR Artificial Intelligence/Machine Learning (AI/ML) WG ](https://github.com/ossf/ai-ml-security/blob/51c6157ace32f566793eae543c69f07e2e49fa67/mvsr.md)
    >
    > We are an incubating WG is going through the initial life cycle phases to address open source software security for AIML workloads. The developing scope involves analyzing open source AIML data sets, data models and OSS code mashups used in AIML to articulate the specific security concerns and controls for the subset of OSS AIML workloads.  This is important because the accelerated adoption of AIML has an OSS and security component that is not well understood, and OpenSSF can play an industry leading position.
    >
    > This committee interlocks with the [LF Data and AI](https://lfaidata.foundation/projects/) foundation monthly to avoid effort duplication.
    >
    > Roadmap goals: [high level efforts for upcoming 18 months]
    >
    > * Create high two level white papers, one an executive overview and the other directed at practitioners  and industry leadership positions (can work with Marketing committee for broad distribution)
    > * Explore a “security slam” for existing OpenSSF tooling to see how it protects/applies to OSS AIML workloads; develop OSS security patterns for use cases where OSS AIML components are integrated in the supply chain.
    > * Coordinate with other working groups to examine crossovers and gaps.
  - ⁠[AI Security Telemetry](https://docs.google.com/document/d/1J8M1F5ev9tXzMpA3dAFXqXYs2t-T10xt0_ObXnqNN04/edit)
    - > (12.) Understanding the AI Supply Chain
      > Owners:
      >
      > - Overview: The AI supply chain includes all the components necessary for building, training, and deploying AI models. This includes data collection and processing, model training, hardware, and software infrastructure.
      > - Importance: Understanding the AI supply chain is crucial for developers to ensure the efficient and ethical use of AI technologies.
      > - Case Study: The development of GPT-3 by OpenAI provides insights into the complexities of the AI supply chain.
      > - Additional Resources:
      >   - [[The AI Supply Chain](https://hbr.org/2021/02/the-ai-supply-chain-runs-on-ignorance)]
      >   - [[AI and Compute](https://openai.com/research/ai-and-compute/)]
      >   - [[Attacks on AI Models: Prompt Injection vs supply chain poisoning](https://blog.mithrilsecurity.io/attacks-on-ai-models-prompt-injection-vs-supply-chain-poisoning/)] a good overview of supply chain with pictures.
      >
      > To understand AI supply chain Security, it helps to understand Open Source Software Supply chain Security
      > ![image](https://github.com/intel/dffml/assets/5950433/61a5e1eb-d604-42cb-96b0-2a668b148627)
    - [The AI/ML Security Landscape](https://docs.google.com/document/d/1AyivzKsERoIZcyr4XrH6CrNeUoYHhpiswThHS0XrbSU/edit?pli=1#heading=h.g0d92hu77q5z)
      - Commented on Provenance & Legal Issues: Provenance section
        - https://docs.google.com/document/d/1J8M1F5ev9tXzMpA3dAFXqXYs2t-T10xt0_ObXnqNN04/edit: AI Security Telemetry: 12. Understanding the AI Supply Chain
Mentions Open Source Software Supply chain Security as a helpful tool for understanding the AI supply chain. Have been looking at [https://scitt.io](https://www.google.com/url?q=https://scitt.io&sa=D&source=docs&ust=1697493629598768&usg=AOvVaw0NGyL7vwdxpnSYWa3idYKx) to assist with transparency, access, and evaluation of provenance related to AI/ML data. [https://github.com/scitt-community/scitt-api-emulator/pull/37#ref-commit-75b9040](https://www.google.com/url?q=https://github.com/scitt-community/scitt-api-emulator/pull/37%23ref-commit-75b9040&sa=D&source=docs&ust=1697493629598833&usg=AOvVaw0No00NERmojttEbr5wShqN)
          From SCITT.io:

          > "The Supply Chain Integrity, Transparency and Trust (SCITT) initiative is a set of proposed IETF internet standards for managing the compliance of goods and services across end-to-end supply chains. SCITT supports the ongoing verification of goods and services where the authenticity of entities, evidence, policy, and artifacts can be assured and the actions of entities can be guaranteed to be authorized, non-repudiable, immutable, and auditable.
In practice, SCITT provides information about artifacts, enabling a mesh of dependencies to understand what each subsystem is consuming. Detailed information comes in varying formats, from structured to unstructured."
      - Commented on OpenSSF Projects (reuse where applicable) section
        - https://github.com/ossf/OpenVEX might be helpful for declaring issues with datasets
          - Hoping to see events of new vulns (being issues with training data in this case) getting integrated to trigger re-deployment/build/train/test cycles of AI/ML workloads.
          - [What Is Alice? Mermaid Diagram](https://github.com/intel/dffml/assets/5950433/1141b8b0-5384-4c28-bdca-895cf7af809b)
          - [Entity Analysis Trinity v0.0.2](https://user-images.githubusercontent.com/5950433/188203911-3586e1af-a1f6-434a-8a9a-a1795d7a7ca3.svg)
- https://tailscale.com/kb/1232/derp-servers/
  - https://github.com/tailscale/tailscale/issues/9787
  - https://github.com/slchris/derp-server/blob/main/Dockerfile
  - https://hub.docker.com/r/sparanoid/derp