## 2023-10-17 @pdxjohnny Engineering Logs

- https://github.com/usnistgov/OSCAL
- https://pages.nist.gov/OSCAL/about/stakeholders/tooldevelopers/
  - > OSCAL provides standardized formats for consuming control, catalog, profile, and implementation information to visualize and automate security compliance processes. OSCAL provides a standardized means for the automated assessment of infrastructure and software solutions to verify the ongoing effectiveness of the system's security control implementation.
    >
    > How Does OSCAL Help Me?
    >
    > - Use automated tools to create more complete and consistent security plans with machine assistance.
    > - Easily attest to the state of control implementations, reducing the paperwork burden associated with supporting federal agencies.
    > - Expose security control and assessment data in a standardized format which can be represented via JSON or XML.
    > - Improve the User Experience (UX) and Machine Experience (MX) by offering new compliance tools.
Minimizes the need for vendors to customize solutions for customers by adhering to a broad-based set of standardized formats.
- https://pages.nist.gov/OSCAL/about/use-cases/
  - > OSCAL supports a number of use cases, some of which are described below.
    >
    > - Managing Multiple Regulatory Frameworks
    >   - The work being performed by the OSCAL development team to document catalogs that then map to multiple regulatory frameworks will simplify the risk management burden to maintain multiple security plans or to maintain the mapping to multiple regulator frameworks within a single security plan.
    >   - As an example, a federal agency may need to meet the requirements of the Federal Information Security Modernization Act (FISMA) and follow the NIST Risk Management Framework guidance. If the agency also maintains health records and must comply with the Health Insurance Portability and Accountability Act (HIPAA) and meet the security and privacy requirements. Moreover, if the agency provides healthcare services where payments are collected, then those transactions must comply with the Payment Card Industry Data Security Standard (PCI DSS). The security controls and requirements associated with these three separate frameworks increase the complexity of implementing, assessing and operating such systems, which can result in increased costs for the agency to maintain the security documentation of systems operating within its portfolio.
    >   - The scenario for the sample federal agency highlights the need to simplify the complexity for agencies required to meet multiple regulatory frameworks, while conducting proper risk management practices. The OSCAL project is considering this scenario as we are developing the OSCAL models. The foundational elements of the OSCAL control, catalog, and profile models permit selection of security controls from multiple catalogs and the creation of a single profile that an agency may use to manage risks and maintain the system’s security posture as required by the three regulatory frameworks. OSCAL abstracts away the complexity of managing multiple frameworks, allowing cyber security professionals to focus on managing security and privacy risks while maintaining the security posture of their systems.
    >   - The project will continue to expand support for additional security catalogs over time to maximize the utility of the OSCAL.
    > - Machine-Readable System Security Plans (SSPs)
    >  - To meet the requirements of different regulatory frameworks and to perform good risk management, cyber security professionals often need to document a system’s implementation and to continuously assess the effectiveness of the implemented security and privacy controls in order to authorize its use during the entire system’s life cycle. This effort is resource intensive; especially in scenarios where multiple regulatory frameworks and control catalogs apply to the system and its control implementation. In addition, control implementation documentation is not standardized, varies widely between agencies, and is stored in a collection of Word documents, Excel files, and other formats that are difficult to manage as cyber security risks and control implementations change over time.
    >  - OSCAL is designed to provide a standardized format that reduces or eliminates this paper-based process, by transitioning documentation to a highly normalized, machine-readable format. This approach has multiple benefits:
    >    - Data between plans is consistent in both format and mapping to requirements and controls from multiple regulatory frameworks, when applicable,
    >    - Data is machine-readable and can be exposed to other security tools to provide additional automation, and
    >    - Data consistency and standardization support innovation in commercial and open-source tooling to provide further automation of assessment and accreditation processes.
    >  - By representing system information using the OSCAL [system security plan model](/concepts/layer/implementation/ssp/), this data can be analyzed using automated processes, streamlining the review and assessment process. The management systems that are used to manage the security and privacy controls implemented in the system can be integrated to provide up-to-date system information using this model. Human-oriented documentation can be easily generated from the OSCAL data. This results in a more usable information set over what is provided using Word and Excel files alone.
    >    - The OSCAL team continues to enhance the OSCAL formats and to test these formats against real data.  The OSCAL formats are being continuously improved and enhanced as they are tested and issues are identified.  The end result will be a robust set of [standardized formats](/concepts/layer/implementation/) that greatly simplify the way security plans are created, and managed; and how technical security controls are implemented and assessed for a system.
    > - Self-Describing Software and Containers
    >   - Another model provided by the OSCAL [implementation layer](/concepts/layer/implementation/) is the [component definition model](/concepts/layer/implementation/component-definition/). This model allows for the control implementation of a software application, virtual machine, or container to be documented and shared by consumers of that resource. This allows the documentation of the controls supported by the application, virtual machine, or container to be bundled and distributed along with the software. System architects and security and privacy managers can use this information as a starting point for documenting the control implementation of a system that uses these applications, virtual machines, or containers.
    > - Self-Describing Policies, Processes, and Procedures
    >   - Similar to the previous use case, the [component definition model](/concepts/layer/implementation/component-definition/) can also be used to describe the set of controls that are addressed by a given policy, process, or procedure. This allows authors of these artifacts to define how a given policy, process, or procedure implements security or privacy controls in a way that can be shared along with the artifact. This implementation information can be used System architects and security and privacy managers as a starting point for documenting the control implementation of a system that uses these policies, processes, or procedures.
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/35
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/96
- https://github.com/scitt-community/scitt-api-emulator/pull/37
  - Got receipt verification working on created receipt federation event
- https://github.com/ietf-wg-scitt/draft-ietf-scitt-architecture/issues/79
  - Proposed entry IDs as hash values of claims. This would help us ensure that claims do not get ping pong inserted multiple times when federation occurs.
- Mailing list post: [SCITT] Federation via ActivityPub
  - https://mailarchive.ietf.org/arch/msg/scitt/IAy_Av-2Q_IkY13A3JGbFPPkNo0/
  - https://mailarchive.ietf.org/arch/msg/scitt/oV0nyTvBqn7c78CIz1q9UhjJfYc/
- TODO
  - [ ] Submit claim to log being federated to