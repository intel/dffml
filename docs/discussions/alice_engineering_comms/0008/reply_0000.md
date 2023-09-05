## 2022-07-27 @pdxjohnny Engineering Logs

- TODO
  - [ ] Get involved in SCITT
    - [x] Meetings
      - https://docs.google.com/document/d/1vf-EliXByhg5HZfgVbTqZhfaJFCmvMdQuZ4tC-Eq6wg/edit#
      - Weekly Monday at 8 AM Pacific
        - Joining today
      - https://armltd.zoom.us/j/99133885299?pwd=b0w4aGorRkpjL3ZHa2NPSmRiNHpXUT09
    - [x] Mailing list
      - https://www.ietf.org/mailman/listinfo/scitt
      - https://mailarchive.ietf.org/arch/browse/scitt/
    - [ ] Slack
      - https://mailarchive.ietf.org/arch/msg/scitt/PbvoKOX996cNHJEOrjReaNlum64/
      - Going to email Orie Steele orie (at) transmute.industries to ask for an invite.
  - [x] Kick off OSS scans
    - Targeting collaboration with CRob on metrics insertion to OpenSSF DB
  - [ ] Finish Q3 plans (Gantt chart, meeting templates, etc.)
    - Generate template for auto creation to fill every meeting / fillable pre-meeting
  - [ ] Follow up with OneAPI folks
  - [ ] Overlay to `alice shouldi contribute` to create git repos when found from forks of PyPi packages
    - [ ] Associated tutorial
      - [ ] Linked from `README`
  - [ ] Finish out `alice please contribute recommended community standards`
        dynamic opimp for meta issue body creation
    - [ ] Associated tutorial
      - [ ] Linked from `README` and `CONTRIBUTING`
  - [ ] Software Analysis Trinity diagram showing Human Intent, Static Analysis, and Dynamic Analysis to represent the soul of the software / entity and the process taken to improve it.
    - [SoftwareAnalysisTrinity.drawio.xml](https://github.com/intel/dffml/files/9190063/SoftwareAnalysisTrinity.drawio.xml.txt)

### Refactoring and Thinking About Locking of Repos for Contributions

- Metadata
  - Date: 2022-07-27 20:30 UTC -7
- Saving this diff which was some work on dynamic application of overlay
  so as to support fixup of the OpImp for `meta_issue_body()`'s inputs.
  - We are going to table this for now for time reasons, but if someone
    wants to pick it up before @pdxjohnny is back in September, please
    give it a go (create an issue).
- Noticed that we have an issue with adding new files and locking. The current
  lock is on the `git_repository/GitRepoSpec`.
  - We then convert to `AliceGitRepo`, at which point anything take `AliceGitRepo`
- `alice`
  - Goal: Display Alice and software analysis trinity
  - https://free-images.com/search/?q=alice%27s+adventures+in+wonderland&cat=st
  - https://free-images.com/display/de_alices_abenteuer_im_43.html
  - https://github.com/KhorSL/ASCII-ART
  - Completed in d067273f8571b6a56733336663aaebc3acb3a701

![alice looking up](https://user-images.githubusercontent.com/5950433/181431145-18cfc8a7-28c8-486f-80f9-8b250e0b0943.png)

```console
$ python ascii_art.py /mnt/c/Users/Johnny/Downloads/alice-looking-up-white-background.png
```

```console
$ alice
usage: alice [-h] [-log LOG] {please,shouldi,threats} ...

                            .,*&&888@@#&:,
                          .:&::,...,:&#@@@#:.
                         .o,.       ..:8@@#@@+
                        .8o+,+o*+*+,+:&#@@#8@@.
                        &8&###@#&..*:8#@@#@#@@&+.
                       ,@:#@##@@8,:&#@@@###@88@@.
                      ,#@8&#@@@#o:#@@@@#8#@#8+&#.
                     +8####@@@@###@@@888#@@@#oo#.
                   .*8@###@@@@@@@@@#o*#@@#@@#8o@,
                  +###@#o8&#@@##8::##@@@&&#@8#&+
                  o@8&#&##::.,o&+88#&8##8*@@#@#,
                 .##888&&oo#&o8###8&o##8##&####8,
                .&#@8&:+o+&@@@#8#&8:8@@@@@#8@@@oo+
               ,&&#@##oo+*:@###&#88,@@@@#@o&##&8#@o,.
              ,#&###@@8:*,#o&@@@@##:&#@###*.&o++o#@@#&+
              o8&8o8@#8+,,#.88#@#&@&&#@##++*&#o&&&#@@@@.
              *88:,#8&#,o+:+@&8#:8@8&8#@@&o++,*++*+:#@@*.
              .+#:o###@8o&8*@o&o8@o888@@@o+:o*&&,@#:&@@@,
                *+&@8&#@o#8+8*#+8#+88@@@@@@&@###8##@8:*,
                  +o.@##@@@&88@*8@:8@@@@@@:.. ,8@:++.
                    +&++8@@@@##@@@@@@@@@@@+    88
                    &.   *@8@:+##o&888#@@@,   .#+
                    &.   ,@+o,.::+*+*:&#&,    ,@.
                    &.   .@8*,. ,*+++.+*     :8+
                    :+   .#@::. .8:.:**    .8@@o,
                    .o.   #@+   :@,.&*   .:@@@@@@8**.
                     +&.  :@o,+.*o,*,  .*@@@@@@@@@@#o
                   .*:&o.  8@o:,*:,  .o@@#8&&@@@@#@@@*
                 ,*:+:::o.*&8+,++  ,&@@#:  * :@@88@@@#:.
               ,::**:o:.,&*+*8:  *8@@##o   *,.8@@#8#@#@#+
              *:+*&o8:. ,o,o:8@+o@@88:*@+  +: +#@#####8##&.
            ,:&::88&,   .&:#o#@@@#,+&&*#&. .:,.&#@#88#####&,
           +::o+&8:.    :##88@@@@:.:8o+&8&. .. +8###&8&##&88*
         .:*+*.8#:    ,o*.+&@@#@8,,o8*+8##+    .+#8##8&&#8888:.
        ,:o., &#8.  .:8*.  .o, &#,*:8:+,&*:,    .8@@#o&&##8:&#8.
      .*o.*,+o8#*  +8&,  .::. .88.+:8o: ,+:,    ,o#@#8&o8##&#8+
     +o, .+,,o#8+,8@o**.,o*,  :8o +*8#*  +&,    ,*o@@#@&8&oo8&:,
    oo*+,,,*8@#..&@8:**:oo+. +8#* *+#@:...oo+  .**:8@@@ooo&:&o##+
    ::+..,++#@,.:##o&o**,....oo#++#8#@:.,:8&:.....*&@@#:oo*&oo&#@*
     .+**:*8@o,+##&o:+,,,+,,o*8#,,8@#@:,,+*o*++,,,,+&#@8*8o88&::*.        .,,,,,++,
         ..8@++#@#88:,,,.,,,:+#&,,#@@#:,,.,&o*,.+++*:#@8+:*+.    ......,:+*&,,.....
            +:&8#@@##8&+,,,***@&,.8@@@*,,,.:o8&o&*o&o&o.     .,.****::*:o*:o*o+,.
                 ...,*:*o&&o*8@@&o8@@@8+,,+:&&:+,...     ,++*&oo&8&&&oo#@##8#&8:.
                        o@#@@@@#@@@@@@@,.....  ..,,.+*::o#@##@##@#@#########@@@8:,.
                        ,@##@@88#@@@@@8     .:***oo*#8###8#@#@#@#@####@#@###@@#8&#:
                         8+.,8+..,*o#@+     ,o+o88&88###@8#######@8#8#88#8#88##88#&
                         *o  *+     #8       .  ,*o&#@##@@@@@@@@@######8#888&&oo:8:
                          8, ,&    +@*        .ooo&#@@@@@#@@@@@@####@##8#8##oo:o&:,
                          +&  &,  .@#.        .:8#@@@@@@@@@@##8#####8#o&&#8*:8&&8:
                           o* ,o  o@&        +o#@@@@@@@@#o&o88:&+ooo&:*::o:o&**o.:*+
                           .8. 8.,o#8    .+&#@@@@@@@@&o+,::*+*:+:, ,. ,.. .,. ,.
                            8. 8.,.&@:*:&@@@@@@@@8o+,    ,.
                           :@o:#,,o8&:o&@@@@#&:+.
                          .@@@@@@@@@@@#8&o+,
                           ,*:&#@#&o*,..

                                /\
                               /  \
                              Intent
                             /      \
                            /        \
                           /          \
                          /            \
                         /              \
                        /  Alice is Here \
                       /                  \
                      /                    \
                     /______________________\

             Dynamic Analysis          Static Analysis

    Alice's source code: https://github.com/intel/dffml/tree/alice/entities/alice
    How we built Alice: https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice
    How to extend Alice: https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
    Comment to get involved: https://github.com/intel/dffml/discussions/1406


positional arguments:
  {please,shouldi,threats}

optional arguments:
  -h, --help            show this help message and exit
  -log LOG              Logging Level
```

- TODO
  - [ ] Auto fork repo before push
    - [ ] Update origin to push to
    - [ ] Create PR
  - [ ] Update README to fix demos
  - [ ] Update CONTRIBUTING with tutorial on adding
        `CONTRIBUTING.md` check and contribution

**entities/alice/alice/timelines.py**

```python
"""
Helpers for the timelines we support
"""

# Trinity Day 0
ALICE_DAY_0_GREGORIAN = datetime.datetime(2022, 4, 16)

def date_alice_from_gregorian(date: str) -> int:
    # TODO
    return ALICE_DAY_0_GREGORIAN
```

```diff
diff --git a/dffml/base.py b/dffml/base.py
index fea0ef7220..9d6cd886fa 100644
--- a/dffml/base.py
+++ b/dffml/base.py
@@ -237,6 +237,7 @@ def convert_value(arg, value, *, dataclass=None):
                         # before checking if the value is an instance of that
                         # type. Since it doesn't make sense to check if the
                         # value is an instance of something that's not a type.
+                        print(possible_type, value)
                         if isinstance(possible_type, type) and isinstance(
                             value, possible_type
                         ):
diff --git a/dffml/df/system_context/system_context.py b/dffml/df/system_context/system_context.py
index e055a343f1..063547ad0c 100644
--- a/dffml/df/system_context/system_context.py
+++ b/dffml/df/system_context/system_context.py
@@ -90,11 +90,11 @@ class SystemContextConfig:
     # links: 'SystemContextConfig'
     overlay: Union["SystemContextConfig", DataFlow] = field(
         "The overlay we will apply with any overlays to merge within it (see default overlay usage docs)",
-        default=APPLY_INSTALLED_OVERLAYS,
+        default=None,
     )
     orchestrator: Union["SystemContextConfig", BaseOrchestrator] = field(
         "The system context who's default flow will be used to produce an orchestrator which will be used to execute this system context including application of overlays",
-        default_factory=lambda: MemoryOrchestrator,
+        default=None,
     )
 
 
@@ -131,6 +131,7 @@ class SystemContext(BaseDataFlowFacilitatorObject):
         )
         # TODO(alice) Apply overlay
         if self.config.overlay not in (None, APPLY_INSTALLED_OVERLAYS):
+            print(self.config.overlay)
             breakpoint()
             raise NotImplementedError(
                 "Application of overlays within SystemContext class entry not yet supported"
diff --git a/dffml/high_level/dataflow.py b/dffml/high_level/dataflow.py
index d180b5c302..d595ae1cb4 100644
--- a/dffml/high_level/dataflow.py
+++ b/dffml/high_level/dataflow.py
@@ -206,12 +206,25 @@ async def run(
             # the of the one that got passed in and the overlay.
             if inspect.isclass(overlay):
                 overlay = overlay()
+            # TODO Move this into Overlay.load. Create a system context to
+            # execute the overlay if it is not already.
+            known_overlay_types = (DataFlow, SystemContext)
+            if not isinstance(overlay, known_overlay_types):
+                raise NotImplementedError(f"{overlay} is not a known type {known_overlay_types}")
+            if isinstance(overlay, DataFlow):
+                overlay = SystemContext(
+                    upstream=overlay,
+                )
             # TODO(alice) overlay.deployment("native.python.overlay.apply")
             apply_overlay = overlay.deployment()
             async for _ctx, result in apply_overlay(
                 dataflow=dataflow,
             ):
+                print("FEEDFACE", _ctx, result)
+                breakpoint()
+                return
                 continue
+
                 # TODO
                 resultant_system_context = SystemContext(
                     upstream=result["overlays_merged"], overlay=None,
diff --git a/dffml/overlay/overlay.py b/dffml/overlay/overlay.py
index 13a50d9c10..0a01d38de9 100644
--- a/dffml/overlay/overlay.py
+++ b/dffml/overlay/overlay.py
@@ -124,7 +124,7 @@ DFFML_MAIN_PACKAGE_OVERLAY = DataFlow(
             stage=Stage.OUTPUT,
             inputs={
                 "merged": DataFlowAfterOverlaysMerged,
-                "dataflow_we_are_applying_overlays_to_by_running_overlay_dataflow_and_passing_as_an_input": DataFlowWeAreApplyingOverlaysToByRunningOverlayDataflowAndPassingAsAnInput,
+                "upstream": DataFlowWeAreApplyingOverlaysToByRunningOverlayDataflowAndPassingAsAnInput,
             },
             outputs={"overlayed": DataFlowAfterOverlaysApplied,},
             multi_output=False,
@@ -208,15 +208,12 @@ merge_implementations(
 DFFML_OVERLAYS_INSTALLED.update(auto_flow=True)
 
 # Create Class for calling operations within the System Context as methods
-DFFMLOverlaysInstalled = SystemContext.subclass(
-    "DFFMLOverlaysInstalled",
-    {
-        "upstream": {"default_factory": lambda: DFFML_OVERLAYS_INSTALLED},
-        # TODO(alice) We'll need to make sure we have code to instantiate and
-        # instance of a class if only a class is given an not an instance.
-        "overlay": {"default_factory": lambda: None},
-        "orchestrator": {"default_factory": lambda: MemoryOrchestrator()},
-    },
+DFFMLOverlaysInstalled = SystemContext(
+    upstream=DFFML_OVERLAYS_INSTALLED,
+    # TODO(alice) We'll need to make sure we have code to instantiate and
+    # instance of a class if only a class is given an not an instance.
+    overlay=None,
+    orchestrator=MemoryOrchestrator(),
 )
 
 # Callee
diff --git a/entities/alice/alice/please/contribute/recommended_community_standards/alice/operations/github/issue.py b/entities/alice/alice/please/contribute/recommended_community_standards/alice/operations/github/issue.py
index 46d20c8c85..fff5d4928b 100644
--- a/entities/alice/alice/please/contribute/recommended_community_standards/alice/operations/github/issue.py
+++ b/entities/alice/alice/please/contribute/recommended_community_standards/alice/operations/github/issue.py
@@ -18,6 +18,14 @@ from ....recommended_community_standards import AliceGitRepo, AlicePleaseContrib
 from ....dffml.operations.git.contribute import AlicePleaseContributeRecommendedCommunityStandardsOverlayGit
 
 
+GitHubIssue = NewType("GitHubIssue", str)
+
+
+@dataclasses.dataclass
+class RecommendedCommunityStandardContribution:
+    path: pathlib.Path
+    issue: GitHubIssue
+
 
 class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:
     """
@@ -39,6 +47,7 @@ class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:
     MetaIssueTitle = NewType("MetaIssueTitle", str)
     MetaIssueBody = NewType("MetaIssueBody", str)
 
+    # TODO This should only be run if there is a need for a README
     # body: Optional['ContributingIssueBody'] = "References:\n- https://docs.github.com/articles/setting-guidelines-for-repository-contributors/",
     async def readme_issue(
         self,
@@ -79,13 +88,40 @@ class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:
             """
         ).lstrip()
 
-    # TODO(alice) There is a bug with Optional which can be revield by use here
+
     @staticmethod
+    async def readme_contribution(
+        issue: "ReadmeIssue",
+        path: AlicePleaseContributeRecommendedCommunityStandards.ReadmePath,
+    ) -> RecommendedCommunityStandardContribution:
+        return RecommendedCommunityStandardContribution(
+            path=path,
+            issue=issue,
+        )
+
+
+    """
+    @dffml.op(
+        stage=dffml.Stage.OUTPUT,
+    )
+    async def collect_recommended_community_standard_contributions(
+        self,
+    ) -> List[RecommendedCommunityStandardContribution]:
+        async with self.octx.ictx.definitions(self.ctx) as od:
+            return [item async for item in od.inputs(RecommendedCommunityStandardContribution)]
+    """
+
+
+    # TODO(alice) There is a bug with Optional which can be revield by use here
     def meta_issue_body(
         repo: AliceGitRepo,
         base: AlicePleaseContributeRecommendedCommunityStandardsOverlayGit.BaseBranch,
-        readme_path: AlicePleaseContributeRecommendedCommunityStandards.ReadmePath,
-        readme_issue: ReadmeIssue,
+        # recommended_community_standard_contributions: List[RecommendedCommunityStandardContribution],
+        # TODO On @op inspect paramter if Collect is found on an input, wrap the
+        # operation in a subflow and add a generic version of
+        # collect_recommended_community_standard_contributions to the flow as an
+        # autostart or triggered via auto start operation.
+        # recommended_community_standard_contributions: Collect[List[RecommendedCommunityStandardContribution]],
     ) -> "MetaIssueBody":
         """
         >>> AlicePleaseContributeRecommendedCommunityStandardsGitHubIssueOverlay.meta_issue_body(
@@ -98,6 +134,7 @@ class AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:
         - [] [License](https://github.com/intel/dffml/blob/main/LICENSE)
         - [] Security
         """
+        readme_issue, readme_path = recommended_community_standard_contributions[0]
         return "\n".join(
             [
                 "- ["
```