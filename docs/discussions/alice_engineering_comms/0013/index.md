- Policy
  - ABC’s of Conformity Assessment
    - https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.2000-01.pdf
    - This might be helpful later when we write docs for / think about how to apply policy (see vol 0 introduction arch diagram)
- SCITT
  - Zachary Newman shared looking at OpenSSF / SCITT terminology ran into same topics that we did when we brought up using shared underlying protocols and formats in the [2022-07-25 SCITT meeting](https://github.com/intel/dffml/discussions/1406#discussioncomment-3223361) when talking about RATs style attestation vs SLSA/in-toto/sigstore style.
    - https://mailarchive.ietf.org/arch/msg/scitt/utSOqlCifoorbqUGWNf-wMlBYR4/
      - Dick agrees with Zach's analysis. "I've also been monitoring the OpenSSF Scorecard initiative, which goes beyond sigstore attestation checking to assign a "trust score". Not sure if this has traction, but there is a lot of activity on github. https://github.com/ossf/scorecard/blob/main/README.md#basic-usage OpenSSF does NOT appear to be following/implementing NIST C-SCRM recommendations and standards for Executive Order 14028 and consumer software labeling and other attestation recommendations; https://www.nist.gov/document/software-supply-chain-security-guidance-under-executive-order-eo-14028-section-4e" [Dick Brooks]
  - Commit message to charter
    - > The Endor POC by `@OR13` was exemplary because there was a low amount of abstraction / extra information / steps introduced for the learner to understand the sequence of data transformations involved. It makes clear the contents of the serialization of choice (DIDs + VCs in Endor's case) and how that varies across the steps. The POC provided immediate value on the mailing list in a way that examples which introduce more abstraction layers are unable to do as quickly.
      >
      > We apply our recent learning from this success by adding to the charter the production of a similar example which in this patch we call "file-based", but we could change that to a more descriptive term if there is one. Having an example similar to the learning methodology presented via Endor would accelerate the pace at which developers up and down the software stack and in different programming languages would be able to adopt SCITT. This is due to the low level of abstraction introduced by it's file and shell based implementation. Files and shell commands translate easy into other languages where they can be slowly swapped out from initial fork/exec and equivalents to language code.
      >
      > The SCITT community could potentially provide documentation on how the fork/exec style implementation could be transformed into the HTTP server implementation. Due to the generic nature of SCITT and the many touchpoints various software systems will likely have with it in the future. It is important for us to consider as a part of our threat model the effect cohesive example documentation has on the correctness of downstream implementations. Providing cohesive examples where we start with the basics (file-based), moving to an example environment implementers are likely to be working in (HTTP-based), and finally explaining how we went from the basic to the complex would give a robust view of what SCITT should look like to implementers and provide them with a clear path to a hopefully correct implementation.
      > 
      > More cohesive documentation will reduce the number of security vulnerabilities we see in our communities code. Code which is fundamentally about security in nature. This modification to the charter seeks to act on recent learnings around example code experienced within the SCITT community itself and seeks to contribute to the development of our threat model as we think about SCITT's lifecycle and rollout.
  - For this reason I propose we
  - where they will be creating the future of SCITT's robust, actively maintained solutions.
    - https://mailarchive.ietf.org/arch/msg/scitt/Hz9BSiIN7JHAgsZL6MuDHK4p7P8/
    - https://github.com/OR13/endor
      - This is learning methodology goldmine.
  - https://github.com/ietf-scitt/charter/pull/21
  - https://mailarchive.ietf.org/arch/msg/scitt/B9cwkueu3gdQ7lBKkhILcFLD0E4/
- RATS
  - https://datatracker.ietf.org/doc/draft-ietf-rats-architecture/
- SBOM
  - We [DFFML community] intend to use the "living" SBOM VDR capabilities to facilitate the breathing of life into our living threat models. This will allow us to facilitate vulns on architecture.
    - https://spdx.github.io/spdx-spec/v2.3/
    - https://energycentral.com/c/pip/what-nist-sbom-vulnerability-disclosure-report-vdr
    - > The recommendation by NIST to provide software consumers with a NIST VDR is gaining traction as a best practice. The latest version of the SPDX SBOM standard, version 2.3, includes provisions (K.1.9) enabling a software vendor to associate a specific SBOM document for a software product with its online NIST VDR attestation for that product, which is linked within the SBOM. The link refers to a “living” SBOM VDR document that is updated by a software vendor, whenever new vulnerabilities are reported. Having this “always updated NIST VDR” available enables software consumers to answer the question “What is the vulnerability status of my software product from Vendor V, as of NOW?”, providing consumers with on-going, up-to-date visibility into the risks that may be present in an installed software product, as new vulnerabilities (CVE's) are being reported/released.
      >
      > As stated previously, NIST did not prescribe a format for a NIST VDR attestation, but guidance is provided on what a VDR includes. Reliable Energy Analytics (REA) has produced an open-source “interpretation” of what a NIST VDR contains in order to meet EO 14028, which is available here in an XML Schema format with samples provided in XML and JSON (https://raw.githubusercontent.com/rjb4standards/REA-Products/master/SBOMVDR_JSON/VDR_118.json) formats.