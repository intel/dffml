## 2023-11-14 @pdxjohnny Engineering Logs

- https://community.intel.com/t5/Blogs/Products-and-Solutions/Security/Introducing-Attested-Containers/post/1539199
  - https://github.com/intel/ACON/issues/51
- https://github.com/aquasecurity/trivy/blob/main/docs/docs/supply-chain/vex.md#openvex
- https://github.com/aquasecurity/trivy/pull/5466
- https://github.com/pdxjohnny/scitt-api-emulator/blob/demo-instance/docs/slsa_in_toto.md

### S2C2F

Upstream for S2C2F sections: https://github.com/ossf/s2c2f/blob/98803e0a558e6d8cef4d2770864ffd3cf7618c65/specification/framework.md#appendix-relation-to-scitt

#### Appendix: Relation to SCITT

> The [Supply Chain Integrity, Transparency, and Trust](https://github.com/ietf-scitt) initiative, or SCITT, is a set of proposed industry standards for managing the compliance of goods and services across end-to-end supply chains. In the future, we expect teams to output "attestations of conformance" to the S2C2F requirements and store it in SCITT. The format of such attestations is to be determined.

#### Appendix: Mapping Secure Supply Chain Consumption Framework Requirements to Other Specifications

Goal: Create YAML file allowing users to map webhook event data to creation of data notarized by SCITT, statments and receipts created. Use YAML as basis for overall automatable format for alignment to S2C2F.

Use presence of data in respective feeds/subjects to determine overall result (URL or RDF + jq / jsonpath?)

| **Requirement ID** | **Requirement Title** | **References** |
| --- | --- | --- |
| ING-1 | Use package managers trusted by your organization | |
| ING-2 | Use an OSS binary repository manager solution | |
| ING-3 | Have a Deny List capability to block known malicious OSS from being consumed | |
| ING-4 | Mirror a copy of all OSS source code to an internal location | |
| SCA-1 | Scan OSS for known vulnerabilities | https://deps.dev |
| SCA-2 | Scan OSS for licenses | https://deps.dev |
| SCA-3 | Scan OSS to determine if its end-of-life | |
| SCA-4 | Scan OSS for malware | clamav workflow or job, virustotal API? |
| SCA-5 | Perform proactive security review of OSS | OpenSSF Scorecard |
| INV-1 | Maintain an automated inventory of all OSS used in development | analysis of dev-requirements, package.json dev, etc. |
| INV-2 | Have an OSS Incident Response Plan | SECURITY.md |
| UPD-1 | Update vulnerable OSS manually | Watch for human approval on renovate/dependabot pull requests |
| UPD-2 | Enable automated OSS updates | Presence of renovate/dependabot pull requests |
| UPD-3 | Display OSS vulnerabilities as comments in Pull Requests (PRs) | |
| AUD-1 | Verify the provenance of your OSS |  |
| AUD-2 | Audit that developers are consuming OSS through the approved ingestion method | |
| AUD-3 | Validate integrity of the OSS that you consume into your build | no network build with content addressed deps aka dockerfiles or melange |
| AUD-4 | Validate SBOMs of OSS that you consume into your build | |
| ENF-1 | Securely configure your package source files (i.e. nuget.config, .npmrc, pip.conf, pom.xml, etc.) | |
| ENF-2 | Enforce usage of a curated OSS feed that enhances the trust of your OSS | |
| REB-1 | Rebuild the OSS in a trusted build environment, or validate that it is reproducibly built | |
| REB-2 | Digitally sign the OSS you rebuild | docs: slsa_in_toto |
| REB-3 | Generate SBOMs for OSS that you rebuild | docs: slsa_in_toto |
| REB-4 | Digitally sign the SBOMs you produce | docs: slsa_in_toto |
| FIX-1 | Implement a change in the code to address a zero-day vulnerability, rebuild, deploy to your organization, and confidentially contribute the fix to the upstream maintainer | |