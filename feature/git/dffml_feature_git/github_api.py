import os
import json
import asyncio
import aiohttp

# Your personal access token
# TOKEN = "your_github_access_token"
TOKEN = os.environ["GH_ACCESS_TOKEN"]


# GraphQL query template with pagination for pull requests and files
QUERY_TEMPLATE = """
query($owner: String!, $repoName: String!, $fileName: String!, $prCursor: String, $fileCursor: String) {
  repository(owner: $owner, name: $repoName) {
    pullRequests(first: 100, after: $prCursor, states: [OPEN, MERGED, CLOSED]) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          title
          url
          files(first: 100, after: $fileCursor) {
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

# Replace with your GitHub repositories and the file you want to check
REPOS = [("intel", "dffml"), ("dffml", "dffml-model-transformers")]
# FILE_PATH = ".github/workflows/trigger_on_push_images_containers.yml"
FILE_PATH = "operations/innersource/setup.cfg"


async def fetch_pull_requests(client, owner, repo_name, file_name):
    pr_cursor = None
    fetched_prs = []

    while True:
        variables = {
            "owner": owner,
            "repoName": repo_name,
            "fileName": file_name,
            "prCursor": pr_cursor,
            "fileCursor": None,  # Start without a file cursor
        }
        payload = {"query": QUERY_TEMPLATE, "variables": json.dumps(variables)}
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        }

        async with client.post(
            "https://api.github.com/graphql", headers=headers, json=payload
        ) as response:
            json_data = await response.json()
            data = (
                json_data.get("data", {})
                .get("repository", {})
                .get("pullRequests", {})
            )

            for edge in data.get("edges", []):
                pr = edge["node"]
                file_cursor = None  # Reset for each new pull request

                while True:  # Paginate through files within this pull request
                    file_page_info, files = await fetch_files(
                        client, owner, repo_name, pr["url"], file_cursor
                    )
                    for file_edge in files:
                        if file_edge["node"]["path"] == file_name:
                            fetched_prs.append(
                                pr["url"]
                            )  # This PR modified the file

                    if not file_page_info.get("hasNextPage"):
                        break  # All files have been checked within this pull request
                    file_cursor = file_page_info["endCursor"]

            pr_page_info = data.get("pageInfo", {})
            if not pr_page_info.get("hasNextPage"):
                break  # All pull requests have been fetched for this repository
            pr_cursor = pr_page_info["endCursor"]

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
    }""" % (
        owner,
        repo_name,
        pr_url,
        file_cursor or "",
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    async with client.post(
        "https://api.github.com/graphql", headers=headers, json=payload
    ) as response:
        json_data = await response.json()
        files_data = (
            json_data.get("data", {})
            .get("repository", {})
            .get("pullRequest", {})
            .get("files", {})
        )
        page_info = files_data.get("pageInfo", {})
        files = files_data.get("edges", [])
        return page_info, files


async def main(repos, file_name):
    async with aiohttp.ClientSession(trust_env=True) as client:
        tasks = [
            fetch_pull_requests(client, owner, repo, file_name)
            for owner, repo in repos
        ]
        for future in asyncio.as_completed(tasks):
            owner, repo, prs = await future
            print(
                f"Fetched pull requests for {owner}/{repo} that modify '{file_name}':"
            )
            print(prs)


if __name__ == "__main__":
    asyncio.run(main(REPOS, FILE_PATH))

# The GraphQL query template
QUERY_TEMPLATE = """
query($repo_name: String!, $owner: String!) {
  repository(name: $repo_name, owner: $owner) {
    pullRequests(first: 10, states: OPEN) {
      nodes {
        title
        files(first: 10) {
          nodes {
            path
          }
        }
      }
    }
  }
}
"""

OLD = """
query ($owner: String!, $name: String!, $expression: String!) {
  repository(owner: $owner, name: $name) {
    object(expression: $expression) {
      ... on Commit {
        associatedPullRequests(first: 5) {
          nodes {
            title
            url
            changedFiles
          }
        }
      }
    }
  }
}
"""


async def old_fetch_prs(session, owner, repo, file_path):
    payload = {
        "query": QUERY_TEMPLATE,
        "variables": {
            "owner": owner,
            "name": repo,
            # "expression": f"HEAD:{file_path}",
            "path": file_path,
        },
    }
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    async with session.post(
        "https://api.github.com/graphql", json=payload, headers=headers
    ) as response:
        prs = await response.json()
        return (owner, repo, prs)


async def old_main(repos, file_path):
    async with aiohttp.ClientSession(trust_env=True) as session:
        # Start all tasks
        tasks = [
            fetch_prs(session, owner, repo, file_path) for owner, repo in repos
        ]

        # Process tasks as they complete
        for completed in asyncio.as_completed(tasks):
            owner, repo, pr_data = await completed
            print(f"Pull requests for repo {owner}/{repo}:")
            print(json.dumps(pr_data, indent=2))
