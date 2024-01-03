## 2022-09-28 Andrew Ng's Intel Innovation Luminary Keynote Notes

- References
  - "joint AI Developer Program where developers can train, test, and deploy their AI models."
    - https://twitter.com/intel/status/1575221403409866752
  - https://www.intel.com/content/www/us/en/newsroom/news/2022-intel-innovation-day-2-livestream-replay.html#gs.djq36o
  - https://datacentricai.org/
    - Datasheets for Datasets
      - https://arxiv.org/abs/1803.09010
      - > The machine learning community currently has no standardized process for documenting datasets, which can lead to severe consequences in high-stakes domains. To address this gap, we propose datasheets for datasets. In the electronics industry, every component, no matter how simple or complex, is accompanied with a datasheet that describes its operating characteristics, test results, recommended uses, and other information. By analogy, we propose that every dataset be accompanied with a datasheet that documents its motivation, composition, collection process, recommended uses, and so on. Datasheets for datasets will facilitate better communication between dataset creators and dataset consumers, and encourage the machine learning community to prioritize transparency and accountability.
- AI = Code + Data  
  - The code is a solved problem!!! Get it off GitHub or something!

![image](https://user-images.githubusercontent.com/5950433/193328916-b9232099-79b1-4c3d-9b7a-768822249630.png)

- Slides
  - Data-Centric AI
    - is the discipline of systematically engineering the data used to build an AI system
      - (This is what we're doing with Alice)

![image](https://user-images.githubusercontent.com/5950433/193330714-4bcceea4-4402-468f-82a9-51882939452c.png)

---

- Alignment
  - The iterative process of ML development
    - https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#entity-analysis-trinity
    - Intent / Train model
      - Establish correlations between threat model intent and collected data / errors (telemetry or static analysis, policy, failures)
    - Dynamic analysis / Improve data
      - We tweak the code to make it do different things to see different data. The application of overlays. Think over time.
    - Static / Error analysis
      - There might be async debug initiated here but this maps pretty nicely conceptually since we'd think of this as a static process, we already have some errors to analyze if we're at this step.

![Entity Analysis Trinity](https://user-images.githubusercontent.com/5950433/188203911-3586e1af-a1f6-434a-8a9a-a1795d7a7ca3.svg)