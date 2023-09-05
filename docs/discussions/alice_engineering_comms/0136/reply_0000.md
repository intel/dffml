## 2023-01-03 @pdxjohnny Engineering Logs

-  https://community.intel.com/t5/Blogs/Tech-Innovation/open-intel/Open-Source-Policy-Why-It-s-Not-Just-For-Wonks-Anymore/post/1439707
- https://github.com/ossf/security-insights-spec#security-insightsyml
  - Ping Terri and Arjan to pursue scanner noise reduction efforts
    - https://github.com/ossf/security-insights-spec#security-insightsyml could merge with existing triage format and check regex / rules for applicability if not able to set within context
    - Threshold declaration for false positives
      - Acceptance based on receipt knowledge graph traversal for those trust chains

### Fixing CI

- Switching to Python 3.9 as minimum supported version (3.11 is latest)
- References
  - https://github.com/scipy/scipy/issues/9005#issuecomment-632236655

---

- TODO
  - [x] Container build
  - [ ] Single workflow which runs rest of plugins
  - [ ] Stream of consiousness (downstream tiggers)
  - [ ] Downstream validation example (VDR or VEX or somethign else?)