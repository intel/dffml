- https://docs.teodev.io/getting-started/beginner-tutorial/write-a-schema-only-app
- https://docs.ray.io/en/latest/ray-overview/getting-started.html
- https://github.com/opea-project/Governance/blob/main/charter.md
- https://github.com/opea-project/GenAIComps/tree/main/comps/retrievers
- We need to put OPEA behind litellm or something

```bash
gh api graphql -f query='
  query {
    repository(owner: "intel", name: "dffml") {
      dependencyGraphManifests {
        totalCount
        nodes {
          blobPath
          dependencies {
            totalCount
            nodes {
              packageName
              requirements
            }
          }
        }
      }
    }
  }
```

```
jq -r '.data.repository.dependencyGraphManifests.nodes[].dependencies.nodes[].packageName'
```

```json
{
  "data": {
    "repository": {
      "dependencyGraphManifests": {
        "totalCount": 60,
        "nodes": [
          {
            "blobPath": "/intel/dffml/blob/main/pyproject.toml",
            "dependencies": {
              "totalCount": 0,
              "nodes": []
            }
          },
          {
            "blobPath": "/intel/dffml/blob/main/requirements-dev.txt",
            "dependencies": {
              "totalCount": 22,
              "nodes": [
                {
                  "packageName": "autoflake",
                  "requirements": ""
                },
                {
                  "packageName": "black",
                  "requirements": "= 24.4.2"
                },
                {
                  "packageName": "codecov",
                  "requirements": ""
                },
                {
                  "packageName": "coverage",
                  "requirements": ""
                },
                {
                  "packageName": "httptest",
                  "requirements": ">= 0.0.17"
                },
                {
                  "packageName": "ipykernel",
                  "requirements": ""
                },
                {
                  "packageName": "ipython",
                  "requirements": ""
                },
                {
                  "packageName": "ipywidgets",
                  "requirements": ""
                },
```