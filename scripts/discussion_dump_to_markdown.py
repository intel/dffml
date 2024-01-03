"""
Page scraping (to be used later to fixup internal cross references off anchor
IDs).

- First back up without edits here: b5e26e9b81b58ffe9a2dc9b39c76c1ed06cc8d20

.. code-block:: console

    $ curl 'https://github.com/intel/dffml/discussions/1369/comments/2603280/threads?back_page=1&forward_page=0&anchor_id=2813540' | tee /tmp/a
    $ curl 'https://github.com/intel/dffml/discussions/1369/comments/2603280/threads?back_page=1&forward_page=0&anchor_id=0' | tee /tmp/a.0
    $ diff -u /tmp/a /tmp/a.0
    $ grep 2813540 /tmp/b | grep -v '2813540&quot' | grep 2813540
    $ curl 'https://github.com/intel/dffml/discussions/1369' | tee /tmp/b
    $ grep '<input type="hidden" name="anchor_id"' /tmp/b

**intial_discussion_query.graphql**

.. code-block:: graphql

    fragment comment on DiscussionComment {
      body
      createdAt
      userContentEdits(first: 50) {
        pageInfo {
          endCursor
          hasNextPage
        }
        totalCount
        nodes {
          diff
          editedAt
        }
      }
    }
    query ($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        pinnedDiscussions(first: 1) {
          nodes {
            discussion {
              title
              body
              category {
                name
              }
              comments(first: 90) {
                pageInfo {
                  endCursor
                  hasNextPage
                }
                totalCount
                nodes {
                  ...comment
                  replies(first: 100) {
                    pageInfo {
                      endCursor
                      hasNextPage
                    }
                    totalCount
                    nodes {
                      ...comment
                    }
                  }
                }
              }
            }
          }
        }
      }
    }

.. code-block:: console

    $ gh api graphql -F owner='intel' -F repo='dffml' -F query=@intial_discussion_query.graphql | tee output.json | python -m json.tool | tee output.json.formated.json

Confirm we got everything, otherwise, write pagination code (there should be some in github operations somewhere).

.. code-block:: console

    $ grep '"hasNextPage": false' < output.json.formated.json | wc -l
    279

The following command returns no results if we got everything and don't need to paginate.

.. code-block:: console

    $ grep '"hasNextPage": true' < output.json.formated.json

As is before this comment update

.. code-block:: console

    $ python3 -u dump_discussion.py | wc
       2566   42911  285694

After removing the first chapter of Alice's Adventures in Wonderland:

.. code-block:: console

    $ python3 -u dump_discussion.py | wc
       2499   40571  273084
"""
import os
import sys
import json
import asyncio
import pathlib
import tempfile
from typing import Callable, Type, Union, NewType, Dict

sys.path.append(str(pathlib.Path(__file__).parent.resolve()))

from dump_discussion import Reply, Comment, Discussion


def title_to_filename(title_link_line: str):
    title = title_link_line[2:]
    if "[" in title_link_line:
        title = title_link_line[3:]
        title = title[: title.index("]")]
    return title.upper().replace(":", "").replace(" ", "_").replace("-", "_")


def current_volume(text):
    if ": Volume" in text.split("\n")[0]:
        return text.split(": Volume")[1].split(":")[0]


def output_markdown(discussion: Dict, output_directory: pathlib.Path):
    # Create the filename for the top level file
    filename = title_to_filename(discussion.body.split("\n")[0])
    prefix = ["docs", "discussions", "alice_engineering_comms"]
    # prefix = ["docs", "tutorials", "alice"]
    text = discussion.body
    text = text.replace("\r", "")
    # path.write_text(text)
    # volume = current_volume(text)
    path = output_directory.joinpath(
        *[*prefix, "index.md"],
    )
    print(path, repr(text[:100] + "..."))
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)
    path.write_text(text)
    for i, comment in enumerate(discussion.comments):
        # Create the filename which will be joined by underscores
        filename_parts = prefix + [f"{i:04}"]
        # Output a file for the comment
        path = output_directory.joinpath(*filename_parts, "index.md")
        text = comment.body
        text = text.replace("\r", "")
        print(path, repr(text[:100] + "..."))
        if not path.parent.is_dir():
            path.parent.mkdir(parents=True)
        path.write_text(text)
        replys = []
        # Output a file for the reply
        for j, reply in enumerate(comment.replies):
            path = output_directory.joinpath(
                *[*filename_parts, "_".join(["reply", f"{j:04}"]) + ".md"],
            )
            text = reply.body
            text = text.replace("\r", "")
            replys += text
            print(path, repr(text[:100] + "..."))
            if not path.parent.is_dir():
                path.parent.mkdir(parents=True)
            path.write_text(text)


async def main():
    input_data = json.load(sys.stdin)
    discussion = Discussion(
        title=input_data["title"], body=input_data["body"], comments=[]
    )
    for comment in input_data["comments"]:
        discussion.comments.append(
            Comment(
                body=comment["body"],
                replies=[],
            )
        )
        for reply in comment["replies"]:
            discussion.comments[-1].replies.append(Reply(body=reply["body"]))
    output_markdown(discussion, pathlib.Path(__file__).parents[1])
    # os.system(f"rm -rf 'docs/tutorials/alice/'")


if __name__ == "__main__":
    asyncio.run(main())
