import os
import json
import random
import urllib.request
from typing import Dict, Any

GITHUB_API_URL: str = "https://api.github.com/graphql"
GITHUB_SEARCH: str = json.dumps(
    {
        "query": """
query {
    search(query: "%s", type: REPOSITORY, first: 10) {
        nodes {
            ... on Repository {
                url
            }
        }
    }
}
"""
    }
)


def get_repos(query: str, github_token: str) -> dict:
    # Repos organized by their URL with their value being their feature data
    repos: Dict[str, Dict[str, Any]] = {}
    # Make the request to the GitHub API
    with urllib.request.urlopen(
        urllib.request.Request(
            GITHUB_API_URL, headers={"Authorization": f"Bearer {github_token}"}
        ),
        data=(GITHUB_SEARCH % (query,)).encode(),
    ) as response:
        # Loop through the 100 repos that were returned
        for node in json.load(response)["data"]["search"]["nodes"]:
            # Randomly assign a maintenance status for demo purposes
            repos[node["url"]] = {
                "features": {"maintained": random.choice([0, 1])}
            }
    return repos
