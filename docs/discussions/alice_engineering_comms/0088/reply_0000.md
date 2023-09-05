## 2022-11-16 @pdxjohnny Engineering Logs

- NVD API style as first way to distribute VEX.
  - ActivityPub publish as well
   - Websub for new notifications? Look up how Mastodon does.
- Working on cve-bin-tool https://github.com/intel/cve-bin-tool/issues/2334#issuecomment-1315643093
  - We're reverse engineering the NIST NVD API to serve VEX.
    - The following logs/recordings can be useful in learning how to reverse
      engineer an HTTP based protocol to implement a similar server.
    - This becomes the base layer for communication in our decentralized CI/CD
      aka DFFML plugin land, aka poly repo land, aka the real world, aka Wonderland.
      - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#what-is-alice
      - [service: sw: src: change: notify: Service to facilitate poly repo pull model dev tooling #1315](https://github.com/intel/dffml/issues/1315#issuecomment-1066814280)
      - Vuln management is a MUST implement channel we can use for patch submission
        and comms for alignment between entities.
  - We're hitting this open issue while were at it.
- Got basic stats response saved from cache working
  - Cache: https://gist.github.com/pdxjohnny/599b453dffc799f1c4dd8d8024b0f60e
  - Got serving feed working with same page requested over fails test (as it should, paging broken currently, next is fix that).
    - [gist: Python example pagination client and server](https://gist.github.com/pdxjohnny/47a6ddcd122a8f693ef346153708525a)
- Side note: This asciinema was 12 MB uncut so I had to trim it up a bit

[![asciicast](https://asciinema.org/a/538130.svg)](https://asciinema.org/a/538130)

- httptest NIST API single CVE import working

[![asciicast](https://asciinema.org/a/538136.svg)](https://asciinema.org/a/538136)

[![asciicast](https://asciinema.org/a/538143.svg)](https://asciinema.org/a/538143)

- Pagnation asciicast (too big, 12 MB decompressed)
  - [nvd-pagenation.json.txt](https://github.com/intel/dffml/files/10023980/nvd-pagenation.json.txt)

```console
$ unxz -d < $(ls ~/asciinema/fedora-rec-* | tail -n 1) | dd if=/dev/stdin of=/dev/null status=progress
24117+1 records in
24117+1 records out
12348069 bytes (12 MB, 12 MiB) copied, 0.0500872 s, 247 MB/s
```

- Basic server seems to be working for v1 API
- Added CLI command `alice threats vulns serve nvdstyle`
  - https://github.com/intel/dffml/commit/cb2c09ead795ba0046cb5911bcd6e939419058d8

https://github.com/intel/dffml/blob/4101595a800e74f57cec5537ea2c65680135b71a/entities/alice/alice/threats/vulns/serve/nvdstyle.py#L1-L241

- https://www.darkreading.com/dr-tech/cybersecurity-nutrition-labels-still-a-work-in-progress
  - https://www.whitehouse.gov/briefing-room/statements-releases/2022/10/20/statement-by-nsc-spokesperson-adrienne-watson-on-the-biden-harris-administrations-effort-to-secure-household-internet-enabled-devices/
    - > Yesterday, the White House convened leaders from the private sector, academic institutions, and the U.S. Government to advance a national cybersecurity labeling program for Internet-of-Things (IoT) devices. The Biden-Harris Administration has made it a priority to strengthen our nation’s cybersecurity, and a key part of that effort is ensuring the devices that have become a commonplace in the average American household – like baby monitors or smart home appliances – are protected from cyber threats. A labeling program to secure such devices would provide American consumers with the peace of mind that the technology being brought into their homes is safe, and incentivize manufacturers to meet higher cybersecurity standards and retailers to market secure devices.
      >
      > Yesterday’s dialogue focused on how to best implement a national cybersecurity labeling program, drive improved security standards for Internet-enabled devices, and generate a globally recognized label. Government and industry leaders discussed the importance of a trusted program to increase security across consumer devices that connect to the Internet by equipping devices with easily recognized labels to help consumers make more informed cybersecurity choices (e.g., an “EnergyStar” for cyber). These conversations build on the foundational work that has been pioneered by the private sector and the National Institute of Standards and Technology (NIST) to help build more secure Internet-connected devices. It also follows President Biden’s Executive Order on Improving the Nation’s Cybersecurity, which highlighted the need for improved IoT security and tasked NIST, in partnership with the Federal Trade Commission, to advance improved cybersecurity standards and standardized product labels for these devices.
      - Related: `$ grep DNA`
- https://csrc.nist.gov/publications/detail/white-paper/2022/11/09/implementing-a-risk-based-approach-to-devsecops/final
  - > DevOps brings together software development and operations to shorten development cycles, allow organizations to be agile, and maintain the pace of innovation while taking advantage of cloud-native technology and practices. Industry and government have fully embraced and are rapidly implementing these practices to develop and deploy software in operational environments, often without a full understanding and consideration of security. Also, most software today relies on one or more third-party components, yet organizations often have little or no visibility into and understanding of how these components are developed, integrated, deployed, and maintained, as well as the practices used to ensure the components’ security. To help improve the security of DevOps practices, the NCCoE is planning a DevSecOps project that will focus initially on developing and documenting an applied risk-based approach and recommendations for secure DevOps and software supply chain practices consistent with the Secure Software Development Framework (SSDF), Cybersecurity Supply Chain Risk Management (C-SCRM), and other NIST, government, and industry guidance. This project will apply these DevSecOps practices in proof-of-concept use case scenarios that will each be specific to a technology, programming language, and industry sector. Both closed source (proprietary) and open source technology will be used to demonstrate the use cases. This project will result in a freely available NIST Cybersecurity Practice Guide.
- https://www.intel.com/content/www/us/en/newsroom/news/2022-intel-innovation-day-2-livestream-replay.html#gs.djq36o
  - Similar to the software labeling, with Alice we are trying to cross these streams
    - Datasheets for Datasets
      - https://arxiv.org/abs/1803.09010
      - > The machine learning community currently has no standardized process for documenting datasets, which can lead to severe consequences in high-stakes domains. To address this gap, we propose datasheets for datasets. In the electronics industry, every component, no matter how simple or complex, is accompanied with a datasheet that describes its operating characteristics, test results, recommended uses, and other information. By analogy, we propose that every dataset be accompanied with a datasheet that documents its motivation, composition, collection process, recommended uses, and so on. Datasheets for datasets will facilitate better communication between dataset creators and dataset consumers, and encourage the machine learning community to prioritize transparency and accountability.

> Side from Andrew Ng's Intel Innovation 2022 Luminary Keynote
> Source: https://www.intel.com/content/www/us/en/newsroom/news/2022-intel-innovation-day-2-livestream-replay.html#gs.iex8mr
> ![image](https://user-images.githubusercontent.com/5950433/193330714-4bcceea4-4402-468f-82a9-51882939452c.png)

- Possible alignment with Andrew's "Data-Centric AI"
 - is the discipline of systematically engineering the data used to build an AI system
   - This is what we're doing with Alice
- Possible alignment with Andrew's "The iterative process of ML development"
  - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#entity-analysis-trinity
  - Intent / Train model
    - Establish correlations between threat model intent and collected data / errors (telemetry or static analysis, policy, failures)
  - Dynamic analysis / Improve data
    - We tweak the code to make it do different things to see different data. The application of overlays. Think over time.
  - Static / Error analysis
    - There might be async debug initiated here but this maps pretty nicely conceptually since we'd think of this as a static process, we already have some errors to analyze if we're at this step.

![Entity Analysis Trinity](https://user-images.githubusercontent.com/5950433/188203911-3586e1af-a1f6-434a-8a9a-a1795d7a7ca3.svg)

- Gist for v2 API call cached: https://gist.github.com/pdxjohnny/ab1bf170dce272cecdd317eae55d1174
- TODO
  - [ ] Clean up SCITT OpenSSF Use Case
    - https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md
    - https://mailarchive.ietf.org/arch/msg/scitt/cxRvcTEUNEhlxE_AJyspdx9y06w/
  - [ ] Get back to Kate
  - [ ] SCIIT for NVD style feed data
    - [ ] Patch CVE Bin Tool to support validation
      - See Dick Brooks's email: https://mailarchive.ietf.org/arch/msg/scitt/cxRvcTEUNEhlxE_AJyspdx9y06w/
        - > Ray’s statement: “I can't imagine that you could ask some other
          > entity other than the mfr that created the device
          > to provide the reference, and attest to it's validity.”
          >
          > This is also true for software vulnerabilities. Only the software product developer has access to the source code needed to answer the question, “Is my software product vulnerable to exploitation by CVE-XYZ?”
          >
          > This is what a NIST VDR provides – a vulnerability disclosure report from a software owner to a customer indicating the vulnerability status of their product at the SBOM component level;
          > - https://energycentral.com/c/pip/what-nist-sbom-vulnerability-disclosure-report-vdr
          >
          > Software vendors provide links to attestations using a Vendor Repose File (VRF), which is yet another artifact that needs to be checked for trustworthiness:
          >
          > - https://energycentral.com/c/pip/advice-software-vendors-prepare-omb-m-22-18-requirements
          >
          > The VDR and VRF are both considered artifacts, which the author is making a statement of trustworthiness, that needs to be vetted by a trusted party, resulting in a claim that gets placed into a trusted registry becoming a “transparent claim” in a SCITT registry.
          >
          > A consumer should be able to query the trustworthiness of the VDR and VRF artifacts using a SCITT Transparency Service, having nothing more than the original VDR and VRF artifacts in their possession.
          - SCITT is awesome because it supports this offline verification
            which is important for us with Alice because we will be running
            in parallel/concurrently across many instances of her. These will
            sometimes compute fully offline (offline RL?). Therefore we want to
            be able to check validity of data before handing off to EDEN nodes
            which might loose connection. This enables them to verify offline
            data push updated in their cache. This allows entities to act in
            accordance with strategic principles by validating data on entry,
            producing receipts offline, and then rejoining those to the other
            nodes receiving those input streams. They need to have these offline
            recpeits when they produce recepits for new input to maintain provenance
            chains (collecting data for inference within a flow running across multiple
            EDEN nodes doing active learning based on perceived trustworthyness of inputs).
  - [ ] Buy fully working mouse
  - [ ] Buy mousepad
  - [ ] Practice on ergonomic keyboard
  - [ ] gif of AOE1 install building for github.com/pdxjohnny/pdxjohnny/README.md
  - [ ] Communicate to Alice she MUST stop creating double issues with todos command
    - Fix the bug
  - [ ] SBOM, VEX, etc. feeds to ActivityPub, websub, RSS, web5 (ATP Data Repositories or if W3C or DIF has something)
    - [ ] Rebuild on trigger
- Future
  - [ ] Auto sync asciinema recs / stream to https://github.com/asciinema/asciinema-server
    - [ ] Conversion to SBOM, VEX, etc. feeds
    - [ ] Coder demo / templates
      - Workspace / template as server
  - [ ] Pull request Atuin to not change the way the up arrow works
  - [ ] Respond to https://mailarchive.ietf.org/arch/msg/scitt/fg6_z2HauVl5d6mklUnMQivE57Y/
        and see if we can collaberate.
  - [ ] Auto sync Atuin https://github.com/ellie/atuin/blob/main/docs/server.md
    - [ ] Conversion to SBOM, VEX, etc. feeds
    - [ ] Coder demo / templates
      - Workspace / template as server