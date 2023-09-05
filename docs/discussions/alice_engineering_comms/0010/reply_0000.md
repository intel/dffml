## 2022-07-29 @pdxjohnny Engineering Logs

- AppSec PNW 2022 Talk playlist: https://youtube.com/playlist?list=PLfoJYLR9vr_IAd1vYWdKCOO4YYpGFVv99
  - John^2: Living Threat Models are Better Than Dead Threat Models
    - Not yet uploaded but has Alice's first live demo
- https://towardsdatascience.com/installing-multiple-alternative-versions-of-python-on-ubuntu-20-04-237be5177474
  - `$ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 40`
- References
  - https://tenor.com/search/alice-gifs
  - https://tenor.com/view/why-thank-you-thanks-bow-thank-you-alice-in-wonderland-gif-3553903
    - Alice curtsy
  - https://tenor.com/view/alice-in-wonderland-gif-26127117
    - Alice blows out unbirthday cake candle

```console
$ alice; sleep 3; gif-for-cli -l 0 --rows $(tput lines) --cols $(tput cols) 3553903
```

```console
$ gif-for-cli --rows `tput lines` --cols `tput cols` --export=alice-search-alices-adventures-in-wonderland-1.gif "Alice curtsy"
(why-thank-you-thanks-bow-thank-you-alice-in-wonderland-gif-3553903)
$ gif-for-cli --rows `tput lines` --cols `tput cols` --export=ascii-gif-alice-unbirthday-blow-out-candles-0.gif 26127117
$ gif-for-cli --rows `tput lines` --cols `tput cols` ascii-gif-alice-unbirthday-blow-out-candles-0.gif
$ echo gif-for-cli --rows `tput lines` --cols `tput cols`
gif-for-cli --rows 97 --cols 320
$ gif-for-cli -l 0 --rows `tput lines` --cols `tput cols` /mnt/c/Users/Johnny/Downloads/ascii-alices-adventures-in-wonderland-1.gif`
```

### Exploring a Helper Around Run DataFlow run_custom

- Realized we already have the lock because it's on `git_repository` at `flow_depth=1`

```diff
diff --git a/dffml/df/base.py b/dffml/df/base.py
index 4f84c1c7c8..2da0512602 100644
--- a/dffml/df/base.py
+++ b/dffml/df/base.py
@@ -404,14 +404,19 @@ def op(
                     )
 
                 definition_name = ".".join(name_list)
+                print("FEEDFACE", name, definition_name)
                 if hasattr(param_annotation, "__supertype__") and hasattr(
                     param_annotation, "__name__"
                 ):
+                    if "repo" in definition_name:
+                        breakpoint()
                     definition_name = param_annotation.__name__
+                    print("FEEDFACE", name, definition_name)
                 if inspect.isclass(param_annotation) and hasattr(
                     param_annotation, "__qualname__"
                 ):
                     definition_name = param_annotation.__qualname__
+                    print("FEEDFACE", name, definition_name)
 
                 if isinstance(param_annotation, Definition):
                     kwargs["inputs"][name] = param_annotation
diff --git a/dffml/df/types.py b/dffml/df/types.py
index f09a8a3cea..54840f58c0 100644
--- a/dffml/df/types.py
+++ b/dffml/df/types.py
@@ -44,6 +44,7 @@ APPLY_INSTALLED_OVERLAYS = _APPLY_INSTALLED_OVERLAYS()
 
 
 Expand = Union
+LockReadWrite = Union
 
 
 primitive_types = (int, float, str, bool, dict, list, bytes)
@@ -65,7 +66,7 @@ def find_primitive(new_type: Type) -> Type:
     )
 
 
-def new_type_to_defininition(new_type: Type) -> Type:
+def new_type_to_defininition(new_type: Type, lock: bool = False) -> Type:
     """
     >>> from typing import NewType
     >>> from dffml import new_type_to_defininition
@@ -77,6 +78,7 @@ def new_type_to_defininition(new_type: Type) -> Type:
     return Definition(
         name=new_type.__name__,
         primitive=find_primitive(new_type).__qualname__,
+        lock=lock,
         links=(
             create_definition(
                 find_primitive(new_type).__qualname__, new_type.__supertype__
@@ -95,7 +97,28 @@ class CouldNotDeterminePrimitive(Exception):
     """
 
 
-def resolve_if_forward_ref(param_annotation, forward_refs_from_cls):
+DEFAULT_DEFINTION_ANNOTATIONS_HANDLERS = {
+    LockReadWrite: lambda definition: setattr(definition, "lock", True),
+}
+
+
+def resolve_if_forward_ref(
+    param_annotation,
+    forward_refs_from_cls,
+    *,
+    defintion_annotations_handlers=None,
+) -> Tuple[Union["Definition", Any], bool]:
+    """
+    Return values:
+
+        param_or_definition: Union[Definition, Any]
+        lock: bool
+
+            If the definition should be locked or not.
+    """
+    if defintion_annotations_handlers is None:
+        defintion_annotations_handlers = DEFAULT_DEFINTION_ANNOTATIONS_HANDLERS
+    annotations = {}
     if isinstance(param_annotation, ForwardRef):
         param_annotation = param_annotation.__forward_arg__
     if (
@@ -104,11 +127,22 @@ def resolve_if_forward_ref(param_annotation, forward_refs_from_cls):
         and hasattr(forward_refs_from_cls, param_annotation)
     ):
         param_annotation = getattr(forward_refs_from_cls, param_annotation)
+        # Check if are in an annotation
+        param_annotation_origin = get_origin(param_annotation)
+        if param_annotation_origin in defintion_annotations_handlers:
+            annotations[
+                param_annotation_origin
+            ] = defintion_annotations_handlers[param_annotation_origin]
+            param_annotation = list(get_args(param_annotation))[0]
+        # Create definition
         if hasattr(param_annotation, "__name__") and hasattr(
             param_annotation, "__supertype__"
         ):
             # typing.NewType support
-            return new_type_to_defininition(param_annotation)
+            definition = new_type_to_defininition(param_annotation)
+            for handler in annotations.values():
+                handler(definition)
+            return definition
     return param_annotation
 
 
