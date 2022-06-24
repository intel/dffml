# Volume 1: Chapter 2: Alice Our Open Source Guide

> Alice will be acting as our proactive open source guide to
> 2nd and 3rd party plugin maintainers and contributors.
> She will attempt to contribute helpful community files
> so as to provide value as soon as possible to the community.

References:

- https://github.com/intel/dffml/community/code-of-conduct/new?template=contributor-covenant
- https://github.com/intel/dffml/community
  - List of files / must haves
- https://opensource.guide/
- https://github.com/intel/dffml/discussions/1369#discussioncomment-2959986

We want to be able to ask Alice to contribute [recommended community standards](https://opensource.guide/) to our projects.

```console
$ alice please contribute -repos https://github.com/intel/dffml "recommended community standards"
```


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
- []  Issue templates
- []  Pull request template
- []  Repository admins accept content reports
```

```console
$ alice please contribute "recommended community standards"
```

Show it working with gh pr list

- Future work
  - `-repos https://github.com/intel/dffml`
    - Infer from context (cwd)