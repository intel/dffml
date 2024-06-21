## 2024-06-17 @pdxjohnny Engineering Logs

- prompt: Can you please write me a file called docs/parsers.md which documents the functionality added in this patch. Please return your response markdown as an attachment?
  - prompt: In the documentation please explain in detail including setting up a new package and entrypoint and class referenced through setup.cfg to and entry_points.txt via file:. Use the added bandit parser as the example plugin we implement.
    - Branch by abstraction and implement as example first
    - https://gist.github.com/deb3384d1ab7abfc49221ef4089b110d
  - prompt: Please include the contents of the added banditparser file and explain what each part does. Write it in rst and use includefile for static_analysis_bandit.py
- TODO
  - [ ] patch[set] documentation for federated train of thought query with git blame. This dirty tree looks like it would gen these changelogs / docs if rebased in upstream. Git blame (aka kernel authors for CC) and query their hypothesized and executed trains of thought to see if the users train of thought avoids known bad trains of thought. Help the user correct via ad-hoc CVE feedback loop process to align with yellow brick road.
  - [ ] https://github.com/intel/cve-bin-tool/pull/4200
    - 🛤️🛤️🛤️🛤️🛤️🛤️🛤️
      - We can do out-of-tree ad-hoc CVE IDs to facilitate the poly repo maintainer AGI loop