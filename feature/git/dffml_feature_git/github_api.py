import os
import sys
import json
import time
import asyncio
import logging

import aiohttp

logger = logging.getLogger(__name__)

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


@snoop
def make_github_operations(
    token,
    repo_urls,
    new_branch_name,
    make_commit_message,
    make_pull_request_body,
    transform_file_content,
    fail_on_not_present: bool = True,
):
    g = Github(token)
    user = g.get_user()

    for repo_url in repo_urls:
        try:
            # Fork the repository
            print("\n\n\n\nUPDATING FOR", repo_url, "\n\n\n", file=sys.stderr)
            org, repo_name = repo_url.split("/")[-2:]
            repo = g.get_repo(f"{org}/{repo_name}")
            fork = user.create_fork(repo)

            # Create a new branch from the default branch
            fork_not_ready_error = None
            for i in range(0, 5):
                try:
                    fork_default_branch = fork.get_branch(fork.default_branch)
                    fork_not_ready_error = None
                    break
                except github.GithubException as error:
                    fork_not_ready_error = error
                    time.sleep(2)
            if fork_not_ready_error is not None:
                try:
                    raise Exception(
                        "Fork not yet ready"
                    ) from fork_not_ready_error
                except Exception as error:
                    logger.error(error)
                    continue

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
            file_path = ".github/workflows/pin_downstream.yml"
            old_content = None
            try:
                pygithub_fileobj = fork.get_contents(
                    file_path, ref=new_branch_name
                )
                old_content = pygithub_fileobj.decoded_content
            except GithubException as error:
                msg = f"{file_path} does not exist in {repo_url}"
                if fail_on_not_present:
                    raise Exception(f"{msg}, unable to update") from error
                else:
                    logger.info(msg)

            commit_message = make_commit_message(repo, fork, old_content)
            pull_request_body = make_pull_request_body(repo, fork, old_content)

            # Transform the content
            content = transform_file_content(repo, fork, old_content)

            # Update file content
            if old_content:
                fork.update_file(
                    file_path,
                    commit_message,
                    content,
                    pygithub_fileobj.sha,
                    branch=new_branch_name,
                )
            else:
                fork.create_file(
                    file_path,
                    commit_message,
                    content,
                    branch=new_branch_name,
                )

            # Create Pull request
            base_repo = repo
            snoop.pp(fork)
            base = base_repo.default_branch
            head = f"{user.login}:{fork.name}:{new_branch_name}"
            pr = base_repo.create_pull(
                title=commit_message,
                body=pull_request_body,
                head=head,
                base=base,
            )

            print(
                "\n\n\n\nUPDATED SUCCESSFULLY",
                pr.html_url,
                "\n\n\n",
                file=sys.stderr,
            )

        except Exception as error:
            try:
                raise Exception(
                    f"Unable to complete operations for {repo_url} due to {error}"
                ) from error
            except Exception as error:
                logger.error(error)


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
        "pin_downstream.yml",
    )
    .read_bytes()
)


async def main(repos, file_name):
    commit_message = os.environ["COMMIT_MESSAGE"]
    pull_request_body = os.environ["PULL_REQUEST_BODY"]
    make_github_operations(
        token,
        repo_urls,
        new_branch_name,
        lambda _upstream, _fork, _old_content: commit_message,
        lambda _upstream, fork, _old_content: pull_request_body.replace(
            "REPO_ORG/REPO_NAME",
            fork.full_name,
        ),
        lambda upstream, _fork, old_content: (
            old_content if old_content is not None else file_content
        )
        .decode()
        .replace(
            "- master",
            f"- {upstream.default_branch}",
        ),
        fail_on_not_present=False,
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


import aiohttp
import contextlib
from pydantic import BaseModel, Field
from gidgethub.aiohttp import GitHubAPI
from typing import Any, Dict, List


class GitHubQuery(BaseModel):
    query: str
    variables: dict


class WorkflowRun(BaseModel):
    id: str
    name: str
    created_at: str
    logs_url: str


class GitHubResponse(BaseModel):
    data: dict
    errors: list = None


class GitHubClient(BaseModel):
    token: str
    username: str
    session: aiohttp.ClientSession = None
    gh: GitHubAPI = None

    class Config:
        arbitrary_types_allowed = True

    async def __aenter__(self):
        self._exit_stack = contextlib.AsyncExitStack()
        await self._exit_stack.__aenter__()
        self.session = await self._exit_stack.enter_async_context(
            aiohttp.ClientSession()
        )
        self.gh = GitHubAPI(
            self.session, self.username, oauth_token=self.token
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._exit_stack.__aexit__(exc_type, exc, tb)

    async def fetch_workflow_runs(
        self, owner: str, repo: str, start_date: str, end_date: str
    ) -> List[WorkflowRun]:
        with snoop():
            query = GitHubQuery(
                query="""
                query($owner: String!, $repo: String!, $start_date: DateTime!, $end_date: DateTime!) {
                    repository(owner: $owner, name: $repo) {
                        workflows {
                            nodes {
                                runs(first: 100, createdAfter: $start_date, createdBefore: $end_date, orderBy: {field: CREATED_AT, direction: DESC}) {
                                    nodes {
                                        id
                                        name
                                        createdAt
                                        logsUrl
                                    }
                                }
                            }
                        }
                    }
                }
                """,
                variables={
                    "owner": owner,
                    "repo": repo,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            response_data = await self.gh.post("/graphql", data=query.dict())
            response = GitHubResponse(**response_data)
            runs = response.data["repository"]["workflowRuns"]["nodes"]
            return [WorkflowRun(**run) for run in runs]

    async def download_log(self, url: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3.raw",
        }
        async with self.session.get(url, headers=headers) as response:
            return await response.text()


async def fetch_and_parse_workflow_logs(
    client: GitHubClient, owner: str, repo: str, start_date: str, end_date: str
):
    with snoop():
        runs = await client.fetch_workflow_runs(owner, repo, start_date, end_date)
        for run in runs:
            log_content = await client.download_log(run.logs_url)
            parse_workflow_logs(log_content)


def parse_workflow_logs(log_content: str):
    # Implement your log parsing logic here
    print("Parsing log content...")
    print(
        log_content[:500]
    )  # Print the first 500 characters for demonstration


async def main():
    with snoop():
        token = os.environ["GH_TOKEN"]
        owner, repo = os.environ["REPO_NAME_WITH_OWNER"].split("/")
        start_date = os.environ["START_DATE"]
        # Date format: "2022-01-01T00:00:00Z"
        end_date = os.environ["END_DATE"]

        async with GitHubClient(token=token, username=owner) as client:
            await fetch_and_parse_workflow_logs(
                client, owner, repo, start_date, end_date
            )


if __name__ == "__main__":
    asyncio.run(main())
