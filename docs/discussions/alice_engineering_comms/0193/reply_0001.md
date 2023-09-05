## 2023-03-01 CVE Bin Tool Monthly

- If you want to be a mentor please ping Terri
- https://github.com/intel/cve-bin-tool/issues?q=is%3Aissue+is%3Aopen+label%3Agsoc
- https://github.com/intel/cve-bin-tool/issues/2633
- https://blogs.python-gsoc.org/en/
- https://github.com/intel/cve-bin-tool/issues/2756
- Dependabot issues are from tests
- Ideally we'd get CVE Bin Tool to be considered equivlant, there are more features for triage and exclusion rules
  - Ideally we work with dependabot to align formats
  - https://github.com/intel/cve-bin-tool/issues/2639

![image](https://user-images.githubusercontent.com/5950433/222214226-0091a5f9-4d10-4882-bbcf-6068503f23bc.png)

- Anthony was at FOSDEM
  - SW360 seems to be moving in a similar direction
  - No one is quite as mature as cve-bin-tool at handling all the SBOM types
    - Anthony sees maturing the triage process as a high value area, especially for GSOC
  - CycloneDX moving faster format spec iteration wise
    - Some nice features on their roadmap
  - Issues in terms of identifying products
    - Mapping naming of products to releases is an ongoing issue most people struggle with
      - Ideally we start all using PURL to help start identifying the right products and versions.
  - Major healthcare providers understand there will be some vulns on release
    - Threat model can help us understand if they matter to deployment
      - [THREATS.md](https://github.com/johnlwhiteman/living-threat-models)
      - [2023-02-22 CVE Bin Tool Monthly Meeting](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-5079592)