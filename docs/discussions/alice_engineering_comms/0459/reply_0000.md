## 2023-11-22 @pdxjohnny Engineering Logs

```console
$ pip install -I git+https://github.com/wbond/oscrypto.git
```

```python
import aiohttp
import asyncio
import json

async def fetch_dependency_graph(session, owner, repo, token, manifest_cursor=None, dependency_cursor=None):
    # The GraphQL query to fetch the dependency graph manifests
    query = """
    query($owner: String!, $repo: String!, $manifest_cursor: String, $dependency_cursor: String) {
      repository(owner: $owner, name: $repo) {
        dependencyGraphManifests(first: 2, after: $manifest_cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            blobPath
            dependencies(first: 2, after: $dependency_cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              edges {
                node {
                  packageName
                  repository {
                    nameWithOwner
                  }
                  requirements
                }
              }
            }
          }
        }
      }
    }
    """
    
    # Format the variables for the GraphQL query
    variables = {
        "owner": owner,
        "repo": repo,
        "manifest_cursor": manifest_cursor,
        "dependency_cursor": dependency_cursor
    }

    # Headers to be sent with the request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Make the POST request to the GitHub GraphQL API
    async with session.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers) as response:
        return await response.json()

async def generate_sbom(owner, repo, token):
    dependency_manifests = []

    async with aiohttp.ClientSession() as session:
        # Pagination for manifests
        has_manifest_page = True
        manifest_cursor = None
        
        while has_manifest_page:
            # Fetch the dependency graph manifests
            data = await fetch_dependency_graph(session, owner, repo, token, manifest_cursor)
            manifest_nodes = data['data']['repository']['dependencyGraphManifests']['nodes']
            manifest_page_info = data['data']['repository']['dependencyGraphManifests']['pageInfo']
            has_manifest_page = manifest_page_info['hasNextPage']
            manifest_cursor = manifest_page_info['endCursor']

            for manifest_node in manifest_nodes:
                manifest_dependencies = []
                # Start nested pagination on first page for each manifest
                has_dependency_page = True
                dependency_cursor = None

                while has_dependency_page:
                    # Fetch the dependencies for the current manifest
                    manifest_data = await fetch_dependency_graph(session, owner, repo, token, manifest_cursor, dependency_cursor)
                    dependencies = manifest_data['data']['repository']['dependencyGraphManifests']['nodes'][0]['dependencies']['edges']
                    dependency_page_info = manifest_data['data']['repository']['dependencyGraphManifests']['nodes'][0]['dependencies']['pageInfo']
                    
                    for dependency_edge in dependencies:
                        dependency_node = dependency_edge['node']
                        manifest_dependencies.append({
                            "packageName": dependency_node['packageName'],
                            "requirements": dependency_node['requirements'],
                            "repository": dependency_node['repository']['nameWithOwner'] if dependency_node['repository'] else None
                        })

                    has_dependency_page = dependency_page_info['hasNextPage']
                    dependency_cursor = dependency_page_info['endCursor']
                
                dependency_manifests.append({
                    "blobPath": manifest_node['blobPath'],
                    "dependencies": manifest_dependencies
                })

    return { "dependencyGraphManifests": dependency_manifests }

# Run the asynchronous function to generate the SBOM and get the result
sbom_data = asyncio.run(generate_sbom(owner, repo, token))

# Now sbom_data is a dictionary with all the dependencyGraphManifests
# You could pretty print it using json.dumps for example
print(json.dumps(sbom_data, indent=2))
```

- TODO
  - [ ] Request from Orie, review COSE typ header parameter draft
  - [x] git ls-files with aiohttp
    - [x] Example files: https://gist.github.com/52d17fd4d44014fe1b8a15111873454b
    - [ ] GitHub Webhook Notary for SBOM generation
    - [ ] SBOM -> Polling of repos -> GitHub webhook style payload creation -> GitHub Webhook Notary
      - Content addressability of webhook payloads to ensure dedup / polling updated SHAs always trigger new update but never when SHAs not updated