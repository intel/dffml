## 2022-08-31 @pdxjohnny Engineering Logs

- Game plan
  - [ ] `alice please contribute`
    - [x] README
    - [x] CONTRIBUTING
    - [x] CODE_OF_CONDUCT
      - https://www.youtube.com/watch?v=u2lGjMMIlAo&list=PLtzAOVTpO2ja6DXSCzoF3v_mQDh7l0ymH
      - https://github.com/intel/dffml/commit/6c1719f9ec779a9d64bfb3b364e2c41c5ac9aab7
    - [ ] SECURITY
    - [ ] SUPPORT
    - [ ] CITATION.cff
      - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files
      - auto populate with 000 UUIDs
    - [ ] CODEOWNERS
      - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
  - [ ] Demo on stream of how write install and publish a third party overlay
    - Have the overlay be a function which outputs a return type of `ContributingContents` and takes the name of the project given in a `CITATIONS.cff` file as another our open source guide example.
    - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files
    - https://github.com/johnlwhiteman/living-threat-models/blob/c027d4e319c715adce104b95f1e88623e02b0949/CITATION.cff
    - https://www.youtube.com/watch?v=TMlC_iAK3Rg&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&index=5&t=2303
    - https://github.com/intel/dffml/blob/9aeb7f19e541e66fc945c931801215560a8206d7/entities/alice/alice/please/contribute/recommended_community_standards/contributing.py#L48-L54
  - [ ] Demo on stream how to write install and contribute a 1st/2nd party overlay, the same code just not third party, from start to finish.
    - CITATION.cff
  - [ ] `alice shouldi contribute`
    - [ ] Support caching / import / export dataflows
    - [ ] Support query in easy way (graphql)
    - [ ] Support joining with previous runs / more sets of data
  - [ ] Contribute the data OpenSSF cares about to their DB via applicable joins and queries
     - [ ] Email Christine and CRob
- TODO
  - [ ] Organization
    - [ ] Daily addition by Alice to engineering log following template
      - [ ] Addition of old TODOs yesterday's logs
  - [ ] Export end state of input network / dump everything used by orchestrator
    - [ ] pickle
    - [ ] JSON
  - [ ] Ensure import works (check for state reset in `__aenter__()`, we probably need a generic wrapper to save the memory ones which populates after the `__aenter__()` of the wrapped object.
  - [ ] GraphQl query of cached state using strawberry library or something like that
  - [ ] Example docs for how to run a flow, then merge with static data as the start state for the cache and then query the whole bit with graphql
- TODO
  - [x] Splice out Code of Conduct contribution demo from July progress report video
  - [x] Add PR and reference PR as example in tutorial along with spliced out `alice please contribute recommended community standards` contribution demo clip
  - [ ] How to Publish an Alice Overlay
  - [ ] How to Contribute an Alice Overlay
  - [ ] Rolling Alice: 2022 Progress Reports: August Activities Recap

---

### How to Publish an Alice Overlay

- Metadata
  - Date: 2022-08-30 10:00 UTC -7
- Docs we are following
  - https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
  - https://github.com/intel/dffml/tree/alice/entities/alice#recommend-community-standards
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0002_our_open_source_guide.md

### How to Contribute an Alice Overlay

- Metadata
  - Date: 2022-08-30 10:00 UTC -7

### Rolling Alice: 2022 Progress Reports: August Activities Recap

- Metadata
  - Date: 2022-08-30 10:00 UTC -7

---

- Failed attempt to get class defined variables with op decorated functions defined in dataflow classes
  - Can't inspect class currently being defined. Can't find the `NewType` references

```diff
diff --git a/dffml/df/base.py b/dffml/df/base.py
index 4f84c1c7c8..df83d7b612 100644
--- a/dffml/df/base.py
+++ b/dffml/df/base.py
@@ -345,7 +345,30 @@ def op(

         forward_refs_from_cls = None
         if hasattr(func, "__qualname__") and "." in func.__qualname__:
+
+            def stack_feedface(max_depth=4):
+                from pprint import pprint
+                # Grab stack frames
+                frames = inspect.stack()
+                for i, frame_info in enumerate(frames):
+                    pprint(frame_info)
+                    breakpoint()
+                    continue
+                    if max_depth != -1 and i >= max_depth:
+                        break
+                    if (
+                        frame_info.function == method_name
+                        and "self" in frame_info.frame.f_locals
+                        and frame_info.frame.f_locals["self"] is obj
+                    ):
+                        return True
+                return False
+
             # Attempt to lookup type definitions defined within class
+            if func.__qualname__.split(".")[0] == "OverlayCODEOWNERS":
+                stack_feedface()
+                breakpoint()
+
             forward_refs_from_cls = getattr(
                 sys.modules[func.__module__],
                 func.__qualname__.split(".")[0],
```