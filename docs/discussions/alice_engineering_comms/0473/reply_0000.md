## 2023-12-06 @pdxjohnny Engineering Logs

Won't you federate supply chain events with me neighbor?

It's always a beautiful day in the neighborhood to strengthen open source supply chain security. The Internet Engineering Task Force (IETF) is working on "An Architecture for Trustworthy and Transparent Digital Supply Chains" within it's Supply Chain Integrity Transparency and Trust (SCITT) working group. The architecture describes a Concise Binary Object Representation (CBOR) based API for creating transparent statements. The SCITT architecture and it's for not require trust in a single centralized Transparency Service.

This talk will build on Federation work from the IETF 118 hacakthon demo'd in the SCITT meeting: https://www.youtube.com/watch?v=zEGob4oqca4&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=12&t=5350s

- https://sessionize.com/ossna2024/

```python

# GraphQL query template with pagination for pull requests and files
QUERY_TEMPLATE = """
query($owner: String!, $repoName: String!, $fileName: String!, $prCursor: String, $fileCursor: String) {
  repository(owner: $owner, name: $repoName) {
    pullRequests(first: 5, after: $prCursor, states: [OPEN, MERGED, CLOSED]) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          title
          url
          files(first: 5, after: $fileCursor) {
            pageInfo {
              endCursor
              hasNextPage
            }
            edges {
              node {
                path
              }
            }
          }
        }
      }
    }
  }
}
"""

# Example repository list and the file path to search for
REPOS = [('owner1', 'repo1'), ('owner2', 'repo2')]
FILE_PATH = "path/to/your/file.txt"

async def fetch_pull_requests(client, owner, repo_name, file_name):
    pr_cursor = None
    fetched_prs = []

    while True:
        variables = {
            'owner': owner,
            'repoName': repo_name,
            'fileName': file_name,
            'prCursor': pr_cursor,
            'fileCursor': None  # Start without a file cursor
        }
        payload = {
            'query': QUERY_TEMPLATE,
            'variables': json.dumps(variables)
        }
        headers = {
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json',
        }

        async with client.post('https://api.github.com/graphql', headers=headers, json=payload) as response:
            json_data = await response.json()
            data = json_data.get('data', {}).get('repository', {}).get('pullRequests', {})
            
            for edge in data.get('edges', []):
                pr = edge['node']
                file_cursor = None  # Reset for each new pull request

                while True:  # Paginate through files within this pull request
                    file_page_info, files = await fetch_files(client, owner, repo_name, pr['url'], file_cursor)
                    for file_edge in files:
                        if file_edge['node']['path'] == file_name:
                            fetched_prs.append(pr['url'])  # This PR modified the file
                            
                    if not file_page_info.get('hasNextPage'):
                        break  # All files have been checked within this pull request
                    file_cursor = file_page_info['endCursor']

            pr_page_info = data.get('pageInfo', {})
            if not pr_page_info.get('hasNextPage'):
                break  # All pull requests have been fetched for this repository
            pr_cursor = pr_page_info['endCursor']
            
    return owner, repo_name, fetched_prs

async def fetch_files(client, owner, repo_name, pr_url, file_cursor):
    query = """
    {
      repository(owner: "%s", name: "%s") {
        pullRequest(url: "%s") {
          files(after: "%s", first: 100) {
            pageInfo {
              endCursor
              hasNextPage
            }
            edges {
              node {
                path
              }
            }
          }
        }
      }
    }""" % (owner, repo_name, pr_url, file_cursor or '')

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {'query': query}

    async with client.post('https://api.github.com/graphql', headers=headers, json=payload) as response:
        json_data = await response.json()
        files_data = json_data.get('data', {}).get('repository', {}).get('pullRequest', {}).get('files', {})
        page_info = files_data.get('pageInfo', {})
        files = files_data.get('edges', [])
        return page_info, files

async def main(repos, file_name):
    async with aiohttp.ClientSession(trust_env=True) as client:
        tasks = [fetch_pull_requests(client, owner, repo, file_name) for owner, repo in repos]
        for future in asyncio.as_completed(tasks):
            owner, repo, prs = await future
            print(f"Fetched pull requests for {owner}/{repo} that modify '{file_name}':")
            print(prs)

if __name__ == '__main__':
    asyncio.run(main(REPOS, FILE_PATH))
```

![image](https://github.com/intel/dffml/assets/5950433/0ac22f17-d8e0-4e29-80b9-8423af4497e6)

- TODO
  - [ ] Think about federation from the CBOR API perspective