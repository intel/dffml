r"""
Usage
*****

.. code-block:: console

    $ python -u scripts/dump_discussion.py --token $(gh auth token) --owner $(git remote get-url upstream | sed -e 's/.*github.com\///g' | sed -e 's/\/.*//g') --repo $(git remote get-url upstream | sed -e 's/\/$//g' -e 's/.*\///g') --discussion-number 1406 | tee 1406.json
"""
import os
import asyncio
import aiohttp
import json
from dataclasses import dataclass
from typing import List
import logging
import argparse

logger = logging.getLogger(__file__)

@dataclass
class Reply:
    id: str
    body: str

@dataclass
class Comment:
    id: str
    body: str
    replies: List[Reply]

@dataclass
class Discussion:
    body: str
    title: str
    comments: List[Comment]

async def fetch_discussion_data(session, graphql_url, token, owner, repo, discussion_number):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    comments_query = """
    query($owner: String!, $repo: String!, $discussionNumber: Int!, $commentsCursor: String) {
      repository(owner: $owner, name: $repo) {
        discussion(number: $discussionNumber) {
          title
          body
          comments(first: 100, after: $commentsCursor) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              id
              body
            }
          }
        }
      }
    }
    """
    replies_query = """
    query($discussionCommentIds: [ID!]!){
      nodes(ids: $discussionCommentIds) {
        ... on DiscussionComment {
          id
          replies(first: 10) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              id
              body
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
    comments_by_id = {}
    comments_by_id_lock = asyncio.Lock()
    discussion_title = None
    discussion_body = None

    async def paginate_replies(tg, batch_comment_ids):
        nonlocal comments_by_id
        nonlocal comments_by_id_lock

        logger.debug("Sending nested replies pagination query: %r: %s", variables, replies_query)
        response = await session.post(graphql_url, headers=headers, json={"query": replies_query, "variables": {"discussionCommentIds": batch_comment_ids}})
        result = await response.json()
        logger.debug("Received nested replies comments pagination query result: %s", json.dumps(result, indent=4, sort_keys=True))

        for comment in result["data"]["nodes"]:
            reply_nodes = comment["replies"]["nodes"]
            has_next_page = comment["replies"]["pageInfo"]["hasNextPage"]
            replies_cursor = comment["replies"]["pageInfo"]["endCursor"]

            async with comments_by_id_lock:
                for reply in reply_nodes:
                    comments_by_id[comment["id"]].replies.append(Reply(id=reply["id"], body=reply["body"]))

            if has_next_page:
                raise NotImplementedError()

    async def paginate_comments(tg, comments_cursor = None):
        nonlocal comments_by_id
        nonlocal comments_by_id_lock
        nonlocal discussion_title
        nonlocal discussion_body

        variables["commentsCursor"] = comments_cursor
        logger.debug("Sending top level comments pagination query: %r: %s", variables, comments_query)
        response = await session.post(graphql_url, headers=headers, json={"query": comments_query, "variables": variables})
        result = await response.json()
        logger.debug("Received top level comments pagination query result: %s", json.dumps(result, indent=4, sort_keys=True))

        discussion_title = result["data"]["repository"]["discussion"]["title"]
        discussion_body = result["data"]["repository"]["discussion"]["body"]
        comments = result["data"]["repository"]["discussion"]["comments"]["nodes"]
        has_next_page = result["data"]["repository"]["discussion"]["comments"]["pageInfo"]["hasNextPage"]
        comments_cursor = result["data"]["repository"]["discussion"]["comments"]["pageInfo"]["endCursor"]

        batch_comment_ids = []

        async with comments_by_id_lock:
            for comment in comments:
                comment = Comment(id=comment["id"], body=comment["body"], replies=[])
                comments_by_id[comment.id] = comment
                batch_comment_ids.append(comment.id)
                discussion_data.append(comment)

        tg.create_task(paginate_replies(tg, batch_comment_ids))

        if has_next_page:
            tg.create_task(paginate_comments(tg, comments_cursor))

    async with asyncio.TaskGroup() as tg:
        tg.create_task(paginate_comments(tg, None))

    return Discussion(title=discussion_title, body=discussion_body, comments=discussion_data)

async def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub discussion data")
    parser.add_argument("--token", help="GitHub Access Token")
    parser.add_argument("--owner", help="GitHub Repository Owner")
    parser.add_argument("--repo", help="GitHub Repository Name")
    parser.add_argument("--discussion-number", type=int, help="GitHub Discussion Number")
    parser.add_argument("--api", help="GitHub GraphQL endpoint", default="https://api.github.com/graphql")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    async with aiohttp.ClientSession(trust_env=True) as session:
        discussion_data = await fetch_discussion_data(session, args.api, args.token, args.owner, args.repo, args.discussion_number)
        print(json.dumps(discussion_data, default=lambda x: x.__dict__, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
