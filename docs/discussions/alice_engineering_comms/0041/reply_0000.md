## 2022-09-29 @pdxjohnny Engineering Logs

- SPIFFE
  - https://github.com/spiffe/spire/issues/1003
- rekor
  - https://github.com/sigstore/rekor/blob/main/docker-compose.yml
- Open Policy Agent
  - https://github.com/transmute-industries/did-eqt/blob/main/docs/did-eqt-opa-primer.md
- Great org README
  - https://github.com/transmute-industries
- Verifiable Data TypeScript Library
  - https://github.com/transmute-industries/verifiable-data
- Sidetree
  - https://identity.foundation/sidetree/spec/
  - > ![sidetree-arch](https://identity.foundation/sidetree/spec/diagrams/sidetree-system.svg)
    >
    > #### [DID State Patches](https://identity.foundation/sidetree/spec/#did-state-patches)
    > Sidetree defines a delta-based [Conflict-Free Replicated Data Type](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type) system, wherein the metadata in a Sidetree-based implementation is controlled by the cryptographic PKI material of individual entities in the system, represented by DIDs. While the most common form of state associated with the DIDs in a Sidetree-based implementation is a [DID Document](https://w3c.github.io/did-core/), Sidetree can be used to maintain any type of DID-associated state.
    >
    > Sidetree specifies a general format for patching the state associated with a DID, called Patch Actions, which define how to deterministic mutate a DID’s associated state. Sidetree further specifies a standard set of Patch Actions (below) implementers MAY use to facilitate DID state patching within their implementations. Support of the standard set of Patch Actions defined herein IS NOT required, but implementers MUST use the Patch Action format for defining patch mechanisms within their implementation. The general Patch Action format is defined as follows:
    > - `add-public-keys`
    > - `remove-public-keys`
    > - `add-services`
    > - `remove-services`
    > - `ietf-json-patch`
    >
    > #### [Proof of Fee](https://identity.foundation/sidetree/spec/#proof-of-fee)
    >
    > [NOTE](https://identity.foundation/sidetree/spec/#note-6) This section is non-normative
    >
    > Sidetree implementers MAY choose to implement protective mechanisms designed to strengthen a Sidetree network against low-cost spurious operations. These mechanisms are primarily designed for open, permissionless implementations utilizing public blockchains that feature native crypto-economic systems.
- GitHub Actions
  - https://docs.github.com/en/actions/using-jobs/running-jobs-in-a-container
  - https://docs.github.com/en/actions/using-containerized-services/about-service-containers
  - https://github.com/jenkinsci/custom-war-packager/issues/173
- Misc. diffs lying around

```diff
diff --git a/dffml/df/base.py b/dffml/df/base.py
index 4f84c1c7c..1303e41c4 100644
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
+    @asynccontextmanager
+    async def raiseretry(self, retries: int) -> ContextManager[None]:
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
index 3ec596d6c..06606a3f8 100644
--- a/dffml/df/exceptions.py
+++ b/dffml/df/exceptions.py
@@ -32,3 +32,8 @@ class ValidatorMissing(Exception):
 
 class MultipleAncestorsFoundError(NotImplementedError):
     pass
+
+
+class RetryOperationException(Exception):
+    def __init__(self, retires: int) -> None:
+        self.retires = retires
diff --git a/dffml/df/memory.py b/dffml/df/memory.py
index f6f15f5a0..740fc7614 100644
--- a/dffml/df/memory.py
+++ b/dffml/df/memory.py
@@ -27,6 +27,7 @@ from .exceptions import (
     ValidatorMissing,
     MultipleAncestorsFoundError,
     NoInputsWithDefinitionInContext,
+    RetryOperationException,
 )
 from .types import (
     Input,
@@ -39,6 +40,7 @@ from .types import (
 from .base import (
     OperationException,
     OperationImplementation,
+    OperationImplementationContext,
     FailedToLoadOperationImplementation,
     BaseDataFlowObject,
     BaseDataFlowObjectContext,
@@ -1190,6 +1192,7 @@ class MemoryOperationImplementationNetworkContext(
         ctx: BaseInputSetContext,
         octx: BaseOrchestratorContext,
         operation: Operation,
+        opctx: OperationImplementationContext,
         inputs: Dict[str, Any],
     ) -> Union[bool, Dict[str, Any]]:
         """
@@ -1198,9 +1201,7 @@ class MemoryOperationImplementationNetworkContext(
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
@@ -1251,22 +1252,28 @@ class MemoryOperationImplementationNetworkContext(
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
+                    if not retries:
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
diff --git a/source/mongodb/dffml_source_mongodb/source.py b/source/mongodb/dffml_source_mongodb/source.py
index 01621851e..656524d75 100644
--- a/source/mongodb/dffml_source_mongodb/source.py
+++ b/source/mongodb/dffml_source_mongodb/source.py
@@ -19,6 +19,7 @@ class MongoDBSourceConfig:
     collection: str = None
     tlsInsecure: bool = False
     log_collection_names: bool = False
+    bypass_document_validation: bool = False

     def __post_init__(self):
         uri = urllib.parse.urlparse(self.uri)
@@ -36,6 +37,7 @@ class MongoDBSourceContext(BaseSourceContext):
             {"_id": record.key},
             {"_id": record.key, **record.export()},
             upsert=True,
+            bypass_document_validation=self.parent.config.bypass_document_validation,
         )

     def document_to_record(self, document, key=None):
```