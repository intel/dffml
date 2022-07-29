# Volume 1: Chapter 2: Our Open Source Guide

> Alice will be acting as our proactive open source guide to
> 2nd and 3rd party plugin maintainers and contributors.
> She will attempt to contribute helpful community files
> so as to provide value as soon as possible to the community.

References:

- https://github.com/intel/dffml/community/code-of-conduct/new?template=contributor-covenant
- https://github.com/intel/dffml/community
  - List of files / must haves
- https://opensource.guide/
- https://github.com/intel/dffml/issues/1393
  - https://github.com/intel/dffml/discussions/1369#discussioncomment-2959986

Install Alice https://github.com/intel/dffml/tree/alice/entities/alice

We want to be able to ask Alice to contribute [recommended community standards](https://opensource.guide/) to our projects.

## Setup

First let's create a repo to work with

```console
$ gh repo create -y --private https://github.com/$USER/my-new-python-project
$ git clone https://github.com/$USER/my-new-python-project
$ cd my-new-python-project
$ echo 'print("Hello World")' > test.py
$ git add test.py
$ git commit -sam 'Initial Commit'
$ git push --set-upstream origin main
```

## How to help Alice contribute more files


This tutorial will help you create a new Open Architecture / Alice
overlay which runs when another flow runs. The upstream flow
in this case is the `AlicePleaseContributeRecommendedCommunityStandards`
base flow.

Copy readme overlay to new file

```console
$ cp alice/please/contribute/recommended_community_standards/readme.py alice/please/contribute/recommended_community_standards/contribute.py
```

Rename types, classes, variables, etc.

```console
$ sed -e 's/Readme/Contributing/g' -e 's/README/CONTRIBUTING/g' -e 's/readme/contributing/g' -i alice/please/contribute/recommended_community_standards/contribute.py
```

Add `OverlayCONTRIBUTING` to the list of overlays to be applied to the
`dffml.overlays.alice.please.contribute.recommended_community_standard`
base flow.

**dffml.git/entites/alice/entry_points.txt**

```diff
diff --git a/entities/alice/entry_points.txt b/entities/alice/entry_points.txt
index 129b2866a1..9e130cb3b2 100644
--- a/entities/alice/entry_points.txt
+++ b/entities/alice/entry_points.txt
@@ -9,6 +9,7 @@ CLI                                            = alice.please.contribute.recomme
 OverlayGit                                     = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGit
 OverlayGitHub                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGitHub
 OverlayREADME                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayREADME
+OverlayCONTRIBUTING                            = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayCONTRIBUTING
 # OverlayMetaIssue                               = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayMetaIssue

 [dffml.overlays.alice.please.contribute.recommended_community_standards.overlay.readme]
```

Add the `OverlayGit` and `OverlayGitHub` overlays to the new overlay as well.

**dffml.git/entites/alice/entry_points.txt**

```ini
[dffml.overlays.alice.please.contribute.recommended_community_standards.overlay.contributing]
OverlayGit                                     = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGit
OverlayGitHub                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGitHu
```

Reinstall for new entrypoints to take effect

```console
$ python -m pip install -e .
```

- Re-run the command and observe results

```console
$ alice please contribute -log debug -repos https://github.com/$USER/my-new-python-project -- recommended community standards
```

```console
$ gh -R https://github.com/$USER/my-new-python-project pr list
297     Recommended Community Standard: README  alice-contribute-recommended-community-standards-readme OPEN
295     Recommended Community Standard: CONTRIBUTING    alice-contribute-recommended-community-standards-contributing   OPEN
```

![Screenshot showing pull request for adding README.md and CONTRIBUTING.md files](https://user-images.githubusercontent.com/5950433/181796646-0b49335c-7739-4dff-bce4-bab98a8fc560.png)

## Debugging

```console
$ for pr in $(gh -R https://github.com/$USER/my-new-python-project pr list --json number --jq '.[].number'); do gh -R https://github.com/$USER/my-new-python-project pr close "${pr}"; done;
```

## Future Work

This section is TODO but long term probably

- Future work
  - `-repos https://github.com/intel/dffml`
    - Infer from context (cwd)

### Meta Issue

Disabled for now

What the body of the issue should be

```
- [] [README](https://github.com/intel/dffml/blob/main/README.md)
- [] Code of conduct
- [] [Contributing](https://github.com/intel/dffml/blob/main/CONTRIBUTING.md)
- [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
```

We will also add now (and later `THREATS.md`)

```
- [] Security
```

We will omit for now

```
- [] Issue templates
- [] Pull request template
- [] Repository admins accept content reports
```
