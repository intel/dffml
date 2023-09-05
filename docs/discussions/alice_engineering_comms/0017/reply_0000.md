## 2022-09-02 @pdxjohnny Engineering Logs

- Game plan
  - [ ] `alice please contribute`
    - [x] README
    - [x] CONTRIBUTING
    - [x] CODE_OF_CONDUCT
      - https://www.youtube.com/watch?v=u2lGjMMIlAo&list=PLtzAOVTpO2ja6DXSCzoF3v_mQDh7l0ymH
      - https://github.com/intel/dffml/commit/6c1719f9ec779a9d64bfb3b364e2c41c5ac9aab7
    - [ ] SECURITY
    - [ ] SUPPORT
    - [ ] .gitignore
      - Dump files add common ignores, collect all inputs derived from file name and of type `GitIgnoreLine` using `group_by` in output flow
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
  - [ ] Sidestep failure to wrap with `@op` decorator on
    - [ ] `with dffml.raiseretry():` around `gh` grabbing issue title
      - Avoid potential resource not available yet after creation server side
    - [ ] `try: ... catch exception as error: raise RetryOperationException from error` in `run` (above `run_no_retry()`)
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

### Raise Retry from Exception for Problematic Operations

- Metadata
  - Date: 2022-09-02 11:20 UTC -7
- `with dffml.raiseretry():` around `gh` grabbing issue title
  - Avoid potential resource not available yet after creation server side
- `try: ... catch exception as error: raise RetryOperationException from error` in `run` (above `run_no_retry()`)

```diff
diff --git a/dffml/df/base.py b/dffml/df/base.py
index 4f84c1c7c..b2d23a678 100644
--- a/dffml/df/base.py
+++ b/dffml/df/base.py
@@ -15,11 +15,12 @@ from typing import (
     Union,
     Optional,
     Set,
+    ContextManager,
 )
 from dataclasses import dataclass, is_dataclass, replace
 from contextlib import asynccontextmanager
 
-from .exceptions import NotOpImp
+from .exceptions import NotOpImp, RetryOperationException
 from .types import (
     Operation,
     Input,
@@ -94,6 +95,7 @@ class OperationImplementationContext(BaseDataFlowObjectContext):
         self.parent = parent
         self.ctx = ctx
         self.octx = octx
+        self.op_retries = None
 
     @property
     def config(self):
@@ -102,6 +104,31 @@ class OperationImplementationContext(BaseDataFlowObjectContext):
         """
         return self.parent.config
 
+
+    @contextlib.contextmanager
+    def raiseretry(retries: int) -> ContextManager[None]:
+        """
+        Use this context manager to have the orchestrator call the operation's
+        ``run()`` method multiple times within the same
+        OperationImplementationContext entry.
+
+        Useful for
+
+        TODO
+
+        - Backoff
+
+        >>> def myop(self):
+        ...     with self.raiseretry(5):
+        ...         if self.op_current_retry < 4:
+        ...             raise Exception()
+        """
+        try:
+            yield
+        except Exception as error:
+            raise RetryOperationException(retries) from error
+
+
     @abc.abstractmethod
     async def run(self, inputs: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
         """
diff --git a/dffml/df/exceptions.py b/dffml/df/exceptions.py
index b1f3bcc87..e185cf22c 100644
--- a/dffml/df/exceptions.py
+++ b/dffml/df/exceptions.py
@@ -28,3 +28,8 @@ class ValidatorMissing(Exception):
 
 class MultipleAncestorsFoundError(NotImplementedError):
     pass
+
+
+class RetryOperationException(Exception):
+    def __init__(self, retires: int) -> None:
+        self.retires = retires
diff --git a/dffml/df/memory.py b/dffml/df/memory.py
index 59286d492..ca0a77cc6 100644
--- a/dffml/df/memory.py
+++ b/dffml/df/memory.py
@@ -26,6 +26,7 @@ from .exceptions import (
     DefinitionNotInContext,
     ValidatorMissing,
     MultipleAncestorsFoundError,
+    RetryOperationException,
 )
 from .types import (
     Input,
@@ -1187,6 +1188,7 @@ class MemoryOperationImplementationNetworkContext(
         ctx: BaseInputSetContext,
         octx: BaseOrchestratorContext,
         operation: Operation,
+        opctx: OperationImplementationContext,
         inputs: Dict[str, Any],
     ) -> Union[bool, Dict[str, Any]]:
         """
@@ -1195,9 +1197,7 @@ class MemoryOperationImplementationNetworkContext(
         # Check that our network contains the operation
         await self.ensure_contains(operation)
         # Create an opimp context and run the operation
-        async with self.operations[operation.instance_name](
-            ctx, octx
-        ) as opctx:
+        with contextlib.nullcontext():
             self.logger.debug("---")
             self.logger.debug(
                 "%s Stage: %s: %s",
@@ -1248,22 +1248,28 @@ class MemoryOperationImplementationNetworkContext(
         """
         Run an operation in our network.
         """
-        if not operation.retry:
-            return await self.run_no_retry(ctx, octx, operation, inputs)
-        for retry in range(0, operation.retry):
-            try:
-                return await self.run_no_retry(ctx, octx, operation, inputs)
-            except Exception:
-                # Raise if no more tries left
-                if (retry + 1) == operation.retry:
-                    raise
-                # Otherwise if there was an exception log it
-                self.logger.error(
-                    "%r: try %d: %s",
-                    operation.instance_name,
-                    retry + 1,
-                    traceback.format_exc().rstrip(),
-                )
+        async with self.operations[operation.instance_name](
+            ctx, octx
+        ) as opctx:
+            opctx.retries = operation.retry
+            for retry in range(0, operation.retry):
+                try:
+                    return await self.run_no_retry(ctx, octx, operation, opctx, inputs)
+                except Exception:
+                    if isinstance(error, RetryOperationException):
+                        retries = error.retries
+                    if not retries
+                        raise
+                    # Raise if no more tries left
+                    if (retry + 1) == retries:
+                        raise
+                    # Otherwise if there was an exception log it
+                    self.logger.error(
+                        "%r: try %d: %s",
+                        operation.instance_name,
+                        retry + 1,
+                        traceback.format_exc().rstrip(),
+                    )
 
     async def operation_completed(self):
         await self.completed_event.wait()
diff --git a/entities/alice/alice/please/contribute/recommended_community_standards/readme.py b/entities/alice/alice/please/contribute/recommended_community_standards/readme.py
index 437601358..836d8f175 100644
--- a/entities/alice/alice/please/contribute/recommended_community_standards/readme.py
+++ b/entities/alice/alice/please/contribute/recommended_community_standards/readme.py
@@ -183,10 +183,11 @@ class OverlayREADME:
         """
         Use the issue title as the pull request title
         """
-        async for event, result in dffml.run_command_events(
-            ["gh", "issue", "view", "--json", "title", "-q", ".title", readme_issue,],
-            logger=self.logger,
-            events=[dffml.Subprocess.STDOUT],
-        ):
-            if event is dffml.Subprocess.STDOUT:
-                return result.strip().decode()
+        with self.raiseretry(5):
+            async for event, result in dffml.run_command_events(
+                ["gh", "issue", "view", "--json", "title", "-q", ".title", readme_issue,],
+                logger=self.logger,
+                events=[dffml.Subprocess.STDOUT],
+            ):
+                if event is dffml.Subprocess.STDOUT:
+                    return result.strip().decode()
```