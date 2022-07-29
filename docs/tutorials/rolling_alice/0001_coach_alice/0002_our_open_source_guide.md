# Volume 1: Chapter 2: Our Open Source Guide

Alice will be acting as our proactive open source guide to
2nd and 3rd party plugin maintainers and contributors.
She will attempt to contribute helpful community files
so as to provide value as soon as possible to the community.

This tutorial is how we extend the `alice please contribute recommended community standards`
command from https://github.com/intel/dffml/tree/alice/entities/alice#recommend-community-standards

We want to be able to ask Alice to contribute a new kind of
[recommended community standard](https://opensource.guide/) to our projects.

We're going to extend the existing
[`alice please contribute recommended community standards`](https://github.com/intel/dffml/tree/alice/entities/alice#recommend-community-standards)
functionality to provide a `CODE_OF_CONDUCT.md` file to a repo if it doesn't
have one already.

This tutorial is covered in
[Rolling Alice: 2022 Progress Reports: July Activities Recap](https://www.youtube.com/watch?v=JDh2DARl8os&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=2)

## Setup

We need to get setup for contribing to Alice first
see https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
for more details.

```console
$ git clone -b alice https://github.com/intel/dffml dffml
$ cd dffml/entities/alice
$ python -m venv .venv
$ . .venv/bin/activate
$ python -m pip install -U pip setuptools wheel
$ python -m pip install \
    -e .[dev] \
    -e ../../ \
    -e ../../examples/shouldi/ \
    -e ../../feature/git/ \
    -e ../../operations/innersource/ \
    -e ../../configloader/yaml/
```

Then we create a repo which Alice will be contributing to and give it
some contents.

```console
$ gh repo create -y --private https://github.com/$USER/my-new-python-project
$ git clone https://github.com/$USER/my-new-python-project
$ cd my-new-python-project
$ echo 'print("Hello World")' > test.py
$ git add test.py
$ git commit -sam 'Initial Commit'
$ git push --set-upstream origin $(git branch -r | sed -e 's/.*\///')
$ cd ..
$ rm -rf my-new-python-project
```

## How to help Alice contribute more files

This tutorial will help you create a new Open Architecture / Alice
overlay which runs when another flow runs. The upstream flow
in this case is the `AlicePleaseContributeRecommendedCommunityStandards`
base flow.

Copy readme overlay to new file

```console
$ cp alice/please/contribute/recommended_community_standards/readme.py alice/please/contribute/recommended_community_standards/code_of_conduct.py
```

Rename types, classes, variables, etc.

```console
$ sed -e 's/Readme/CodeOfConduct/g' -e 's/README/CODE_OF_CONDUCT/g' -e 's/readme/code_of_conduct/g' -i alice/please/contribute/recommended_community_standards/code_of_conduct.py
```

Add `OverlayCONTRIBUTING` to the list of overlays to be applied to the
`dffml.overlays.alice.please.contribute.recommended_community_standard`
base flow.

```console
$ sed -i 's/OverlayREADME .*/&\nOverlayCODE_OF_CONDUCT                         = alice.please.contribute.recommended_community_standards.code_of_conduct:OverlayCODE_OF_CONDUCT/' entry_points.txt
```

The output of `git diff` should look similar to the following

**entry_points.txt**

```diff
diff --git a/entities/alice/entry_points.txt b/entities/alice/entry_points.txt
index b764491..c9bd781 100644
--- a/entities/alice/entry_points.txt
+++ b/entities/alice/entry_points.txt
@@ -9,6 +9,7 @@ CLI                                            = alice.please.contribute.recomme
 OverlayGit                                     = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGit
 OverlayGitHub                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGitHub
 OverlayREADME                                  = alice.please.contribute.recommended_community_standards.readme:OverlayREADME
+OverlayCODE_OF_CONDUCT                         = alice.please.contribute.recommended_community_standards.code_of_conduct:OverlayCODE_OF_CONDUCT
 OverlayCONTRIBUTING                            = alice.please.contribute.recommended_community_standards.contributing:OverlayCONTRIBUTING

 [dffml.overlays.alice.please.contribute.recommended_community_standards.readme]
```

Add the following section to the end of ``entry_points.txt`` to enable the
`OverlayGit` and `OverlayGitHub` overlays on our new code of conduct overlay
flow as well.

**entry_points.txt**

```ini
[dffml.overlays.alice.please.contribute.recommended_community_standards.code_of_conduct]
OverlayGit                                     = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGit
OverlayGitHub                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGitHub
```

Reinstall for new entrypoints to take effect

```console
$ python -m pip install -e .
```

Re-run the command to contribute a `CODE_OF_CONDUCT.md` file as well.

```console
$ alice please contribute -log debug -repos https://github.com/$USER/my-new-python-project -- recommended community standards
```

Check the PRs to confirm they were created

```console
$ gh -R https://github.com/$USER/my-new-python-project pr list
343     Recommended Community Standard: README  alice-contribute-recommended-community-standards-readme OPEN
341     Recommended Community Standard: CONTRIBUTING    alice-contribute-recommended-community-standards-contributing   OPEN
339     Recommended Community Standard: CODE_OF_CONDUCT alice-contribute-recommended-community-standards-code_of_conduct        OPEN
```

![Screenshot showing pull request for adding README.md and CONTRIBUTING.md files](https://user-images.githubusercontent.com/5950433/181826046-53ae3ef5-6750-48ad-afd2-8cf9174e0b63.png)

You can now edit the code in
``alice/please/contribute/recommended_community_standards/code_of_conduct.py``.

For tutorials which will help you extend further see the "Data Flow Programming"
section of the Alice CONTRIBUTING docs.
https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst#data-flow-programming

## Debugging

To close all PRs on a repo run the following

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

## Misc. Notes

- References:
  - https://github.com/intel/dffml/community/code-of-conduct/new?template=contributor-covenant
  - https://github.com/intel/dffml/community
    - List of files / must haves
  - https://opensource.guide/
  - https://github.com/intel/dffml/issues/1393
    - https://github.com/intel/dffml/discussions/1369#discussioncomment-2959986
