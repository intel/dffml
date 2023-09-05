## 2022-07-28 @pdxjohnny Engineering Logs

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
  - [ ] Overlay to `alice shouldi contribute` to create git repos when found from forks of PyPi packages
    - [ ] Associated tutorial
      - [ ] Linked from `README`
  - [ ] Finish out `alice please contribute recommended community standards`
        dynamic opimp for meta issue body creation
    - [ ] Associated tutorial
      - [ ] Linked from `README` and `CONTRIBUTING`
  - [ ] Software Analysis Trinity diagram showing Human Intent, Static Analysis, and Dynamic Analysis to represent the soul of the software / entity and the process taken to improve it.
    - [SoftwareAnalysisTrinity.drawio.xml](https://github.com/intel/dffml/files/9190063/SoftwareAnalysisTrinity.drawio.xml.txt)
- Noticed that we have an issue with adding new files and locking. The current
  lock is on the `git_repository/GitRepoSpec`.
  - We then convert to `AliceGitRepo`, at which point anything take `AliceGitRepo`
  - alice: please: contribute: recommended community standards: Refactoring into overlays associated with each file contributed
    - Completed in 1a71dbe3ab3743430ce2783f4210a6cd807c36a1

### 43

```
(Pdb) custom_run_dataflow_ctx.config.dataflow.seed.append(dffml.Input(value=repo, definition=definition, origin=('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme', 'result')))
(Pdb) custom_run_dataflow_ctx.config.dataflow.seed
[Input(value=origin, definition=writable.github.remote.origin), Input(value=master, definition=repo.git.base.branch), Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-hxnacg5_', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)]
```

- Attempting to figure out why an operation is not being called
  - `contribute_readme_md` should be getting `base`, but is not.

```
{'_': {ReadmeGitRepo: [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)],
       ReadmeIssue: [Input(value=https://github.com/pdxjohnny/testaaaa/issues/108, definition=ReadmeIssue)],
       ReadmePath: [Input(value=/tmp/dffml-feature-git-68ghk7vd/README.md, definition=ReadmePath)],
       github.pr.body: [Input(value=Closes: https://github.com/pdxjohnny/testaaaa/issues/108, definition=github.pr.body)],
       repo.git.base.branch: [Input(value=master, definition=repo.git.base.branch)],
       repo.readme.git.commit.message: [Input(value=Recommended Community Standard: README

Closes: https://github.com/pdxjohnny/testaaaa/issues/108
, definition=repo.readme.git.commit.message)],
       writable.github.remote.origin: [Input(value=origin, definition=writable.github.remote.origin)]},
 'alternate_definitions': [],
 'by_origin': {('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch', 'result'): [Input(value=master, definition=repo.git.base.branch)],
               ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGitHub:github_owns_remote', 'result'): [Input(value=origin, definition=writable.github.remote.origin)],
               ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme', 'result'): [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)],
               ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:create_readme_file_if_not_exists', 'result'): [Input(value=/tmp/dffml-feature-git-68ghk7vd/README.md, definition=ReadmePath)],
               ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_commit_message', 'result'): [Input(value=Recommended Community Standard: README

Closes: https://github.com/pdxjohnny/testaaaa/issues/108
, definition=repo.readme.git.commit.message)],
               ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_issue', 'result'): [Input(value=https://github.com/pdxjohnny/testaaaa/issues/108, definition=ReadmeIssue)],
               ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_pr_body', 'result'): [Input(value=Closes: https://github.com/pdxjohnny/testaaaa/issues/108, definition=github.pr.body)]},
 'check_for_default_value': [repo.git.base.branch],
 'contexts': [MemoryInputNetworkContextEntry(ctx=Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo), definitions={ReadmeGitRepo: [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)], writable.github.remote.origin: [Input(value=origin, definition=writable.github.remote.origin)], repo.git.base.branch: [Input(value=master, definition=repo.git.base.branch)], ReadmePath: [Input(value=/tmp/dffml-feature-git-68ghk7vd/README.md, definition=ReadmePath)], ReadmeIssue: [Input(value=https://github.com/pdxjohnny/testaaaa/issues/108, definition=ReadmeIssue)], repo.readme.git.commit.message: [Input(value=Recommended Community Standard: README

Closes: https://github.com/pdxjohnny/testaaaa/issues/108
, definition=repo.readme.git.commit.message)], github.pr.body: [Input(value=Closes: https://github.com/pdxjohnny/testaaaa/issues/108, definition=github.pr.body)]}, by_origin={('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme', 'result'): [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)], ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGitHub:github_owns_remote', 'result'): [Input(value=origin, definition=writable.github.remote.origin)], ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch', 'result'): [Input(value=master, definition=repo.git.base.branch)], ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:create_readme_file_if_not_exists', 'result'): [Input(value=/tmp/dffml-feature-git-68ghk7vd/README.md, definition=ReadmePath)], ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_issue', 'result'): [Input(value=https://github.com/pdxjohnny/testaaaa/issues/108, definition=ReadmeIssue)], ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_commit_message', 'result'): [Input(value=Recommended Community Standard: README

Closes: https://github.com/pdxjohnny/testaaaa/issues/108
, definition=repo.readme.git.commit.message)], ('alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_pr_body', 'result'): [Input(value=Closes: https://github.com/pdxjohnny/testaaaa/issues/108, definition=github.pr.body)]})],
 'ctx': Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo),
 'dataflow': <dffml.df.types.DataFlow object at 0x7f177ec3b7f0>,
 'definition': repo.git.base.branch,
 'gather': {'base': [],
            'repo': [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)]},
 'handle_string': "Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', "
                  "URL='https://github.com/pdxjohnny/testaaaa'), "
                  'definition=ReadmeGitRepo)',
 'input_flow': InputFlow(inputs={'repo': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme': 'result'}], 'base': ['seed'], 'commit_message': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_commit_message': 'result'}]}, conditions=[]),
 'input_name': 'base',
 'input_source': 'seed',
 'input_sources': ['seed'],
 'item': Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo),
 'operation': Operation(name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:contribute_readme_md', inputs={'repo': ReadmeGitRepo, 'base': repo.git.base.branch, 'commit_message': repo.readme.git.commit.message}, outputs={'result': repo.readme.git.branch}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:contribute_readme_md', validator=False, retry=0),
 'origin': 'seed',
 'origins': ['seed'],
 'pprint': <function pprint at 0x7f1782d94670>,
 'rctx': <dffml.df.memory.MemoryRedundancyCheckerContext object at 0x7f177ec5e220>,
 'self': <dffml.df.memory.MemoryInputNetworkContext object at 0x7f177ec3ba30>}
> /home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py(788)gather_inputs()
-> return
(Pdb) gather
{'repo': [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)], 'base': []}
(Pdb) operation.inputs
{'repo': ReadmeGitRepo, 'base': repo.git.base.branch, 'commit_message': repo.readme.git.commit.message}
(Pdb) self.ctxhd.keys()
dict_keys(["Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)"])
(Pdb) from pprint import pprint
(Pdb) pprint(inputs.definitions)
{ReadmeGitRepo: [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)],
 ReadmeIssue: [Input(value=https://github.com/pdxjohnny/testaaaa/issues/108, definition=ReadmeIssue)],
 ReadmePath: [Input(value=/tmp/dffml-feature-git-68ghk7vd/README.md, definition=ReadmePath)],
 github.pr.body: [Input(value=Closes: https://github.com/pdxjohnny/testaaaa/issues/108, definition=github.pr.body)],
 repo.git.base.branch: [Input(value=master, definition=repo.git.base.branch)],
 repo.readme.git.commit.message: [Input(value=Recommended Community Standard: README

Closes: https://github.com/pdxjohnny/testaaaa/issues/108
, definition=repo.readme.git.commit.message)],
 writable.github.remote.origin: [Input(value=origin, definition=writable.github.remote.origin)]}
(Pdb) gather
{'repo': [Input(value=GitRepoSpec(directory='/tmp/dffml-feature-git-68ghk7vd', URL='https://github.com/pdxjohnny/testaaaa'), definition=ReadmeGitRepo)], 'base': []}
(Pdb) operation.inputs
{'repo': ReadmeGitRepo, 'base': repo.git.base.branch, 'commit_message': repo.readme.git.commit.message}
```

- Suspect discarded because of mismatched origin, if not that, will check definition
  - Found out that it was seed vs. output origin mismatch
  - Found out that BaseBranch comes from OverlayGit
  - Registered OverlayGit as an overlay of OverlayReadme to that it's definitions get loaded
    - This way `auto_flow` will make the expected origin the output from OverlayGit operations
      rather than seed (the default when no matching outputs are seen on DataFlow init).
  - We found it created an infinite loop
    - Will try reusing redundancy checker, that seems to be doing well
- https://github.com/intel/dffml/issues/1408
- Now debugging why `readme_pr` not called, OverlayGit definitions were seen earlier
  on subflow start to be present, must be something else.
  - The logs tell us that alice_contribute_readme is returning `None`, which means
    that the downstream operation is not called, since None means no return value
    in this case.

```
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme Outputs: None
```

- Future
  - `run_custom` Optionally support forward subflow
- TODO
  - [ ] Set definition proprety `AliceGitRepo.lock` to `True`


### 44

- Found out that util: subprocess: run command events: Do not return after yield of stdout/err
  - Fixed in b6eea6ed4549f9e7a89aab6306a51213b2bf36c9

```console
$ (for i in $(echo determin_base_branch readme_pr_body contribute_readme_md github_owns_remote alice_contribute_readme); do grep -rn "${i} Outputs" .output/2022-07-28-14-11.txt; done) | sort | uniq | sort
354:DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGitHub:github_owns_remote Outputs: {'result': 'origin'}
361:DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch Outputs: {'result': 'master'}
450:DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_pr_body Outputs: {'result': 'Closes: https://github.com/pdxjohnny/testaaaa/issues/188'}
472:DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:contribute_readme_md Outputs: {'result': 'alice-contribute-recommended-community-standards-readme'}
479:DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme Outputs: None
```

```
(Pdb)
DEBUG:dffml.MemoryOperationImplementationNetworkContext:alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:contribute_readme_md Outputs: {'result': 'alice-contribute-recommended-community-standards-readme'}
(Pdb) pprint(readme_dataflow.flow['alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_pr'].inputs)
{'base': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayGit:determin_base_branch': 'result'}],
 'body': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_pr_body': 'result'}],
 'head': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:contribute_readme_md': 'result'}],
 'origin': ['seed'],
 'repo': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:alice_contribute_readme': 'result'}],
 'title': [{'alice.please.contribute.recommended_community_standards.recommended_community_standards.OverlayREADME:readme_pr_title': 'result'}]}
```

- origin is set to seed
  - `'origin': ['seed']` was there because `OverlayGitHub.github_owns_remote` is not in the flow
  - We forgot add it to `entry_points.txt`, added

```console
$ dffml service dev export alice.cli:AlicePleaseContributeCLIDataFlow | tee alice.please.contribute.recommended_community_standards.json
$ (echo -e 'HTTP/1.0 200 OK\n' && dffml dataflow diagram -shortname alice.please.contribute.recommended_community_standards.json) | nc -Nlp 9999;
```

- Opens
  - `guessed_repo_string_means_no_git_branch_given` is feeding `git_repo_default_branch` but `dffml dataflow diagram` just have a bug because it's not showing the connection.

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
subgraph 43a22312a3d4f5c995c54c5196acc50a[create_meta_issue]
style 43a22312a3d4f5c995c54c5196acc50a fill:#fff4de,stroke:#cece71
d2345f23e5ef9f54c591c4a687c24575[create_meta_issue]
1d79010ee1550f057c531130814c40b9(body)
1d79010ee1550f057c531130814c40b9 --> d2345f23e5ef9f54c591c4a687c24575
712d4318e59bd2dc629f0ddebb257ca3(repo)
712d4318e59bd2dc629f0ddebb257ca3 --> d2345f23e5ef9f54c591c4a687c24575
38a94f1c2162803f571489d707d61021(title)
38a94f1c2162803f571489d707d61021 --> d2345f23e5ef9f54c591c4a687c24575
2b22b4998ac3e6a64d82e0147e71ee1b(result)
d2345f23e5ef9f54c591c4a687c24575 --> 2b22b4998ac3e6a64d82e0147e71ee1b
end
subgraph f77af509c413b86b6cd7e107cc623c73[meta_issue_body]
style f77af509c413b86b6cd7e107cc623c73 fill:#fff4de,stroke:#cece71
69a9852570720a3d35cb9dd52a281f71[meta_issue_body]
480d1cc478d23858e92d61225349b674(base)
480d1cc478d23858e92d61225349b674 --> 69a9852570720a3d35cb9dd52a281f71
37035ea5a06a282bdc1e1de24090a36d(readme_issue)
37035ea5a06a282bdc1e1de24090a36d --> 69a9852570720a3d35cb9dd52a281f71
fdf0dbb8ca47ee9022b3daeb8c7df9c0(readme_path)
fdf0dbb8ca47ee9022b3daeb8c7df9c0 --> 69a9852570720a3d35cb9dd52a281f71
428ca84f627c695362652cc7531fc27b(repo)
428ca84f627c695362652cc7531fc27b --> 69a9852570720a3d35cb9dd52a281f71
0cd9eb1ffb3c56d2b0a4359f800b1f20(result)
69a9852570720a3d35cb9dd52a281f71 --> 0cd9eb1ffb3c56d2b0a4359f800b1f20
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
0cd9eb1ffb3c56d2b0a4359f800b1f20 --> 1d79010ee1550f057c531130814c40b9
dd5aab190ce844673819298c5b8fde76 --> 712d4318e59bd2dc629f0ddebb257ca3
9b92d5a346885079a2821c4d27cb5174 --> 712d4318e59bd2dc629f0ddebb257ca3
e7ad3469d98c3bd160363dbc47e2d741(seed<br>MetaIssueTitle)
e7ad3469d98c3bd160363dbc47e2d741 --> 38a94f1c2162803f571489d707d61021
150204cd2d5a921deb53c312418379a1 --> 480d1cc478d23858e92d61225349b674
1d2360c9da18fac0b6ec142df8f3fbda --> 37035ea5a06a282bdc1e1de24090a36d
5cc65e17d40e6a7223c1504f1c4b0d2a --> fdf0dbb8ca47ee9022b3daeb8c7df9c0
dd5aab190ce844673819298c5b8fde76 --> 428ca84f627c695362652cc7531fc27b
9b92d5a346885079a2821c4d27cb5174 --> 428ca84f627c695362652cc7531fc27b
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

- As of f8619a6362251d04929f4bfa395882b3257a3776 it works without meta issue
  creation: https://github.com/pdxjohnny/testaaaa/pull/193

# 45

```console
$ gif-for-cli --rows $(tput lines) --cols $(tput cols) --export=/mnt/c/Users/Johnny/Downloads/alice-search-alices-adventures-in-wonderland-1.gif "Alice's Adventures in Wonderland"
```

```console
$ watch -n 0.2 'grep FEEDFACE .output/$(ls .output/ | tail -n 1) | sed -e "s/alice.please.contribute.recommended_community_standards.recommended_community_standards.//g" | grep -i repo'
```