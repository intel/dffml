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


import github
from github import Github
from github import GithubException

import snoop


def sync_fork(upstream, fork, branch):
    try:
        print(f"Successfully synced {fork} branch {branch} with {upstream}")
    except Exception as error:
        raise Exception(
            f"Unable to sync {fork} with {upstream} due to {error}"
        ) from error


@snoop
def make_github_operations(
    token, repo_urls, new_branch_name, transform_file_content
):
    g = Github(token)
    user = g.get_user()

    for repo_url in repo_urls:
        try:
            # Fork the repository
            org, repo_name = repo_url.split("/")[-2:]
            repo = g.get_repo(f"{org}/{repo_name}")
            fork = user.create_fork(repo)

            # Create a new branch from the default branch
            fork_default_branch = fork.get_branch(fork.default_branch)
            try:
                fork.create_git_ref(
                    ref="refs/heads/" + new_branch_name,
                    sha=fork_default_branch.commit.sha,
                )
            except github.GithubException as error:
                if "Reference already exists" not in str(error):
                    raise

            # Get the sha of the last commit to the branch in the upstream repo
            upstream_default_branch_sha = repo.get_branch(
                repo.default_branch
            ).commit.sha

            # Get the git ref of the branch in the forked repo
            new_branch_ref = fork.get_git_ref(f"heads/{new_branch_name}")

            # Update the git ref to point to the new sha
            new_branch_ref.edit(upstream_default_branch_sha, force=True)

            # Update the contents of testing.yml
            file_path = ".github/workflows/testing.yml"
            try:
                pygithub_fileobj = fork.get_contents(
                    file_path, ref=new_branch_name
                )
            except GithubException as error:
                raise Exception(
                    f"{file_path} does not exist in {repo_url}, unable to update."
                ) from error

            # Transform the content
            content = transform_file_content(pygithub_fileobj.decoded_content)

            # Update file content
            fork.update_file(
                pygithub_fileobj.path,
                "Update testing.yml",
                content,
                pygithub_fileobj.sha,
                branch=new_branch_name,
            )

            # Create Pull request
            base_repo = repo
            snoop.pp(fork)
            base = base_repo.default_branch
            head = f"{user.login}:{fork.name}:{new_branch_name}"
            base_repo.create_pull(
                title="Update testing.yml", body="", head=head, base=base
            )

        except GithubException as e:
            print(
                f"Unable to complete operations for {repo_url} due to {str(e)}"
            )


import pathlib


repo_urls = list(["/".join(["https://github.com", *repo]) for repo in REPOS])
token = TOKEN
new_branch_name = "update-testing-workflow"
file_content = (
    pathlib.Path(__file__)
    .parents[3]
    .joinpath(
        ".github",
        "workflows",
        "testing.yml",
    )
    .read_text()
)


async def main(repos, file_name):
    make_github_operations(
        token, repo_urls, new_branch_name, lambda content: content.upper()
    )
    return
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
