## 2022-07-26 @pdxjohnny Engineering Logs

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

![Software Analysis Trinity drawio](https://user-images.githubusercontent.com/5950433/181014158-4187950e-d0a4-4d7d-973b-dc414320e64f.svg)

- Update current overlays to have lock taken on `AliceGitRepo` and then subflows with `ReadmeGitRepo` and `ContributingGitRepo`.
  - This way the parent flow locks and they don't have to worry about loosing the lock between operations.

```console
$ git grep -C 22 run_custom
alice/please/contribute/recommended_community_standards/cli.py-    async def cli_run_on_repo(self, repo: "CLIRunOnRepo"):
alice/please/contribute/recommended_community_standards/cli.py-        # TODO Similar to Expand being an alias of Union
alice/please/contribute/recommended_community_standards/cli.py-        #
alice/please/contribute/recommended_community_standards/cli.py-        # async def cli_run_on_repo(self, repo: 'CLIRunOnRepo') -> SystemContext[StringInputSetContext[AliceGitRepo]]:
alice/please/contribute/recommended_community_standards/cli.py-        #     return repo
alice/please/contribute/recommended_community_standards/cli.py-        #
alice/please/contribute/recommended_community_standards/cli.py-        # Or ideally at class scope
alice/please/contribute/recommended_community_standards/cli.py-        #
alice/please/contribute/recommended_community_standards/cli.py-        # 'CLIRunOnRepo' -> SystemContext[StringInputSetContext[AliceGitRepo]]
alice/please/contribute/recommended_community_standards/cli.py-        async with self.parent.__class__(self.parent.config) as custom_run_dataflow:
alice/please/contribute/recommended_community_standards/cli.py-            async with custom_run_dataflow(
alice/please/contribute/recommended_community_standards/cli.py-                self.ctx, self.octx
alice/please/contribute/recommended_community_standards/cli.py-            ) as custom_run_dataflow_ctx:
alice/please/contribute/recommended_community_standards/cli.py-                # This is the type cast
alice/please/contribute/recommended_community_standards/cli.py-                custom_run_dataflow.op = self.parent.op._replace(
alice/please/contribute/recommended_community_standards/cli.py-                    inputs={
alice/please/contribute/recommended_community_standards/cli.py-                        "repo": AlicePleaseContributeRecommendedCommunityStandards.RepoString
alice/please/contribute/recommended_community_standards/cli.py-                    }
alice/please/contribute/recommended_community_standards/cli.py-                )
alice/please/contribute/recommended_community_standards/cli.py-                # Set the dataflow to be the same flow
alice/please/contribute/recommended_community_standards/cli.py-                # TODO Reuse ictx? Is that applicable?
alice/please/contribute/recommended_community_standards/cli.py-                custom_run_dataflow.config.dataflow = self.octx.config.dataflow
alice/please/contribute/recommended_community_standards/cli.py:                await dffml.run_dataflow.run_custom(
alice/please/contribute/recommended_community_standards/cli.py-                    custom_run_dataflow_ctx, {"repo": repo},
alice/please/contribute/recommended_community_standards/cli.py-                )
```