@@ -118,6 +152,7 @@ def _create_definition(
     default=NO_DEFAULT,
     *,
     forward_refs_from_cls: Optional[object] = None,
+    lock: bool = False,
 ):
     param_annotation = resolve_if_forward_ref(
         param_annotation, forward_refs_from_cls
@@ -138,12 +173,14 @@ def _create_definition(
     elif get_origin(param_annotation) in [
         Union,
         collections.abc.AsyncIterator,
+        LockReadWrite,
     ]:
         # If the annotation is of the form Optional
         return create_definition(
             name,
             list(get_args(param_annotation))[0],
             forward_refs_from_cls=forward_refs_from_cls,
+            lock=bool(get_origin(param_annotation) in (LockReadWrite,),),
         )
     elif (
         get_origin(param_annotation) is list
@@ -235,6 +272,7 @@ def create_definition(
     default=NO_DEFAULT,
     *,
     forward_refs_from_cls: Optional[object] = None,
+    lock: bool = False,
 ):
     if hasattr(param_annotation, "__name__") and hasattr(
         param_annotation, "__supertype__"
@@ -246,6 +284,7 @@ def create_definition(
         param_annotation,
         default=default,
         forward_refs_from_cls=forward_refs_from_cls,
+        lock=lock,
     )
     # We can guess name if converting from NewType. However, we can't otherwise.
     if not definition.name:
@@ -847,7 +886,9 @@ class DataFlow:
         for operation in args:
             name = getattr(getattr(operation, "op", operation), "name")
             if name in operations:
-                raise ValueError(f"Operation {name} given as positional and in dict")
+                raise ValueError(
+                    f"Operation {name} given as positional and in dict"
+                )
             operations[name] = operation
 
         self.operations = operations
diff --git a/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py b/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
index 825f949d65..0ff7e11c31 100644
--- a/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
+++ b/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
@@ -8,18 +8,21 @@ import dffml
 import dffml_feature_git.feature.definitions
 
 
-class AliceGitRepo(NamedTuple):
+class AliceGitRepoSpec(NamedTuple):
     directory: str
     URL: str
 
 
+AliceGitRepo = dffml.LockReadWrite[AliceGitRepoSpec]
+
+
 class AliceGitRepoInputSetContextHandle(dffml.BaseContextHandle):
     def as_string(self) -> str:
         return str(self.ctx.repo)
 
 
 class AliceGitRepoInputSetContext(dffml.BaseInputSetContext):
-    def __init__(self, repo: AliceGitRepo):
+    def __init__(self, repo: AliceGitRepoSpec):
         self.repo = repo
 
     async def handle(self) -> AliceGitRepoInputSetContextHandle:
```

- Is this the same as what we had in c89d3d8444cdad248fce5a7fff959c9ea48a7c9d ?

```python
    async def alice_contribute_readme(self, repo: AliceGitRepo) -> ReadmeGitRepo:
        key, definition = list(self.parent.op.outputs.items())[0]
        await self.octx.ictx.cadd(
            AliceGitRepoInputSetContext(repo),
            dffml.Input(
                value=repo,
                definition=definition,
                parents=None,
                origin=(self.parent.op.instance_name, key),
            )
        )
```

```diff
diff --git a/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py b/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
index 825f949d65..1bc1c41e50 100644
--- a/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
+++ b/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
@@ -203,30 +203,22 @@ class OverlayREADME:
     ReadmePRBody = NewType("github.pr.body", str)

     # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
-    async def alice_contribute_readme(self, repo: AliceGitRepo) -> ReadmeGitRepo:
-        # TODO Clean this up once SystemContext refactor complete
-        readme_dataflow_cls_upstream = OverlayREADME
-        readme_dataflow_cls_overlays = dffml.Overlay.load(
-            entrypoint="dffml.overlays.alice.please.contribute.recommended_community_standards.overlay.readme"
-        )
-        readme_dataflow_upstream = dffml.DataFlow(
-            *dffml.object_to_operations(readme_dataflow_cls_upstream)
-        )
+    async def new_context(self, repo: AliceGitRepo) -> ReadmeGitRepo:
+        return
         # auto_flow with overlays
-        readme_dataflow = dffml.DataFlow(
+        dataflow = dffml.DataFlow(
             *itertools.chain(
                 *[
                     dffml.object_to_operations(cls)
                     for cls in [
-                        readme_dataflow_cls_upstream,
-                        *readme_dataflow_cls_overlays,
+                        upstream,
+                        *overlays,
                     ]
                 ]
             )
         )
         async with dffml.run_dataflow.imp(
-            # dataflow=self.octx.config.dataflow,
-            dataflow=readme_dataflow,
+            dataflow=dataflow,
             input_set_context_cls=AliceGitRepoInputSetContext,
         ) as custom_run_dataflow:
             # Copy all inputs from parent context into child. We eventually
@@ -277,6 +269,18 @@ class OverlayREADME:
                     },
                 )

+    async def alice_contribute_readme(self, repo: AliceGitRepo) -> ReadmeGitRepo:
+        key, definition = list(self.parent.op.outputs.items())[0]
+        await self.octx.ictx.cadd(
+            AliceGitRepoInputSetContext(repo),
+            dffml.Input(
+                value=repo,
+                definition=definition,
+                parents=None,
+                origin=(self.parent.op.instance_name, key),
+            )
+        )
+
     # TODO Run this system context where readme contexts is given on CLI or
     # overriden via disabling of static overlay and application of overlay to
     # generate contents dynamiclly.
```

- Visualize the flow before we attempt to add `CONTRIBUTING.md` contribution

```console
$ dffml service dev export alice.cli:AlicePleaseContributeCLIDataFlow | tee alice.please.contribute.recommended_community_standards.json
$ (echo -e 'HTTP/1.0 200 OK\n' && dffml dataflow diagram -shortname alice.please.contribute.recommended_community_standards.json) | nc -Nlp 9999;
```

```mermaid
graph TD
subgraph a759a07029077edc5c37fea0326fa281[Processing Stage]
style a759a07029077edc5c37fea0326fa281 fill:#afd388b5,stroke:#a4ca7a
subgraph 8cfb8cd5b8620de4a7ebe0dfec00771a[cli_has_repos]
style 8cfb8cd5b8620de4a7ebe0dfec00771a fill:#fff4de,stroke:#cece71
d493c90433d19f11f33c2d72cd144940[cli_has_repos]
e07552ee3b6b7696cb3ddd786222eaad(cmd)
e07552ee3b6b7696cb3ddd786222eaad --> d493c90433d19f11f33c2d72cd144940
cee6b5fdd0b6fbd0539cdcdc7f5a3324(wanted)
cee6b5fdd0b6fbd0539cdcdc7f5a3324 --> d493c90433d19f11f33c2d72cd144940
79e1ea6822bff603a835fb8ee80c7ff3(result)
d493c90433d19f11f33c2d72cd144940 --> 79e1ea6822bff603a835fb8ee80c7ff3
end
subgraph 0c2b64320fb5666a034794bb2195ecf0[cli_is_asking_for_recommended_community_standards]
style 0c2b64320fb5666a034794bb2195ecf0 fill:#fff4de,stroke:#cece71
222ee6c0209f1f1b7a782bc1276868c7[cli_is_asking_for_recommended_community_standards]
330f463830aa97e88917d5a9d1c21500(cmd)
330f463830aa97e88917d5a9d1c21500 --> 222ee6c0209f1f1b7a782bc1276868c7
ba29b52e9c5aa88ea1caeeff29bfd491(result)
222ee6c0209f1f1b7a782bc1276868c7 --> ba29b52e9c5aa88ea1caeeff29bfd491
end
subgraph eac58e8db2b55cb9cc5474aaa402c93e[cli_is_meant_on_this_repo]
style eac58e8db2b55cb9cc5474aaa402c93e fill:#fff4de,stroke:#cece71
6c819ad0228b0e7094b33e0634da9a38[cli_is_meant_on_this_repo]
dc7c5f0836f7d2564c402bf956722672(cmd)
dc7c5f0836f7d2564c402bf956722672 --> 6c819ad0228b0e7094b33e0634da9a38
58d8518cb0d6ef6ad35dc242486f1beb(wanted)
58d8518cb0d6ef6ad35dc242486f1beb --> 6c819ad0228b0e7094b33e0634da9a38
135ee61e3402d6fcbd7a219b0b4ccd73(result)
6c819ad0228b0e7094b33e0634da9a38 --> 135ee61e3402d6fcbd7a219b0b4ccd73
end
subgraph 37887bf260c5c8e9bd18038401008bbc[cli_run_on_repo]
style 37887bf260c5c8e9bd18038401008bbc fill:#fff4de,stroke:#cece71
9d1042f33352800e54d98c9c5a4223df[cli_run_on_repo]
e824ae072860bc545fc7d55aa0bca479(repo)
e824ae072860bc545fc7d55aa0bca479 --> 9d1042f33352800e54d98c9c5a4223df
40109d487bb9f08608d8c5f6e747042f(result)
9d1042f33352800e54d98c9c5a4223df --> 40109d487bb9f08608d8c5f6e747042f
end
subgraph 66ecd0c1f2e08941c443ec9cd89ec589[guess_repo_string_is_directory]
style 66ecd0c1f2e08941c443ec9cd89ec589 fill:#fff4de,stroke:#cece71
737d719a0c348ff65456024ddbc530fe[guess_repo_string_is_directory]
33d806f9b732bfd6b96ae2e9e4243a68(repo_string)
33d806f9b732bfd6b96ae2e9e4243a68 --> 737d719a0c348ff65456024ddbc530fe
dd5aab190ce844673819298c5b8fde76(result)
737d719a0c348ff65456024ddbc530fe --> dd5aab190ce844673819298c5b8fde76
end
subgraph 2bcd191634373f4b97ecb9546df23ee5[alice_contribute_contributing]
style 2bcd191634373f4b97ecb9546df23ee5 fill:#fff4de,stroke:#cece71
a2541ce40b2e5453e8e919021011e5e4[alice_contribute_contributing]
3786b4af914402320d260d077844620e(repo)
3786b4af914402320d260d077844620e --> a2541ce40b2e5453e8e919021011e5e4
da4270ecc44b6d9eed9809a560d24a28(result)
a2541ce40b2e5453e8e919021011e5e4 --> da4270ecc44b6d9eed9809a560d24a28
end
subgraph 13b430e6b93de7e40957165687f8e593[contribute_contributing_md]
style 13b430e6b93de7e40957165687f8e593 fill:#fff4de,stroke:#cece71
ff8f8968322872ccc3cf151d167e22a2[contribute_contributing_md]
4f752ce18209f62ed749e88dd1f70266(base)
4f752ce18209f62ed749e88dd1f70266 --> ff8f8968322872ccc3cf151d167e22a2
2def8c6923c832adf33989b26c91295a(commit_message)
2def8c6923c832adf33989b26c91295a --> ff8f8968322872ccc3cf151d167e22a2
f5548fcbcec8745ddf04104fc78e83a3(repo)
f5548fcbcec8745ddf04104fc78e83a3 --> ff8f8968322872ccc3cf151d167e22a2
24292ae12efd27a227a0d6368ba01faa(result)
ff8f8968322872ccc3cf151d167e22a2 --> 24292ae12efd27a227a0d6368ba01faa
end
subgraph 71a5f33f393735fa1cc91419b43db115[contributing_commit_message]
style 71a5f33f393735fa1cc91419b43db115 fill:#fff4de,stroke:#cece71
d034a42488583464e601bcaee619a539[contributing_commit_message]
c0a0fa68a872adf890ed639e07ed5882(issue_url)
c0a0fa68a872adf890ed639e07ed5882 --> d034a42488583464e601bcaee619a539
ce14ca2191f2b1c13c605b240e797255(result)
d034a42488583464e601bcaee619a539 --> ce14ca2191f2b1c13c605b240e797255
end
subgraph db8a1253cc59982323848f5e42c23c9d[contributing_issue]
style db8a1253cc59982323848f5e42c23c9d fill:#fff4de,stroke:#cece71
c39bd2cc88723432048c434fdd337eab[contributing_issue]
821d21e8a69d1fa1757147e7e768f306(body)
821d21e8a69d1fa1757147e7e768f306 --> c39bd2cc88723432048c434fdd337eab
0581b90c76b0a4635a968682b060abff(repo)
0581b90c76b0a4635a968682b060abff --> c39bd2cc88723432048c434fdd337eab
809719538467f6d0bf18f7ae26f08d80(title)
809719538467f6d0bf18f7ae26f08d80 --> c39bd2cc88723432048c434fdd337eab
c9f2ea5a7f25b3ae9fbf5041be5fa071(result)
c39bd2cc88723432048c434fdd337eab --> c9f2ea5a7f25b3ae9fbf5041be5fa071
end
subgraph 1e6046d1a567bf390566b1b995df9dcf[contributing_pr]
style 1e6046d1a567bf390566b1b995df9dcf fill:#fff4de,stroke:#cece71
4ec1433342f2f12ab8c59efab20e7b06[contributing_pr]
bb85c3467b05192c99a3954968c7a612(base)
bb85c3467b05192c99a3954968c7a612 --> 4ec1433342f2f12ab8c59efab20e7b06
77f6c1c6b7ee62881b49c289097dfbde(body)
77f6c1c6b7ee62881b49c289097dfbde --> 4ec1433342f2f12ab8c59efab20e7b06
a0a2fabc65fe5601c7ea289124d04f70(head)
a0a2fabc65fe5601c7ea289124d04f70 --> 4ec1433342f2f12ab8c59efab20e7b06
cf92708915b9f41cb490b991abd6c374(origin)
cf92708915b9f41cb490b991abd6c374 --> 4ec1433342f2f12ab8c59efab20e7b06
210ae36c85f3597c248e0b32da7661ae(repo)
210ae36c85f3597c248e0b32da7661ae --> 4ec1433342f2f12ab8c59efab20e7b06
1700dc637c25bd503077a2a1422142e2(title)
1700dc637c25bd503077a2a1422142e2 --> 4ec1433342f2f12ab8c59efab20e7b06
806e8c455d2bb7ad68112d2a7e16eed6(result)
4ec1433342f2f12ab8c59efab20e7b06 --> 806e8c455d2bb7ad68112d2a7e16eed6
end
subgraph 04c27c13241164ae88456c1377995897[contributing_pr_body]
style 04c27c13241164ae88456c1377995897 fill:#fff4de,stroke:#cece71
a3cebe78451142664930d44ad4d7d181[contributing_pr_body]
6118470d0158ef1a220fe7c7232e1b63(contributing_issue)
6118470d0158ef1a220fe7c7232e1b63 --> a3cebe78451142664930d44ad4d7d181
99a7dd1ae037153eef80e1dee51b9d2b(result)
a3cebe78451142664930d44ad4d7d181 --> 99a7dd1ae037153eef80e1dee51b9d2b
end
subgraph 0d4627f8d8564b6c4ba33c12dcb58fc1[contributing_pr_title]
style 0d4627f8d8564b6c4ba33c12dcb58fc1 fill:#fff4de,stroke:#cece71
bfa172a9399604546048d60db0a36187[contributing_pr_title]
0fd26f9166ccca10c68e9aefa9c15767(contributing_issue)
0fd26f9166ccca10c68e9aefa9c15767 --> bfa172a9399604546048d60db0a36187
77a2f9d4dfad5f520f1502e8ba70e47a(result)
bfa172a9399604546048d60db0a36187 --> 77a2f9d4dfad5f520f1502e8ba70e47a
end
subgraph c67b92ef6a2e025ca086bc2f89d9afbb[create_contributing_file_if_not_exists]
style c67b92ef6a2e025ca086bc2f89d9afbb fill:#fff4de,stroke:#cece71
993a1fe069a02a45ba3579b1902b2a36[create_contributing_file_if_not_exists]
401c179bb30b24c2ca989c64d0b1cdc7(contributing_contents)
401c179bb30b24c2ca989c64d0b1cdc7 --> 993a1fe069a02a45ba3579b1902b2a36
dde78f81b1bdfe02c0a2bf6e51f65cb4(repo)
dde78f81b1bdfe02c0a2bf6e51f65cb4 --> 993a1fe069a02a45ba3579b1902b2a36
e5b8d158dc0ec476dbbd44549a981815(result)
993a1fe069a02a45ba3579b1902b2a36 --> e5b8d158dc0ec476dbbd44549a981815
end
subgraph 4ea6696419c4a0862a4f63ea1f60c751[create_branch_if_none_exists]
style 4ea6696419c4a0862a4f63ea1f60c751 fill:#fff4de,stroke:#cece71
502369b37882b300d6620d5b4020f5b2[create_branch_if_none_exists]
fdcb9b6113856222e30e093f7c38065e(name)
fdcb9b6113856222e30e093f7c38065e --> 502369b37882b300d6620d5b4020f5b2
bdcf4b078985f4a390e4ed4beacffa65(repo)
bdcf4b078985f4a390e4ed4beacffa65 --> 502369b37882b300d6620d5b4020f5b2
5a5493ab86ab4053f1d44302e7bdddd6(result)
502369b37882b300d6620d5b4020f5b2 --> 5a5493ab86ab4053f1d44302e7bdddd6
end
subgraph b1d510183f6a4c3fde207a4656c72cb4[determin_base_branch]
style b1d510183f6a4c3fde207a4656c72cb4 fill:#fff4de,stroke:#cece71
476aecd4d4d712cda1879feba46ea109[determin_base_branch]
ff47cf65b58262acec28507f4427de45(default_branch)
ff47cf65b58262acec28507f4427de45 --> 476aecd4d4d712cda1879feba46ea109
150204cd2d5a921deb53c312418379a1(result)
476aecd4d4d712cda1879feba46ea109 --> 150204cd2d5a921deb53c312418379a1
end
subgraph 2a08ff341f159c170b7fe017eaad2f18[git_repo_to_alice_git_repo]
style 2a08ff341f159c170b7fe017eaad2f18 fill:#fff4de,stroke:#cece71
7f74112f6d30c6289caa0a000e87edab[git_repo_to_alice_git_repo]
e58180baf478fe910359358a3fa02234(repo)
e58180baf478fe910359358a3fa02234 --> 7f74112f6d30c6289caa0a000e87edab
9b92d5a346885079a2821c4d27cb5174(result)
7f74112f6d30c6289caa0a000e87edab --> 9b92d5a346885079a2821c4d27cb5174
end
subgraph b5d35aa8a8dcd28d22d47caad02676b0[guess_repo_string_is_url]
style b5d35aa8a8dcd28d22d47caad02676b0 fill:#fff4de,stroke:#cece71
0de074e71a32e30889b8bb400cf8db9f[guess_repo_string_is_url]
c3bfe79b396a98ce2d9bfe772c9c20af(repo_string)
c3bfe79b396a98ce2d9bfe772c9c20af --> 0de074e71a32e30889b8bb400cf8db9f
2a1c620b0d510c3d8ed35deda41851c5(result)
0de074e71a32e30889b8bb400cf8db9f --> 2a1c620b0d510c3d8ed35deda41851c5
end
subgraph 60791520c6d124c0bf15e599132b0caf[guessed_repo_string_is_operations_git_url]
style 60791520c6d124c0bf15e599132b0caf fill:#fff4de,stroke:#cece71
102f173505d7b546236cdeff191369d4[guessed_repo_string_is_operations_git_url]
4934c6211334318c63a5e91530171c9b(repo_url)
4934c6211334318c63a5e91530171c9b --> 102f173505d7b546236cdeff191369d4
8d0adc31da1a0919724baf73d047743c(result)
102f173505d7b546236cdeff191369d4 --> 8d0adc31da1a0919724baf73d047743c
end
subgraph f2c7b93622447999daab403713239ada[guessed_repo_string_means_no_git_branch_given]
style f2c7b93622447999daab403713239ada fill:#fff4de,stroke:#cece71
c8294a87e7aae8f7f9cb7f53e054fed5[guessed_repo_string_means_no_git_branch_given]
5567dd8a6d7ae4fe86252db32e189a4d(repo_url)
5567dd8a6d7ae4fe86252db32e189a4d --> c8294a87e7aae8f7f9cb7f53e054fed5
d888e6b64b5e3496056088f14dab9894(result)
c8294a87e7aae8f7f9cb7f53e054fed5 --> d888e6b64b5e3496056088f14dab9894
end
subgraph 113addf4beee5305fdc79d2363608f9d[github_owns_remote]
style 113addf4beee5305fdc79d2363608f9d fill:#fff4de,stroke:#cece71
049b72b81b976fbb43607bfeeb0464c5[github_owns_remote]
6c2b36393ffff6be0b4ad333df2d9419(remote)
6c2b36393ffff6be0b4ad333df2d9419 --> 049b72b81b976fbb43607bfeeb0464c5
19a9ee483c1743e6ecf0a2dc3b6f8c7a(repo)
19a9ee483c1743e6ecf0a2dc3b6f8c7a --> 049b72b81b976fbb43607bfeeb0464c5
b4cff8d194413f436d94f9d84ece0262(result)
049b72b81b976fbb43607bfeeb0464c5 --> b4cff8d194413f436d94f9d84ece0262
end
subgraph 8506cba6514466fb6d65f33ace4b0eac[alice_contribute_readme]
style 8506cba6514466fb6d65f33ace4b0eac fill:#fff4de,stroke:#cece71
d4507d3d1c3fbf3e7e373eae24797667[alice_contribute_readme]
68cf7d6869d027ca46a5fb4dbf7001d1(repo)
68cf7d6869d027ca46a5fb4dbf7001d1 --> d4507d3d1c3fbf3e7e373eae24797667
2f9316539862f119f7c525bf9061e974(result)
d4507d3d1c3fbf3e7e373eae24797667 --> 2f9316539862f119f7c525bf9061e974
end
subgraph 4233e6dc67cba131d4ef005af9c02959[contribute_readme_md]
style 4233e6dc67cba131d4ef005af9c02959 fill:#fff4de,stroke:#cece71
3db0ee5d6ab83886bded5afd86f3f88f[contribute_readme_md]
37044e4d8610abe13849bc71a5cb7591(base)
37044e4d8610abe13849bc71a5cb7591 --> 3db0ee5d6ab83886bded5afd86f3f88f
631c051fe6050ae8f8fc3321ed00802d(commit_message)
631c051fe6050ae8f8fc3321ed00802d --> 3db0ee5d6ab83886bded5afd86f3f88f
182194bab776fc9bc406ed573d621b68(repo)
182194bab776fc9bc406ed573d621b68 --> 3db0ee5d6ab83886bded5afd86f3f88f
0ee9f524d2db12be854fe611fa8126dd(result)
3db0ee5d6ab83886bded5afd86f3f88f --> 0ee9f524d2db12be854fe611fa8126dd
end
subgraph a6080d9c45eb5f806a47152a18bf7830[create_readme_file_if_not_exists]
style a6080d9c45eb5f806a47152a18bf7830 fill:#fff4de,stroke:#cece71
67e388f508dd96084c37d236a2c67e67[create_readme_file_if_not_exists]
54faf20bfdca0e63d07efb3e5a984cf1(readme_contents)
54faf20bfdca0e63d07efb3e5a984cf1 --> 67e388f508dd96084c37d236a2c67e67
8c089c362960ccf181742334a3dccaea(repo)
8c089c362960ccf181742334a3dccaea --> 67e388f508dd96084c37d236a2c67e67
5cc65e17d40e6a7223c1504f1c4b0d2a(result)
67e388f508dd96084c37d236a2c67e67 --> 5cc65e17d40e6a7223c1504f1c4b0d2a
end
subgraph e7757158127e9845b2915c16a7fa80c5[readme_commit_message]
style e7757158127e9845b2915c16a7fa80c5 fill:#fff4de,stroke:#cece71
562bdc535c7cebfc66dba920b1a17540[readme_commit_message]
0af5cbea9050874a0a3cba73bb61f892(issue_url)
0af5cbea9050874a0a3cba73bb61f892 --> 562bdc535c7cebfc66dba920b1a17540
2641f3b67327fb7518ee34a3a40b0755(result)
562bdc535c7cebfc66dba920b1a17540 --> 2641f3b67327fb7518ee34a3a40b0755
end
subgraph cf99ff6fad80e9c21266b43fd67b2f7b[readme_issue]
style cf99ff6fad80e9c21266b43fd67b2f7b fill:#fff4de,stroke:#cece71
da44417f891a945085590baafffc2bdb[readme_issue]
d519830ab4e07ec391038e8581889ac3(body)
d519830ab4e07ec391038e8581889ac3 --> da44417f891a945085590baafffc2bdb
268852aa3fa8ab0864a32abae5a333f7(repo)
268852aa3fa8ab0864a32abae5a333f7 --> da44417f891a945085590baafffc2bdb
77a11dd29af309cf43ed321446c4bf01(title)
77a11dd29af309cf43ed321446c4bf01 --> da44417f891a945085590baafffc2bdb
1d2360c9da18fac0b6ec142df8f3fbda(result)
da44417f891a945085590baafffc2bdb --> 1d2360c9da18fac0b6ec142df8f3fbda
end
subgraph 7ec0442cf2d95c367912e8abee09b217[readme_pr]
style 7ec0442cf2d95c367912e8abee09b217 fill:#fff4de,stroke:#cece71
bb314dc452cde5b6af5ea94dd277ba40[readme_pr]
127d77c3047facc1daa621148c5a0a1d(base)
127d77c3047facc1daa621148c5a0a1d --> bb314dc452cde5b6af5ea94dd277ba40
cb421e4de153cbb912f7fbe57e4ad734(body)
cb421e4de153cbb912f7fbe57e4ad734 --> bb314dc452cde5b6af5ea94dd277ba40
cbf7a0b88c0a41953b245303f3e9a0d3(head)
cbf7a0b88c0a41953b245303f3e9a0d3 --> bb314dc452cde5b6af5ea94dd277ba40
e5f9ad44448abd2469b3fd9831f3d159(origin)
e5f9ad44448abd2469b3fd9831f3d159 --> bb314dc452cde5b6af5ea94dd277ba40
a35aee6711d240378eb57a3932537ca1(repo)
a35aee6711d240378eb57a3932537ca1 --> bb314dc452cde5b6af5ea94dd277ba40
dfcce88a7d605d46bf17de1159fbe5ad(title)
dfcce88a7d605d46bf17de1159fbe5ad --> bb314dc452cde5b6af5ea94dd277ba40
a210a7890a7bea8d629368e02da3d806(result)
bb314dc452cde5b6af5ea94dd277ba40 --> a210a7890a7bea8d629368e02da3d806
end
subgraph 227eabb1f1c5cc0bc931714a03049e27[readme_pr_body]
style 227eabb1f1c5cc0bc931714a03049e27 fill:#fff4de,stroke:#cece71
2aea976396cfe68dacd9bc7d4a3f0cba[readme_pr_body]
c5dfd309617c909b852afe0b4ae4a178(readme_issue)
c5dfd309617c909b852afe0b4ae4a178 --> 2aea976396cfe68dacd9bc7d4a3f0cba
40ddb5b508cb5643e7c91f7abdb72b84(result)
2aea976396cfe68dacd9bc7d4a3f0cba --> 40ddb5b508cb5643e7c91f7abdb72b84
end
subgraph 48687c84e69b3db0acca625cbe2e6b49[readme_pr_title]
style 48687c84e69b3db0acca625cbe2e6b49 fill:#fff4de,stroke:#cece71
d8668ff93f41bc241c8c540199cd7453[readme_pr_title]
3b2137dd1c61d0dac7d4e40fd6746cfb(readme_issue)
3b2137dd1c61d0dac7d4e40fd6746cfb --> d8668ff93f41bc241c8c540199cd7453
956e024fde513b3a449eac9ee42d6ab3(result)
d8668ff93f41bc241c8c540199cd7453 --> 956e024fde513b3a449eac9ee42d6ab3
end
subgraph d3ec0ac85209a7256c89d20f758f09f4[check_if_valid_git_repository_URL]
style d3ec0ac85209a7256c89d20f758f09f4 fill:#fff4de,stroke:#cece71
f577c71443f6b04596b3fe0511326c40[check_if_valid_git_repository_URL]
7440e73a8e8f864097f42162b74f2762(URL)
7440e73a8e8f864097f42162b74f2762 --> f577c71443f6b04596b3fe0511326c40
8e39b501b41c5d0e4596318f80a03210(valid)
f577c71443f6b04596b3fe0511326c40 --> 8e39b501b41c5d0e4596318f80a03210
end
subgraph af8da22d1318d911f29b95e687f87c5d[clone_git_repo]
style af8da22d1318d911f29b95e687f87c5d fill:#fff4de,stroke:#cece71
155b8fdb5524f6bfd5adbae4940ad8d5[clone_git_repo]
eed77b9eea541e0c378c67395351099c(URL)
eed77b9eea541e0c378c67395351099c --> 155b8fdb5524f6bfd5adbae4940ad8d5
8b5928cd265dd2c44d67d076f60c8b05(ssh_key)
8b5928cd265dd2c44d67d076f60c8b05 --> 155b8fdb5524f6bfd5adbae4940ad8d5
4e1d5ea96e050e46ebf95ebc0713d54c(repo)
155b8fdb5524f6bfd5adbae4940ad8d5 --> 4e1d5ea96e050e46ebf95ebc0713d54c
6a44de06a4a3518b939b27c790f6cdce{valid_git_repository_URL}
6a44de06a4a3518b939b27c790f6cdce --> 155b8fdb5524f6bfd5adbae4940ad8d5
end
subgraph d3d91578caf34c0ae944b17853783406[git_repo_default_branch]
style d3d91578caf34c0ae944b17853783406 fill:#fff4de,stroke:#cece71
546062a96122df465d2631f31df4e9e3[git_repo_default_branch]
181f1b33df4d795fbad2911ec7087e86(repo)
181f1b33df4d795fbad2911ec7087e86 --> 546062a96122df465d2631f31df4e9e3
57651c1bcd24b794dfc8d1794ab556d5(branch)
546062a96122df465d2631f31df4e9e3 --> 57651c1bcd24b794dfc8d1794ab556d5
5ed1ab77e726d7efdcc41e9e2f8039c6(remote)
546062a96122df465d2631f31df4e9e3 --> 5ed1ab77e726d7efdcc41e9e2f8039c6
4c3cdd5f15b7a846d291aac089e8a622{no_git_branch_given}
4c3cdd5f15b7a846d291aac089e8a622 --> 546062a96122df465d2631f31df4e9e3
end
end
subgraph a4827add25f5c7d5895c5728b74e2beb[Cleanup Stage]
style a4827add25f5c7d5895c5728b74e2beb fill:#afd388b5,stroke:#a4ca7a
end
subgraph 58ca4d24d2767176f196436c2890b926[Output Stage]
style 58ca4d24d2767176f196436c2890b926 fill:#afd388b5,stroke:#a4ca7a
end
subgraph inputs[Inputs]
style inputs fill:#f6dbf9,stroke:#a178ca
128516cfa09b0383023eab52ee24878a(seed<br>dffml.util.cli.CMD)
128516cfa09b0383023eab52ee24878a --> e07552ee3b6b7696cb3ddd786222eaad
ba29b52e9c5aa88ea1caeeff29bfd491 --> cee6b5fdd0b6fbd0539cdcdc7f5a3324
128516cfa09b0383023eab52ee24878a(seed<br>dffml.util.cli.CMD)
128516cfa09b0383023eab52ee24878a --> 330f463830aa97e88917d5a9d1c21500
128516cfa09b0383023eab52ee24878a(seed<br>dffml.util.cli.CMD)
128516cfa09b0383023eab52ee24878a --> dc7c5f0836f7d2564c402bf956722672
ba29b52e9c5aa88ea1caeeff29bfd491 --> 58d8518cb0d6ef6ad35dc242486f1beb
79e1ea6822bff603a835fb8ee80c7ff3 --> e824ae072860bc545fc7d55aa0bca479
135ee61e3402d6fcbd7a219b0b4ccd73 --> e824ae072860bc545fc7d55aa0bca479
40109d487bb9f08608d8c5f6e747042f --> 33d806f9b732bfd6b96ae2e9e4243a68
dd5aab190ce844673819298c5b8fde76 --> 3786b4af914402320d260d077844620e
9b92d5a346885079a2821c4d27cb5174 --> 3786b4af914402320d260d077844620e
150204cd2d5a921deb53c312418379a1 --> 4f752ce18209f62ed749e88dd1f70266
ce14ca2191f2b1c13c605b240e797255 --> 2def8c6923c832adf33989b26c91295a
da4270ecc44b6d9eed9809a560d24a28 --> f5548fcbcec8745ddf04104fc78e83a3
c9f2ea5a7f25b3ae9fbf5041be5fa071 --> c0a0fa68a872adf890ed639e07ed5882
c94383981c3a071b8c3df7293c8c7c92(seed<br>ContributingIssueBody)
c94383981c3a071b8c3df7293c8c7c92 --> 821d21e8a69d1fa1757147e7e768f306
da4270ecc44b6d9eed9809a560d24a28 --> 0581b90c76b0a4635a968682b060abff
90c6a88275f27b28dc12f5741ac1652f(seed<br>ContributingIssueTitle)
90c6a88275f27b28dc12f5741ac1652f --> 809719538467f6d0bf18f7ae26f08d80
150204cd2d5a921deb53c312418379a1 --> bb85c3467b05192c99a3954968c7a612
99a7dd1ae037153eef80e1dee51b9d2b --> 77f6c1c6b7ee62881b49c289097dfbde
24292ae12efd27a227a0d6368ba01faa --> a0a2fabc65fe5601c7ea289124d04f70
b4cff8d194413f436d94f9d84ece0262 --> cf92708915b9f41cb490b991abd6c374
da4270ecc44b6d9eed9809a560d24a28 --> 210ae36c85f3597c248e0b32da7661ae
77a2f9d4dfad5f520f1502e8ba70e47a --> 1700dc637c25bd503077a2a1422142e2
c9f2ea5a7f25b3ae9fbf5041be5fa071 --> 6118470d0158ef1a220fe7c7232e1b63
c9f2ea5a7f25b3ae9fbf5041be5fa071 --> 0fd26f9166ccca10c68e9aefa9c15767
90b3c16d6d8884aa6f70b475d98f661b(seed<br>repo.directory.contributing.contents)
90b3c16d6d8884aa6f70b475d98f661b --> 401c179bb30b24c2ca989c64d0b1cdc7
da4270ecc44b6d9eed9809a560d24a28 --> dde78f81b1bdfe02c0a2bf6e51f65cb4
21ccfd2c550bd853d28581f0b0c9f9fe(seed<br>default.branch.name)
21ccfd2c550bd853d28581f0b0c9f9fe --> fdcb9b6113856222e30e093f7c38065e
dd5aab190ce844673819298c5b8fde76 --> bdcf4b078985f4a390e4ed4beacffa65
9b92d5a346885079a2821c4d27cb5174 --> bdcf4b078985f4a390e4ed4beacffa65
5a5493ab86ab4053f1d44302e7bdddd6 --> ff47cf65b58262acec28507f4427de45
57651c1bcd24b794dfc8d1794ab556d5 --> ff47cf65b58262acec28507f4427de45
4e1d5ea96e050e46ebf95ebc0713d54c --> e58180baf478fe910359358a3fa02234
40109d487bb9f08608d8c5f6e747042f --> c3bfe79b396a98ce2d9bfe772c9c20af
2a1c620b0d510c3d8ed35deda41851c5 --> 4934c6211334318c63a5e91530171c9b
2a1c620b0d510c3d8ed35deda41851c5 --> 5567dd8a6d7ae4fe86252db32e189a4d
5ed1ab77e726d7efdcc41e9e2f8039c6 --> 6c2b36393ffff6be0b4ad333df2d9419
dd5aab190ce844673819298c5b8fde76 --> 19a9ee483c1743e6ecf0a2dc3b6f8c7a
9b92d5a346885079a2821c4d27cb5174 --> 19a9ee483c1743e6ecf0a2dc3b6f8c7a
dd5aab190ce844673819298c5b8fde76 --> 68cf7d6869d027ca46a5fb4dbf7001d1
9b92d5a346885079a2821c4d27cb5174 --> 68cf7d6869d027ca46a5fb4dbf7001d1
150204cd2d5a921deb53c312418379a1 --> 37044e4d8610abe13849bc71a5cb7591
2641f3b67327fb7518ee34a3a40b0755 --> 631c051fe6050ae8f8fc3321ed00802d
2f9316539862f119f7c525bf9061e974 --> 182194bab776fc9bc406ed573d621b68
d2708225c1f4c95d613a2645a17a5bc0(seed<br>repo.directory.readme.contents)
d2708225c1f4c95d613a2645a17a5bc0 --> 54faf20bfdca0e63d07efb3e5a984cf1
2f9316539862f119f7c525bf9061e974 --> 8c089c362960ccf181742334a3dccaea
1d2360c9da18fac0b6ec142df8f3fbda --> 0af5cbea9050874a0a3cba73bb61f892
1daacccd02f8117e67ad3cb8686a732c(seed<br>ReadmeIssueBody)
1daacccd02f8117e67ad3cb8686a732c --> d519830ab4e07ec391038e8581889ac3
2f9316539862f119f7c525bf9061e974 --> 268852aa3fa8ab0864a32abae5a333f7
0c1ab2d4bda10e1083557833ae5c5da4(seed<br>ReadmeIssueTitle)
0c1ab2d4bda10e1083557833ae5c5da4 --> 77a11dd29af309cf43ed321446c4bf01
150204cd2d5a921deb53c312418379a1 --> 127d77c3047facc1daa621148c5a0a1d
40ddb5b508cb5643e7c91f7abdb72b84 --> cb421e4de153cbb912f7fbe57e4ad734
0ee9f524d2db12be854fe611fa8126dd --> cbf7a0b88c0a41953b245303f3e9a0d3
b4cff8d194413f436d94f9d84ece0262 --> e5f9ad44448abd2469b3fd9831f3d159
2f9316539862f119f7c525bf9061e974 --> a35aee6711d240378eb57a3932537ca1
956e024fde513b3a449eac9ee42d6ab3 --> dfcce88a7d605d46bf17de1159fbe5ad
1d2360c9da18fac0b6ec142df8f3fbda --> c5dfd309617c909b852afe0b4ae4a178
1d2360c9da18fac0b6ec142df8f3fbda --> 3b2137dd1c61d0dac7d4e40fd6746cfb
8d0adc31da1a0919724baf73d047743c --> 7440e73a8e8f864097f42162b74f2762
8d0adc31da1a0919724baf73d047743c --> eed77b9eea541e0c378c67395351099c
a6ed501edbf561fda49a0a0a3ca310f0(seed<br>git_repo_ssh_key)
a6ed501edbf561fda49a0a0a3ca310f0 --> 8b5928cd265dd2c44d67d076f60c8b05
8e39b501b41c5d0e4596318f80a03210 --> 6a44de06a4a3518b939b27c790f6cdce
4e1d5ea96e050e46ebf95ebc0713d54c --> 181f1b33df4d795fbad2911ec7087e86
end
```

- Notes
  - `create_*_if_not_exists` doesn't appear connected.
- Only either README or CONTRIBUTING is currently being added when
  we run with our new CONTRIBUTING contribution flow overlayed.

```console
$ for pr in $(gh -R https://github.com/pdxjohnny/testaaaa pr list --json number --jq '.[].number'); do gh -R https://github.com/pdxjohnny/testaaaa pr close "${pr}"; done
✓ Closed pull request #222 (Recommended Community Standard: README)
✓ Closed pull request #219 (Recommended Community Standard: CONTRIBUTING)
$ nodemon -e py --exec 'clear; for pr in $(gh -R https://github.com/pdxjohnny/testaaaa pr list --json number --jq '.[].number'); do gh -R https://github.com/pdxjohnny/testaaaa pr close "${pr}"; done; (alice please contribute -log debug -repos https://github.com/pdxjohnny/testaaaa -- recommended community standards; gh -R https://github.com/pdxjohnny/testaaaa pr list) 2>&1 | tee .output/$(date +%4Y-%m-%d-%H-%M).txt; test 1'
$ less -S .output/$(ls .output/ | tail -n 1)
```

### Refactor into README and CONTRIBUTING Overlays

- Had the thought, aren't we just adding a new context here?

```diff
diff --git a/dffml/df/memory.py b/dffml/df/memory.py
index 59286d4927..87c75d637b 100644
--- a/dffml/df/memory.py
+++ b/dffml/df/memory.py
@@ -377,6 +377,7 @@ class MemoryInputNetworkContext(BaseInputNetworkContext):
                     self.ctxhd[handle_string].by_origin[item.origin] = []
                 # Add input to by origin set
                 self.ctxhd[handle_string].by_origin[item.origin].append(item)
+                self.logger.debug("Added to %s: %r", handle_string, item)

     async def uadd(self, *args: Input):
         """
diff --git a/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py b/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
index 2873a1b193..cc4d374e57 100644
--- a/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
+++ b/entities/alice/alice/please/contribute/recommended_community_standards/recommended_community_standards.py
@@ -1,7 +1,8 @@
+import asyncio
 import pathlib
 import textwrap
 import itertools
-from typing import NamedTuple, NewType, Optional
+from typing import NamedTuple, NewType, Optional, Type, Any


 import dffml
@@ -183,6 +184,34 @@ class OverlayGitHub:
         return remote


+async def context_adder(
+    self,
+    upstream_cls: Type[Any],
+    input_set_context: dffml.BaseInputSetContext,
+    value: Any,
+):
+    upstream = dffml.DataFlow(*dffml.object_to_operations(upstream_cls))
+    key, definition = list(self.parent.op.outputs.items())[0]
+    async with self.octx.ictx.definitions(self.ctx) as definitions:
+        await self.octx.ictx.cadd(
+            input_set_context,
+            dffml.Input(
+                value=value,
+                definition=definition,
+                parents=None,
+                origin=(self.parent.op.instance_name, key),
+            ),
+            *[
+                item
+                async for item in definitions.inputs()
+                if (
+                    item.definition in upstream.definitions.values()
+                    and item.definition not in self.parent.op.inputs.values()
+                )
+            ],
+        )
+
+
 # NOTE Not sure if the orchestrator will know what to do if we do this
 # ReadmeGitRepo = AliceGitRepo
 class ReadmeGitRepo(NamedTuple):
@@ -204,6 +233,9 @@ class OverlayREADME:

     # async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
     async def alice_contribute_readme(self, repo: AliceGitRepo) -> ReadmeGitRepo:
+        # await context_adder(
+        #     self, OverlayREADME, AliceGitRepoInputSetContext(repo), repo
+        # )
         # TODO Clean this up once SystemContext refactor complete
         readme_dataflow_cls_upstream = OverlayREADME
         readme_dataflow_cls_overlays = dffml.Overlay.load(
```

```
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch Stage: PROCESSING: alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch Inputs: {'default_branch': 'master'}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch Conditions: {}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch Outputs: {'result': 'master'}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryInputNetworkContext:Added to https://github.com/pdxjohnny/testaaaa: Input(value=master, definition=repo.git.base.branch)
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 6fc55525-c499-421c-8b07-497dd277b1ff(GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa')) (now held by Operation(name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing', inputs={'repo': AliceGitRepo}, outputs={'result': ContributingGitRepo}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing', validator=False, retry=0))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing Stage: PROCESSING: alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing Inputs: {'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa')}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing Conditions: {}
DEBUG:dffml.MemoryInputNetworkContext:Added to GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'): Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'), definition=ContributingGitRepo)
DEBUG:dffml.MemoryInputNetworkContext:Added to GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'): Input(value=origin, definition=writable.github.remote.origin)
DEBUG:dffml.MemoryInputNetworkContext:Added to GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'): Input(value=master, definition=repo.git.base.branch)
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayCONTRIBUTING:alice_contribute_contributing Outputs: None
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 6fc55525-c499-421c-8b07-497dd277b1ff(GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa')) (now held by Operation(name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists', inputs={'repo': AliceGitRepo, 'name': default.branch.name}, outputs={'result': git_branch}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists', validator=False, retry=0))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists Stage: PROCESSING: alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists Inputs: {'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'), 'name': 'main'}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists Conditions: {}
DEBUG:dffml_feature_git.util:proc.create: ('git', 'branch', '-r')
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:create_branch_if_none_exists Outputs: None
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 6fc55525-c499-421c-8b07-497dd277b1ff(GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa')) (now held by Operation(name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme', inputs={'repo': AliceGitRepo}, outputs={'result': ReadmeGitRepo}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme', validator=False, retry=0))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme Stage: PROCESSING: alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme Inputs: {'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa')}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme Conditions: {}
DEBUG:dffml.MemoryInputNetworkContext:Added to GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'): Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)
DEBUG:dffml.MemoryInputNetworkContext:Added to GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'): Input(value=origin, definition=writable.github.remote.origin)
DEBUG:dffml.MemoryInputNetworkContext:Added to GitRepoSpec(directory='/tmp/dffml-feature-git-rrflb9gm', URL='https://github.com/pdxjohnny/testaaaa'): Input(value=master, definition=repo.git.base.branch)
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme Outputs: None
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryInputNetworkContext:Received https://github.com/pdxjohnny/testaaaa result {} from <dffml.df.memory.MemoryOrchestratorContext object at 0x7f2405795d90>
DEBUG:dffml.MemoryInputNetworkContext:Received https://github.com/pdxjohnny/testaaaa result {} from <dffml.df.memory.MemoryOrchestratorContext object at 0x7f2405795d90>
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.cli.OverlayCLI:cli_run_on_repo Outputs: None
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOrchestratorContext:ctx.outstanding: 1
DEBUG:dffml.MemoryInputNetworkContext:Received 9eda82af632e2587d31fcd06d5fb0bfb1df47c4a8383e6a998f26c7c4906a86b result {} from <dffml.df.memory.MemoryOrchestratorContext object at 0x7f240588c040>
DEBUG:dffml.MemoryOrchestratorContext:ctx.outstanding: 0
https://github.com/pdxjohnny/testaaaa {}
9eda82af632e2587d31fcd06d5fb0bfb1df47c4a8383e6a998f26c7c4906a86b {}
```

- Want to understand why we are not waiting for the contexts to complete which were added
  in above diff and logs.
  - Fallback plan is to call both from a function in a separate overlay until it's working
    this will just call `run_custom` via a helper function for both README and CONTRIBUTING
    overlays.
    - Going to write this first, then contributing new file tutorial
    - Then tutorial on `alice shouldi contribute` with overlay addition via installed to entrypoint
    - Then test with ability to add overlays via CLI as one offs
    - Final bit of each tutorial is to add to this fallback overlay
  - If we still have time before 8 AM then we'll try to debug
- alice: please: contribute: recommended community standards: readme: Scope PR title and body definitions
  - 1cf1d73bcdb8f0940c02e01dec1e26253c2ec4cf
- Tried with `dffml.run()`, it worked right away. Going with this.
  - 1bf5e4c9a4eae34f30f9c4b5c9a04d09d6a11c6e
    - alice: please: contribute: recommended community standards: readme: Use dffml.subflow_typecast to execute README contribution
  - 85d57ad8989bfb12d5fe0fb6eec21002ce75f271
    - high level: subflow typecast: Basic OpImpCtx helper
  - 8c0531e5364c09fec019d1971e4033401bfcbd2b
    - overlay: static overlay application with loading entrypoint dataflow class with overlays applied.
  - af4306a500daf11ba3c4c3db39c1da9879456d12
    - alice: please: contribute: recommended community standards: Disable OverlayMetaIssue in default installed set of overlays


### How to help Alice contribute more files

This tutorial will help you create a new Open Architecture / Alice
overlay which runs when another flow runs. The upstream flow
in this case is the `AlicePleaseContributeRecommendedCommunityStandards`
base flow.

- Copy readme overlay to new file

```console
$ cp alice/please/contribute/recommended_community_standards/readme.py alice/please/contribute/recommended_community_standards/contribute.py
```

- Rename types, classes, variables, etc.

```console
$ sed -e 's/Readme/Contributing/g' -e 's/README/CONTRIBUTING/g' -e 's/readme/contributing/g' -i alice/please/contribute/recommended_community_standards/contribute.py
```

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

**dffml.git/entites/alice/entry_points.txt**

```ini
[dffml.overlays.alice.please.contribute.recommended_community_standards.overlay.contributing]
OverlayGit                                     = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGit
OverlayGitHub                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGitHu
```

- Reinstall for new entrypoints to take effect

```console
$ python -m pip install -e .
```

- Re-run the command and observe results

```console
for pr in $(gh -R https://github.com/$USER/ pr list --json number --jq '.[].number'); do gh -R https://github.com/pdxjohnny/testaaaa pr close "${pr}"; done; (alice please contribute -log debug -repos https://github.com/pdxjohnny/testaaaa -- recommended community standards; gh -R https://github.com/pdxjohnny/testaaaa pr list
```

![Screenshot showing pull request for adding README.md and CONTRIBUTING.md and CODE_OF_CONDUCT.md files](https://user-images.githubusercontent.com/5950433/181826046-53ae3ef5-6750-48ad-afd2-8cf9174e0b63.png)

### Script to test Coach Alice Our Open Source Guide tutorial

```bash
#!/usr/bin/env bash
set -x
set -e

# export USER=githubusername
export REPO_URL="https://github.com/$USER/my-new-python-project"

cd $(mktemp -d)

git clone --depth=1 -b alice https://github.com/intel/dffml dffml
cd dffml/entities/alice
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install \
  -e .[dev] \
  -e ../../ \
  -e ../../examples/shouldi/ \
  -e ../../feature/git/ \
  -e ../../operations/innersource/ \
  -e ../../configloader/yaml/

gh repo create -y --private "${REPO_URL}"
git clone "${REPO_URL}"
cd my-new-python-project
echo 'print("Hello World")' > test.py
git add test.py
git commit -sam 'Initial Commit'
git push --set-upstream origin $(git branch --show-current)
cd ..
rm -rf my-new-python-project

cp alice/please/contribute/recommended_community_standards/readme.py alice/please/contribute/recommended_community_standards/code_of_conduct.py

sed -e 's/Readme/CodeOfConduct/g' -e 's/README/CODE_OF_CONDUCT/g' -e 's/readme/code_of_conduct/g' -i alice/please/contribute/recommended_community_standards/code_of_conduct.py

sed -i 's/OverlayREADME .*/&\nOverlayCODE_OF_CONDUCT                         = alice.please.contribute.recommended_community_standards.code_of_conduct:OverlayCODE_OF_CONDUCT/' entry_points.txt

tee -a entry_points.txt << 'EOF'

[dffml.overlays.alice.please.contribute.recommended_community_standards.code_of_conduct]
OverlayGit                                     = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGit
OverlayGitHub                                  = alice.please.contribute.recommended_community_standards.recommended_community_standards:OverlayGitHub
EOF

python -m pip install -e .

alice please contribute -log debug -repos "${REPO_URL}" -- recommended community standards

gh -R "${REPO_URL}" pr list
# 343     Recommended Community Standard: README  alice-contribute-recommended-community-standards-readme OPEN
# 341     Recommended Community Standard: CONTRIBUTING    alice-contribute-recommended-community-standards-contributing   OPEN
# 339     Recommended Community Standard: CODE_OF_CONDUCT alice-contribute-recommended-community-standards-code_of_conduct        OPEN

for pr in $(gh -R "${REPO_URL}" pr list --json number --jq '.[].number');
do
  gh -R "${REPO_URL}" pr close "${pr}"
done
```

- The Alice codebase

```console
$ find alice/please/ -type f | grep -v __init
alice/please/contribute/recommended_community_standards/contributing.py
alice/please/contribute/recommended_community_standards/cli.py
alice/please/contribute/recommended_community_standards/readme.py
alice/please/contribute/recommended_community_standards/meta_issue.py
alice/please/contribute/recommended_community_standards/recommended_community_standards.py
```

### TODOs

- Explain how to add more top level Alice CLI comamnds
- Explain how to overlay shouldi flows beyond standard DFFML docs.