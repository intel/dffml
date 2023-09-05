## 2022-08-29 @pdxjohnny Engineering Logs

- Notes to self
  - Watched the progress report videos to make sure I know where we're at, thanks past Johns and others
    - Realized we should use `CITATION.cff` instead of `myconfig.json` in the examples under today's TODOs
    - They seem to form a cohesive if a bit rambling picture.
    - Reminded me why I quit caffeine. Sleep is important.
    - We could probably do for a 1 minute explainer video on what is Alice
      - Below "Status" would probably be a good way to start the day tomorrow as the 1 minute video with a breif bit about what is Alice at the begining.
        - Alice is our developer helper. We extend her to help us understand and preform various parts of the software development lifecycle. We extend her by writing simple Python functions which are easy for anyone to distribute or combine. She is based on a programming language agnostic format known as the Open Architecture. Eventually we will be able to extend any part of her in any language, or driven by machine learning models.
- SCITT
  - Watched https://www.youtube.com/watch?v=6B8Bv0naAIA&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&t=1320s
    - SCITT Architecture
      - ![image](https://user-images.githubusercontent.com/5950433/187310016-472934fb-e5cc-47e8-875d-a5ea93592074.png)
    - Dick's comment here on verification is related to a statement I'd made earlier today
      - https://www.youtube.com/watch?v=6B8Bv0naAIA&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&t=1584s
    - https://github.com/ietf-scitt/charter/pull/18/files#r957557301
    - Roy
      - In the case of the notary we have the opportunity to allow for claims that last longer than they are supposed to. The notary concept will allow his buddies to control certs (effectively) on their servers sides.
      - Answer to: How's this related to sigstore?
        - In SCITT sigstore would send contents to SCITT instance and then notary would put it on a ledger
        - In the case of SLSA they also submit to the SCITT store, it looks like at the moment they just plug into one another
    - Concerns that we are too software centric with current prospective charter.
      - Point taken but they can't scope increase more.
      - We want to align efforts across SCITT and OpenSSF to ensure we all work in the same directions
      - We can expand to non software use cases later if we flush this out as is first and make sure to design it with extensibility in mind.
  - Reviewed https://github.com/ietf-scitt/charter/pull/18/files#diff-7dc19c29f46d126113e2e7fb7b70710fd0fd3100c95564297664f8ceae8c653eR8
    - "For example, a public computer interface system could report its software composition, which can be compared against known software compositions for such a device, as recorded in a public append-only transparent registry." (https://github.com/ietf-scitt/charter/tree/60e628f1d718b69dc0d02f7a8168a5485f818201)
      - This sounds very similar to something we've talked about before which may be in a stream recording of how we identify the devices which aren't known to be running the "machines serve humans" rule, etc.
        - This is important for either SCITT or OA to address
   - https://github.com/ietf-scitt/charter/pull/18#pullrequestreview-1089013246
- Status
  - We want to make sure the contribution process works and is clear. Then we will move on to the data collection portion. Remember we are working over time. We are building the entity at the center of the Trinity, Alice. Please contribute falls under our Static Analysis portion. The Open Architecture, SCITT, SBOM all are used in our top portion, Intent. We are building the entity using the architecture which we will use the represent the findings of our static and dynamic analysis.
  - Alice can make contributions, we've laid the foundations for the automation of the software development process. Our next step is to help her understand what she's looking at, what is the code, how can she use the source Luke? Later we'll get into more details on the dynamic analysis portion of the Trinity, where we'll work, over time, across many program executions of the code we are working on, to understand how it's execution maps to the work that we're doing via our understanding of what we've done (`please contribute`) and what we we're doing it on (`alice shouldi contribute`).
  - As such our top priorities right now are
    - Ensuring the contribution process to what exists (`alice please contribute`) is rock solid.
    - Building out and making `alice shouldi contribute` accessible and ready for contribution.
    - Engaging with those that are collecting metrics (https://metrics.openssf.org) and ensuring our work on metric collection bears fruit.
  - Following our engagement on the metric collection front we will preform analysis to determine how to best target further `alice please contribute` efforts and align the two with a documented process on how we select high value targets so that others can pick up and run with extending.
  - Participating organizations in parallel begin automated outreach via Alice please contribute
- Game plan.
  - [x] `alice please contribute`
  - [x] Contribution ready
  - [ ] Demo on stream of how write install and publish a third party overlay
    - Have the overlay be a function which outputs a return type of `ContributingContents` and takes the name of the project given in a `CITATIONS.cff` file of the CONTRIBUTING example.
    - https://www.youtube.com/watch?v=TMlC_iAK3Rg&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=5&t=2303
    - https://github.com/intel/dffml/blob/9aeb7f19e541e66fc945c931801215560a8206d7/entities/alice/alice/please/contribute/recommended_community_standards/contributing.py#L48-L54
  - [ ] Demo on stream how to write install and contribute a 1st/2nd party overlay, the same code just not third party, from start to finish.
  - [ ] `alice shouldi contribute`
    - [ ] Support caching / import / export dataflows
    - [ ] Support query in easy way (graphql)
    - [ ] Support joining with previous runs / more sets of data
  - [ ] Contribute the data OpenSSF cares about to their DB via applicable joins and queries
     - [ ] Email Christine and CRob
- TODO
  - [ ] Organization
    - [ ] Daily addition by Alice to engineering log following template
      - [ ] Addition of old TODOs yesterday's logs
  - [ ] Export end state of input network / dump everything used by orchestrator
    - [ ] pickle
    - [ ] JSON
  - [ ] Ensure import works (check for state reset in `__aenter__()`, we probably need a generic wrapper to save the memory ones which populates after the `__aenter__()` of the wrapped object.
  - [ ] GraphQl query of cached state using strawberry library or something like that
  - [ ] Example docs for how to run a flow, then merge with static data as the start state for the cache and then query the whole bit with graphql

---

Title: Software Supply Chain Security Guidance Under Executive Order (EO) 14028
Section 4e
February 4, 2022 
Source: https://www.nist.gov/system/files/documents/2022/02/04/software-supply-chain-security-guidance-under-EO-14028-section-4e.pdf

Terminology
Section 4e uses several terms, including “conformity,” “attestation,” and “artifacts.” Because EO 14028
does not define these terms, this guidance presents the following definitions from existing standards
and guidance:
• Conformity assessment is a “demonstration that specified requirements are fulfilled.” [ISO/IEC
17000] In the context of Section 4e, the requirements are secure software development
practices, so conformity assessment is a demonstration that the software producer has followed
secure software development practices for their software.
• Attestation is the “issue of a statement, based on a decision, that fulfillment of specified
requirements has been demonstrated.” [ISO/IEC 17000]
3
o If the software producer itself attests that it conforms to secure software development
practices, this is known by several terms, including first-party attestation, selfattestation, declaration, and supplier’s declaration of conformity (SDoC).
o If the software purchaser attests to the software producer’s conformity with secure
software development practices, this is known as second-party attestation.
o If an independent third-party attests to the software producer’s conformity with secure
software development practices, this is known as third-party attestation or
certification.
• An artifact is “a piece of evidence.” [adapted from NISTIR 7692] Evidence is “grounds for belief
or disbelief; data on which to base proof or to establish truth or falsehood.” [NIST SP 800-160
Vol. 1] Artifacts provide records of secure software development practices.
o Low-level artifacts will be generated during software development, such as threat
models, log entries, source code files, source code vulnerability scan reports, testing
results, telemetry, or risk-based mitigation decisions for a particular piece of software.
These artifacts may be generated manually or by automated means, and they are
maintained by the software producer.
o High-level artifacts may be generated by summarizing secure software development
practices derived from the low-level artifacts. An example of a high-level artifact is a
publicly accessible document describing the methodology, procedures, and processes a
software producer uses for its secure practices for software development.
The following subsections of EO 14028 Section 4e use these terms:
(ii) generating and, when requested by a purchaser, providing artifacts that demonstrate
conformance to the processes set forth in subsection (e)(i) of this section;
(v) providing, when requested by a purchaser, artifacts of the execution of the tools and
processes described in subsection (e)(iii) and (iv) of this section, and making publicly available
summary information on completion of these actions, to include a summary description of the
risks assessed and mitigated;
(ix) attesting to conformity with secure software development practices;
In other words, when a federal agency (purchaser) acquires software or a product containing software,
the agency should receive attestation from the software producer that the software’s development
complies with government-specified secure software development practices. The federal agency might
also request artifacts from the software producer that support its attestation of conformity with the
secure software development practices described in Section 4e subsections (i), (iii), and (iv), which are
listed here:
(i) secure software development environments, including such actions as:
(A) using administratively separate build environments;
(B) auditing trust relationships;
4
(C) establishing multi-factor, risk-based authentication and conditional access across the
enterprise;
(D) documenting and minimizing dependencies on enterprise products that are part of
the environments used to develop, build, and edit software;
(E) employing encryption for data; and
(F) monitoring operations and alerts and responding to attempted and actual cyber
incidents;
(iii) employing automated tools, or comparable processes, to maintain trusted source code
supply chains, thereby ensuring the integrity of the code;
(iv) employing automated tools, or comparable processes, that check for known and potential
vulnerabilities and remediate them, which shall operate regularly, or at a minimum prior to
product, version, or update release;