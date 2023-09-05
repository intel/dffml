- https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads#push
- https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#push

```console
$ git log -n 2
commit b6f9725a5eaa1696904a6b07ded61a27ba5e5b29 (HEAD -> alice, upstream/alice)
Author: john-s-andersen <john.s.andersen@intel.com>
Date:   Wed Oct 12 18:00:57 2022 +0000

    util: df: internal: Fix for Python 3.9.13 hasattr not detecting NewType.__supertype__ in generator

    Signed-off-by: john-s-andersen <john.s.andersen@intel.com>

commit fb5d646e7099f62cb5c34b936d19c1af30c055a7
Author: John Andersen <johnandersenpdx@gmail.com>
Date:   Tue Oct 11 17:56:59 2022 -0700

    docs: tutorials: rolling alice: forward: Add link to John^2 Living Threat Models Are Better Than Dead Threat Models talk
$ gh api https://api.github.com/repos/intel/dffml/compare/fb5d646e7099f62cb5c34b936d19c1af30c055a7...b6f9725a5eaa1696904a6b07ded61a27ba5e5b29 | jq -r '.files[].filename'
dffml/util/df/internal.py
```

- Clipped API output

```json
{
  "files": [
    {
      "sha": "55960cf9ea7036a0fcfd68d7799ff1567a876158",
      "filename": "dffml/util/df/internal.py",
      "status": "modified",
      "additions": 4,
      "deletions": 1,
      "changes": 5,
      "blob_url": "https://github.com/intel/dffml/blob/b6f9725a5eaa1696904a6b07ded61a27ba5e5b29/dffml%2Futil%2Fdf%2Finternal.py",
      "raw_url": "https://github.com/intel/dffml/raw/b6f9725a5eaa1696904a6b07ded61a27ba5e5b29/dffml%2Futil%2Fdf%2Finternal.py",
      "contents_url": "https://api.github.com/repos/intel/dffml/contents/dffml%2Futil%2Fdf%2Finternal.py?ref=b6f9725a5eaa1696904a6b07ded61a27ba5e5b29",
      "patch": "@@ -24,6 +24,9 @@ def object_to_operations(obj, module=None):\n             obj,\n             predicate=lambda i: inspect.ismethod(i)\n             or inspect.isfunction(i)\n-            and not hasattr(i, \"__supertype__\"),\n+            and not hasattr(i, \"__supertype__\")\n+            # NOTE HACK
 Fails in 3.9.13 to remove\n+            # NewType without the check in the str repr.\n+            and \" NewType \" not in str(i),\n         )\n     ]"
    }
  ]
}
```

```python
import os
import json
import pathlib
import urllib.request

owner, repository = os.environ["OWNER_REPOSITORY"].split("/", maxsplit=1)

with urllib.request.urlopen(
    urllib.request.Request(
        os.environ["COMPARE_URL"],
        headers={
            "Authorization": "bearer " + os.environ["GH_ACCESS_TOKEN"],
        },
    )
) as response:
    response_json = json.load(response)

# Build the most recent commit
commit = response_json["commits"][-1]["sha"]

manifest = list([
    {
        "image_name": pathlib.Path(compare_file["filename"]).stem,
        "dockerfile": compare_file["filename"],
        "owner": owner,
        "repository": repository,
        "branch": os.environ["BRANCH"],
        "commit": commit,
    }
    for compare_file in response_json["files"]
    if compare_file["filename"].startswith(os.environ["PREFIX"])
])

print(json.dumps(manifest, sort_keys=True, indent=4))
print("::set-output name=matrix::" + json.dumps({"include": manifest}))
```

```console
$ PREFIX=dffml GH_ACCESS_TOKEN=$(grep oauth_token < ~/.config/gh/hosts.yml | sed -e 's/    oauth_token: //g') BRANCH=main OWNER_REPOSITORY=intel/dffml COMPARE_URL=https://api.github.com/repos/intel/dffml/compare/a75bef07fd1279f1a36a601d4e652c2b97bfa1de...b6f9725a5eaa1696904a6b07ded61a27ba5e5b29 python test.py
[
    {
        "branch": "main",
        "commit": "b6f9725a5eaa1696904a6b07ded61a27ba5e5b29",
        "dockerfile": "dffml-base.Dockerfile",
        "image_name": "dffml-base",
        "owner": "intel",
        "repository": "dffml"
    }
]
::set-output name=matrix::{"include": [{"image_name": "dffml-base", "dockerfile": "dffml-base.Dockerfile", "owner": "intel", "repository": "dffml", "branch": "main", "commit": "b6f9725a5eaa1696904a6b07ded61a27ba5e5b29"}]}
```