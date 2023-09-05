"""
Usage
*****

.. code-block:: console

    $ python -u scripts/dump_discussion.py --token $(gh auth token) --owner $(git remote get-url upstream | sed -e 's/.*github.com\///g' | sed -e 's/\/.*//g') --repo $(git remote get-url upstream | sed -e 's/.*\///g') --discussion-number 1406 | tee 1406.json
"""
import os
import asyncio
import aiohttp
import json
from dataclasses import dataclass
from typing import List
import argparse

@dataclass
class Reply:
    body: str

@dataclass
class Comment:
    body: str
    replies: List[Reply]

@dataclass
class Discussion:
    title: str
    comments: List[Comment]

async def fetch_discussion_data(session, token, owner, repo, discussion_number):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    query = """
    query($owner: String!, $repo: String!, $discussionNumber: Int!, $commentsCursor: String, $repliesCursor: String) {
      repository(owner: $owner, name: $repo) {
        discussion(number: $discussionNumber) {
          title
          comments(first: 100, after: $commentsCursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              body
              replies(first: 100, after: $repliesCursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  body
                }
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "owner": owner,
        "repo": repo,
        "discussionNumber": discussion_number
    }

    discussion_data = []
    has_next_page = True
    comments_cursor = None

    while has_next_page:
        variables["commentsCursor"] = comments_cursor
        response = await session.post("https://api.github.com/graphql", headers=headers, json={"query": query, "variables": variables})
        result = await response.json()

        discussion_title = result["data"]["repository"]["discussion"]["title"]
        comments = result["data"]["repository"]["discussion"]["comments"]["nodes"]
        has_next_page = result["data"]["repository"]["discussion"]["comments"]["pageInfo"]["hasNextPage"]
        comments_cursor = result["data"]["repository"]["discussion"]["comments"]["pageInfo"]["endCursor"]

        for comment in comments:
            comment_body = comment["body"]
            replies = []

            has_next_reply_page = True
            replies_cursor = None

            while has_next_reply_page:
                variables["repliesCursor"] = replies_cursor
                response = await session.post("https://api.github.com/graphql", headers=headers, json={"query": query, "variables": variables})
                reply_result = await response.json()

                reply_nodes = reply_result["data"]["repository"]["discussion"]["comments"]["nodes"][0]["replies"]["nodes"]
                has_next_reply_page = reply_result["data"]["repository"]["discussion"]["comments"]["nodes"][0]["replies"]["pageInfo"]["hasNextPage"]
                replies_cursor = reply_result["data"]["repository"]["discussion"]["comments"]["nodes"][0]["replies"]["pageInfo"]["endCursor"]

                for reply in reply_nodes:
                    replies.append(Reply(body=reply["body"]))

            discussion_data.append(Comment(body=comment_body, replies=replies))

    return Discussion(title=discussion_title, comments=discussion_data)

async def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub discussion data")
    parser.add_argument("--token", help="GitHub Access Token")
    parser.add_argument("--owner", help="GitHub Repository Owner")
    parser.add_argument("--repo", help="GitHub Repository Name")
    parser.add_argument("--discussion-number", type=int, help="GitHub Discussion Number")
    args = parser.parse_args()

    async with aiohttp.ClientSession(trust_env=True) as session:
        discussion_data = await fetch_discussion_data(session, args.token, args.owner, args.repo, args.discussion_number)
        print(json.dumps(discussion_data, default=lambda x: x.__dict__, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
