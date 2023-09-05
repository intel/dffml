## 2023-01-05 @pdxjohnny Engineering Logs

- TODO
  - [x] Simplify, ditch all but main package and Alice for now.
    - [ ] Re-enable plugins incrementally later
  - [ ] Fix failures in main package tests

### Fixing CI

- Rebased `main` into `alice`.
- https://github.com/pdxjohnny/dffml/actions/runs/3849393578/jobs/6558333925
- Updated version of `black` autoformatter due to issues with `click` dependency
  - The downside of using an autoformatter is sometimes it will change a bunch of stuff. So we'll probably end up with one big "autoformatted due to psf/black upgrade" commit, which probably would have needed to be done anyway.
- References
  - https://stackoverflow.com/questions/71673404/importerror-cannot-import-name-unicodefun-from-click

```
Ran 428 tests in 385.519s
FAILED (failures=6, errors=38, skipped=29)
```