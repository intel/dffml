## 2024-01-05 @pdxjohnny Engineering Logs

- https://github.com/langchain-ai/langchain/issues/15580#issuecomment-1878528580
- https://docs.rs/reqwest/latest/reqwest/struct.Response.html
- https://en.wikipedia.org/wiki/Holacracy
- Advanced patterns for GitHub's GraphQL API - https://www.youtube.com/watch?v=i5pIszu9MeM&t=719s
  - https://github.com/intel/dffml/blob/main/scripts/dump_discussion.py
  - https://github.com/toast-ninja/github-analytics-starter
- https://github.com/openvex/generate-vex/pull/1

```
vexctl generate pkg:github/$(git remote get-url origin | sed -e 's/https:\/\/github.com\///')@$(git log -n 1 --pretty=format:%H) --templates=.openvex/templates/ --file=.openvex/$(git log -n 1 --pretty=format:%H).openvex.json
```

- https://aquasecurity.github.io/trivy/v0.44/docs/supply-chain/vex/
- TODO
  - [x] Improve and auto dump discussion thread
    - https://github.com/intel/dffml/pull/1483