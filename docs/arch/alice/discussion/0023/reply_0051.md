- Some work in progress: e25658017b46a550ff53e027e0d91b0957607f52
- https://azure.microsoft.com/en-us/overview/what-is-a-qubit/#introduction
  - > A qubit uses the quantum mechanical phenomena of superposition to achieve a linear combination of two states. A classical binary bit can only represent a single binary value, such as 0 or 1, meaning that it can only be in one of two possible states. A qubit, however, can represent a 0, a 1, or any proportion of 0 and 1 in superposition of both states, with a certain probability of being a 0 and a certain probability of being a 1.
- applied quantum computing train of thought
  - this qubit is perfect for the circle, the everything is one, the infinity between zero and on - elightnement: everything is one 
    - Therefore really does the quibit just represent the deviation from one? We are always hoping between system contexts. Is this some sort of where did we land? How aligned was the system context with what we we requested? Was the milstone met? Sometimes we care about partial credit, sometimes we don't is that the 0 or 1?
    - Alice, do you think you can achive this next state? Cross domain conceptual mapping (x/z = a/b where you have two unkown denomenators, you predict from x to z and then to b or from a to b and tehn to z or ..., whatever you have good models for. Alice encode these models into quibits, then use quantum computing simulation to predict your ability to do a system context transform from state A to state B within bounds of overlayed strategic principles)
- Working on backing up this doc...
   - Python files as operations with imports being themseleves inputs when viewed from the static analysis data which later tells us how we can reconstruct waht needs to be installed when we also pair with dynamic analysis and figure out how to swap packages via existing tooling (aka if we run a CI job with PIP_INDEX set to a mirror were we put our own versions of dependencies, see 2ndparty ADR, this came from that, then when the CI job runs pip install as it usually would it picks up the depenencies with no changes to the contents of the job)
   - `imp_enter` call dataflow to pip install discovered `import/from` modules
   - f25c2e4d05d2c909eb1781d6c51c66a6c1eeee86

```console
$ curl 'https://github.com/intel/dffml/discussions/1369/comments/2603280/threads?back_page=1&forward_page=0&anchor_id=2813540' | tee /tmp/a
$ curl 'https://github.com/intel/dffml/discussions/1369/comments/2603280/threads?back_page=1&forward_page=0&anchor_id=0' | tee /tmp/a.0
$ diff -u /tmp/a /tmp/a.0
$ grep 2813540 /tmp/b | grep -v '2813540&quot' | grep 2813540
$ curl 'https://github.com/intel/dffml/discussions/1369' | tee /tmp/b
$ grep '<input type="hidden" name="anchor_id"' /tmp/b
```

- https://github.com/cli/cli/issues/5659#issuecomment-1138588268
- https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions#discussioncomment
  - We define fragments which are saying what we want from a given type. Like a select.
- `Edge` suffix in GitHub docs looks like an `Input` item.
  - https://docs.github.com/en/graphql/reference/objects#usercontenteditedge

**intial_discussion_query.graphql**

```graphql
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
```

```console
$ gh api graphql -F owner='intel' -F repo='dffml' -F query=@intial_discussion_query.graphql | tee output.json | python -m json.tool | tee output.json.formated.json
```

Confirm we got everything, otherwise, write pagination code (there should be some in github operations somewhere).

```console
$ grep '"hasNextPage": false' < output.json.formated.json | wc -l
279
```

The following command returns no results if we got everything and don't need to paginate.

```console
$ grep '"hasNextPage": true' < output.json.formated.json
```

**dump_discussion.py**

```python
import os
import json
import pathlib
import tempfile


INPUT = json.loads(pathlib.Path("output.json.formated.json").read_text())


def title_to_filename(title_link_line: str):
    title = title_link_line[2:]
    if "[" in title_link_line:
        title = title_link_line[3:]
        title = title[: title.index("]")]
    return title.upper().replace(":", "").replace(" ", "_").replace("-", "_")


def output_markdown(
    graphql_query_output: dict, output_directory: pathlib.Path
):
    # Loop through all the pinned discussions
    for discussion_node in graphql_query_output["data"]["repository"][
        "pinnedDiscussions"
    ]["nodes"]:
        # Create the filename for the top level file
        filename = title_to_filename(
            discussion_node["discussion"]["body"].split("\n")[0]
        )
        output_directory.joinpath(
            "_".join(["ROLLING", "ALICE", f"{0:04}"]) + ".md"
        ).write_text(discussion_node["discussion"]["body"],)
        for i, comment_node in enumerate(
            discussion_node["discussion"]["comments"]["nodes"], start=1
        ):
            # Create the filename which will be joined by underscores
            filename_parts = ["ROLLING", "ALICE", f"{i:04}"]
            if comment_node["body"].split()[:1] == ["#"]:
                # If we are in a chapter. Create a directory
                filename_parts += [
                    title_to_filename(comment_node["body"].split("\n")[0])
                ]
            # Output a file for the comment
            output_directory.joinpath(
                "_".join(filename_parts) + ".md"
            ).write_text(comment_node["body"],)
            # Output a file for the reply
            for j, reply_node in enumerate(comment_node["replies"]["nodes"]):
                output_directory.joinpath(
                    "_".join(filename_parts + ["REPLY", f"{j:04}"]) + ".md"
                ).write_text(reply_node["body"],)


with tempfile.TemporaryDirectory() as tempdir:
    output_markdown(INPUT, pathlib.Path(tempdir))
    os.system(f"tree {tempdir}")
```

As is before this comment update

```console
$ python3 -u dump_discussion.py | wc
   2566   42911  285694
```

After removing the first chapter of Alice's Adventures in Wonderland:

```console
$ python3 -u dump_discussion.py | wc
   2499   40571  273084
```

- Backed up without edits here: b5e26e9b81b58ffe9a2dc9b39c76c1ed06cc8d20
- [`scripts/dump_discussion.py`](https://github.com/intel/dffml/blob/alice/scripts/dump_discussion.py)
