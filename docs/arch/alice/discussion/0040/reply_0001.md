- Issues with below state (6bd1c1aca0031f92d4617e48c5d15e36be10f78b)
  - `AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_issue`
    - Needs to go to `AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body.inputs.readme_issue`
  - `AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest:readme_pr`
    - Should take body built using `AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_issue` output result URL to issue

```mermaid
graph TD
subgraph a759a07029077edc5c37fea0326fa281[Processing Stage]
style a759a07029077edc5c37fea0326fa281 fill:#afd388b5,stroke:#a4ca7a
subgraph efa51e6b3ce9fb2ad65cec49ec665eb0[alice.cli.AlicePleaseContributeRecommendedCommunityStandards:create_readme_file_if_not_exists]
style efa51e6b3ce9fb2ad65cec49ec665eb0 fill:#fff4de,stroke:#cece71
9760336ebe9515d00f159c552ad08a5e[alice.cli.AlicePleaseContributeRecommendedCommunityStandards:create_readme_file_if_not_exists]
9a9667eb3423808c842ecd1df7be9ee5(readme_contents)
9a9667eb3423808c842ecd1df7be9ee5 --> 9760336ebe9515d00f159c552ad08a5e
822f93e7cb5f6173da8dcb240aad3c12(repo)
822f93e7cb5f6173da8dcb240aad3c12 --> 9760336ebe9515d00f159c552ad08a5e
cd82a27f3620b31ddb229a5e4f24a4b8(result)
9760336ebe9515d00f159c552ad08a5e --> cd82a27f3620b31ddb229a5e4f24a4b8
end
subgraph 64c87e41605343a281c778ad0d5019f0[alice.cli.AlicePleaseContributeRecommendedCommunityStandards:guess_repo_string_is_directory]
style 64c87e41605343a281c778ad0d5019f0 fill:#fff4de,stroke:#cece71
3b9d71c43fd0bdd66060f6fb3c28224f[alice.cli.AlicePleaseContributeRecommendedCommunityStandards:guess_repo_string_is_directory]
5cc3fb2b31bb4731e38ae38da552c1b3(repo_string)
5cc3fb2b31bb4731e38ae38da552c1b3 --> 3b9d71c43fd0bdd66060f6fb3c28224f
93da91c143d2ee719207bd8642ec67fb(result)
3b9d71c43fd0bdd66060f6fb3c28224f --> 93da91c143d2ee719207bd8642ec67fb
end
subgraph 642347776f960d0856f659de7aedfa16[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayAliceOperationsGit:git_repo_to_alice_git_repo]
style 642347776f960d0856f659de7aedfa16 fill:#fff4de,stroke:#cece71
a6e056055014b276f67aaf86a9c4ba7b[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayAliceOperationsGit:git_repo_to_alice_git_repo]
93d047c136ba3cb04eaa5a02cf55b7ad(repo)
93d047c136ba3cb04eaa5a02cf55b7ad --> a6e056055014b276f67aaf86a9c4ba7b
a76d82d2cc58665bd2ec3d4a7969004e(result)
a6e056055014b276f67aaf86a9c4ba7b --> a76d82d2cc58665bd2ec3d4a7969004e
end
subgraph 6b657df72c0269e835e3e735ecc4521e[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_has_repos]
style 6b657df72c0269e835e3e735ecc4521e fill:#fff4de,stroke:#cece71
b1e3576964f11f31e1f3f916dde29fe4[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_has_repos]
0961ef0167e6a9c90cb8fb3075902bc1(cmd)
0961ef0167e6a9c90cb8fb3075902bc1 --> b1e3576964f11f31e1f3f916dde29fe4
830d76af1097e94bfdba380285f0de47(wanted)
830d76af1097e94bfdba380285f0de47 --> b1e3576964f11f31e1f3f916dde29fe4
2f1fff87c365ccf897ad9fa9b51651f5(result)
b1e3576964f11f31e1f3f916dde29fe4 --> 2f1fff87c365ccf897ad9fa9b51651f5
end
subgraph 02c8ac697f1e6ffd72c166dc80439f1e[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_is_asking_for_recommended_community_standards]
style 02c8ac697f1e6ffd72c166dc80439f1e fill:#fff4de,stroke:#cece71
3e0e4a40c3015a3f1b21a02603b25a9a[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_is_asking_for_recommended_community_standards]
d7a71c842f1ca874a013a2672afa9813(cmd)
d7a71c842f1ca874a013a2672afa9813 --> 3e0e4a40c3015a3f1b21a02603b25a9a
0b253e3fa412f6b0a7bd06cab08fc818(result)
3e0e4a40c3015a3f1b21a02603b25a9a --> 0b253e3fa412f6b0a7bd06cab08fc818
end
subgraph c20005853bfb169d35e6707ef2ebe08b[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_is_meant_on_this_repo]
style c20005853bfb169d35e6707ef2ebe08b fill:#fff4de,stroke:#cece71
83fb945001548dd14d1f45703474dce4[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_is_meant_on_this_repo]
b8293b09b395db3874949b6bc9350fad(cmd)
b8293b09b395db3874949b6bc9350fad --> 83fb945001548dd14d1f45703474dce4
b196a395ef19d4c1c50673fa6e641b76(wanted)
b196a395ef19d4c1c50673fa6e641b76 --> 83fb945001548dd14d1f45703474dce4
86e1297795fe041e459492298063139b(result)
83fb945001548dd14d1f45703474dce4 --> 86e1297795fe041e459492298063139b
end
subgraph a316b05aa4579172111db540b3fcc638[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_run_on_repo]
style a316b05aa4579172111db540b3fcc638 fill:#fff4de,stroke:#cece71
a3c07e11685f8f31609cabb6ddc687bf[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_run_on_repo]
fee30a08dd99a5b6f0ccb4ae08af34d9(repo)
fee30a08dd99a5b6f0ccb4ae08af34d9 --> a3c07e11685f8f31609cabb6ddc687bf
end
subgraph 231bfd9b60e68e2add191f4bc3908586[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:contribute_readme_md]
style 231bfd9b60e68e2add191f4bc3908586 fill:#fff4de,stroke:#cece71
b5860d2f7255d256566097f666a75a4c[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:contribute_readme_md]
3dbc4878c5ebc8dd20bd9be09260fad8(base)
3dbc4878c5ebc8dd20bd9be09260fad8 --> b5860d2f7255d256566097f666a75a4c
c81256045645ef3cb67ed070f6034db9(commit_message)
c81256045645ef3cb67ed070f6034db9 --> b5860d2f7255d256566097f666a75a4c
d0aa0537b79bf8600c2e5942aa73e75a(repo)
d0aa0537b79bf8600c2e5942aa73e75a --> b5860d2f7255d256566097f666a75a4c
30ac8ac9e7295721a0587b15a98c4fdf(result)
b5860d2f7255d256566097f666a75a4c --> 30ac8ac9e7295721a0587b15a98c4fdf
end
subgraph 991971fd925f48ab84936c53c2e7c6b1[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:determin_base_branch]
style 991971fd925f48ab84936c53c2e7c6b1 fill:#fff4de,stroke:#cece71
39604f2a099b470fa14e075d9fe480bb[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:determin_base_branch]
35b46df24b1604a456bd487c41525426(default_branch)
35b46df24b1604a456bd487c41525426 --> 39604f2a099b470fa14e075d9fe480bb
24a1136d076c239f151da2f4ca3c7825(result)
39604f2a099b470fa14e075d9fe480bb --> 24a1136d076c239f151da2f4ca3c7825
end
subgraph f0bbe583b4285223fb8fad86047a66f9[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:create_meta_issue]
style f0bbe583b4285223fb8fad86047a66f9 fill:#fff4de,stroke:#cece71
9223cba0aac5bb81f432a03a6d5feb29[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:create_meta_issue]
6af177f56b61b3397a503c3e54e84d8a(body)
6af177f56b61b3397a503c3e54e84d8a --> 9223cba0aac5bb81f432a03a6d5feb29
205ef79a6639c6d770a710067db57cc2(repo)
205ef79a6639c6d770a710067db57cc2 --> 9223cba0aac5bb81f432a03a6d5feb29
7500502ec1ac30c0f496c2b45737da90(title)
7500502ec1ac30c0f496c2b45737da90 --> 9223cba0aac5bb81f432a03a6d5feb29
1f6ae7539e8b0fb7cc58ef97100be467(result)
9223cba0aac5bb81f432a03a6d5feb29 --> 1f6ae7539e8b0fb7cc58ef97100be467
end
subgraph 6e72e27dda9acc50fe25775cbe4c171d[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body]
style 6e72e27dda9acc50fe25775cbe4c171d fill:#fff4de,stroke:#cece71
735041fe58840530e39ede1e7ecd06e0[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body]
8b9ef3ddda41827e341041ad9eaaa8c0(base)
8b9ef3ddda41827e341041ad9eaaa8c0 --> 735041fe58840530e39ede1e7ecd06e0
b5c3f99145842917dffb001e8a0f5ac9(readme_issue)
b5c3f99145842917dffb001e8a0f5ac9 --> 735041fe58840530e39ede1e7ecd06e0
d88f700df593fe6be5a459a072898e61(readme_path)
d88f700df593fe6be5a459a072898e61 --> 735041fe58840530e39ede1e7ecd06e0
27aedf8b5be461202b6c14b312c1f824(repo)
27aedf8b5be461202b6c14b312c1f824 --> 735041fe58840530e39ede1e7ecd06e0
2965094fb920d11e73dd622c881e2d09(result)
735041fe58840530e39ede1e7ecd06e0 --> 2965094fb920d11e73dd622c881e2d09
end
subgraph 08060156e4e9c8b71ace2b19530cac1f[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_commit_message]
style 08060156e4e9c8b71ace2b19530cac1f fill:#fff4de,stroke:#cece71
4f647ec6a92d622243eac92fcad91c17[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_commit_message]
7eab9107cbb22d2eadc5962b8ecb74c7(issue_url)
7eab9107cbb22d2eadc5962b8ecb74c7 --> 4f647ec6a92d622243eac92fcad91c17
a8c4a2848aaaa5e4596765f016da33d0(result)
4f647ec6a92d622243eac92fcad91c17 --> a8c4a2848aaaa5e4596765f016da33d0
end
subgraph 91e845c504cd89a25f37f1eeb95343a9[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_issue]
style 91e845c504cd89a25f37f1eeb95343a9 fill:#fff4de,stroke:#cece71
3620522a14263c8b131a2b6dac8bbb9b[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_issue]
3aecb32635b14d6ec4725055d3205687(body)
3aecb32635b14d6ec4725055d3205687 --> 3620522a14263c8b131a2b6dac8bbb9b
1b78d200cc45b9497d7a538fa38938af(repo)
1b78d200cc45b9497d7a538fa38938af --> 3620522a14263c8b131a2b6dac8bbb9b
0cf09dbc0b5bd4ec73d3fdd38bb54c3e(title)
0cf09dbc0b5bd4ec73d3fdd38bb54c3e --> 3620522a14263c8b131a2b6dac8bbb9b
3552fba49df8542048552d4c1adaf862(result)
3620522a14263c8b131a2b6dac8bbb9b --> 3552fba49df8542048552d4c1adaf862
end
subgraph f49cf4e7472c14775be7d8848b8057c4[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest:readme_pr]
style f49cf4e7472c14775be7d8848b8057c4 fill:#fff4de,stroke:#cece71
aea484b3ef6be5b49c1f7220fe2d16c4[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubPullRequest:readme_pr]
0790bfcf818aa9958a7924272c0ea10d(base)
0790bfcf818aa9958a7924272c0ea10d --> aea484b3ef6be5b49c1f7220fe2d16c4
6f08eeac5dc9434f80829d548ee1a29b(head)
6f08eeac5dc9434f80829d548ee1a29b --> aea484b3ef6be5b49c1f7220fe2d16c4
b5ef7004cb12ebd34c891050b7c53e20(repo)
b5ef7004cb12ebd34c891050b7c53e20 --> aea484b3ef6be5b49c1f7220fe2d16c4
7be6f6090dc80588254ff6836315189a(result)
aea484b3ef6be5b49c1f7220fe2d16c4 --> 7be6f6090dc80588254ff6836315189a
end
subgraph 268635da25617e0034b56e72f4b24e37[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:create_branch_if_none_exists]
style 268635da25617e0034b56e72f4b24e37 fill:#fff4de,stroke:#cece71
141e16f8584892cc8e6449f4c4ccb5f9[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:create_branch_if_none_exists]
c2a16f0c5632ec0a12626c6f65f6bd43(name)
c2a16f0c5632ec0a12626c6f65f6bd43 --> 141e16f8584892cc8e6449f4c4ccb5f9
c35eb2cb2de3f227f243a3825074568a(repo)
c35eb2cb2de3f227f243a3825074568a --> 141e16f8584892cc8e6449f4c4ccb5f9
d27352faaf6bab6d9f4d4cfbe381cc7c(result)
141e16f8584892cc8e6449f4c4ccb5f9 --> d27352faaf6bab6d9f4d4cfbe381cc7c
end
subgraph 9c2f7529803e25e7d215c9660df67572[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:guess_repo_string_is_url]
style 9c2f7529803e25e7d215c9660df67572 fill:#fff4de,stroke:#cece71
1e7cc4969c1a1142f4a8a1f222ee8966[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:guess_repo_string_is_url]
93cecf783409bbc954cecd53ccc294f2(repo_string)
93cecf783409bbc954cecd53ccc294f2 --> 1e7cc4969c1a1142f4a8a1f222ee8966
271a24db335549c3a738fbd185e45700(result)
1e7cc4969c1a1142f4a8a1f222ee8966 --> 271a24db335549c3a738fbd185e45700
end
subgraph fb99aca88b7a2db253a8af85b41b1d5d[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:guessed_repo_string_is_operations_git_url]
style fb99aca88b7a2db253a8af85b41b1d5d fill:#fff4de,stroke:#cece71
d66a6ba3daf795fbc106d68368daf882[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:guessed_repo_string_is_operations_git_url]
5c1de086764843eb34b7ac3f08a5b754(repo_url)
5c1de086764843eb34b7ac3f08a5b754 --> d66a6ba3daf795fbc106d68368daf882
b1495b37288052e990c4388f7a285976(result)
d66a6ba3daf795fbc106d68368daf882 --> b1495b37288052e990c4388f7a285976
end
subgraph 7207621873b5274dceb6cbe5b820c495[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:guessed_repo_string_means_no_git_branch_given]
style 7207621873b5274dceb6cbe5b820c495 fill:#fff4de,stroke:#cece71
031f5686c307b9e5fb15a90e546b14a4[alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayOperationsGit:guessed_repo_string_means_no_git_branch_given]
03c75c343da6bc066628aa7fcac47323(repo_url)
03c75c343da6bc066628aa7fcac47323 --> 031f5686c307b9e5fb15a90e546b14a4
9c1f0d548d86f8bdda6abf7a88f53dd5(result)
031f5686c307b9e5fb15a90e546b14a4 --> 9c1f0d548d86f8bdda6abf7a88f53dd5
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
d2708225c1f4c95d613a2645a17a5bc0(seed<br>repo.directory.readme.contents)
d2708225c1f4c95d613a2645a17a5bc0 --> 9a9667eb3423808c842ecd1df7be9ee5
93da91c143d2ee719207bd8642ec67fb --> 822f93e7cb5f6173da8dcb240aad3c12
a76d82d2cc58665bd2ec3d4a7969004e --> 822f93e7cb5f6173da8dcb240aad3c12
6fefd04e5dceb7b65fe9e1d74b431f54(seed<br>repo.string)
6fefd04e5dceb7b65fe9e1d74b431f54 --> 5cc3fb2b31bb4731e38ae38da552c1b3
4e1d5ea96e050e46ebf95ebc0713d54c --> 93d047c136ba3cb04eaa5a02cf55b7ad
128516cfa09b0383023eab52ee24878a(seed<br>dffml.util.cli.CMD)
128516cfa09b0383023eab52ee24878a --> 0961ef0167e6a9c90cb8fb3075902bc1
0b253e3fa412f6b0a7bd06cab08fc818 --> 830d76af1097e94bfdba380285f0de47
128516cfa09b0383023eab52ee24878a(seed<br>dffml.util.cli.CMD)
128516cfa09b0383023eab52ee24878a --> d7a71c842f1ca874a013a2672afa9813
128516cfa09b0383023eab52ee24878a(seed<br>dffml.util.cli.CMD)
128516cfa09b0383023eab52ee24878a --> b8293b09b395db3874949b6bc9350fad
0b253e3fa412f6b0a7bd06cab08fc818 --> b196a395ef19d4c1c50673fa6e641b76
2f1fff87c365ccf897ad9fa9b51651f5 --> fee30a08dd99a5b6f0ccb4ae08af34d9
86e1297795fe041e459492298063139b --> fee30a08dd99a5b6f0ccb4ae08af34d9
24a1136d076c239f151da2f4ca3c7825 --> 3dbc4878c5ebc8dd20bd9be09260fad8
93da91c143d2ee719207bd8642ec67fb --> d0aa0537b79bf8600c2e5942aa73e75a
a76d82d2cc58665bd2ec3d4a7969004e --> d0aa0537b79bf8600c2e5942aa73e75a
d27352faaf6bab6d9f4d4cfbe381cc7c --> 35b46df24b1604a456bd487c41525426
57651c1bcd24b794dfc8d1794ab556d5 --> 35b46df24b1604a456bd487c41525426
2965094fb920d11e73dd622c881e2d09 --> 6af177f56b61b3397a503c3e54e84d8a
93da91c143d2ee719207bd8642ec67fb --> 205ef79a6639c6d770a710067db57cc2
a76d82d2cc58665bd2ec3d4a7969004e --> 205ef79a6639c6d770a710067db57cc2
e7ad3469d98c3bd160363dbc47e2d741(seed<br>MetaIssueTitle)
e7ad3469d98c3bd160363dbc47e2d741 --> 7500502ec1ac30c0f496c2b45737da90
24a1136d076c239f151da2f4ca3c7825 --> 8b9ef3ddda41827e341041ad9eaaa8c0
cd82a27f3620b31ddb229a5e4f24a4b8 --> d88f700df593fe6be5a459a072898e61
93da91c143d2ee719207bd8642ec67fb --> 27aedf8b5be461202b6c14b312c1f824
a76d82d2cc58665bd2ec3d4a7969004e --> 27aedf8b5be461202b6c14b312c1f824
3552fba49df8542048552d4c1adaf862 --> 7eab9107cbb22d2eadc5962b8ecb74c7
1daacccd02f8117e67ad3cb8686a732c(seed<br>ReadmeIssueBody)
1daacccd02f8117e67ad3cb8686a732c --> 3aecb32635b14d6ec4725055d3205687
93da91c143d2ee719207bd8642ec67fb --> 1b78d200cc45b9497d7a538fa38938af
a76d82d2cc58665bd2ec3d4a7969004e --> 1b78d200cc45b9497d7a538fa38938af
0c1ab2d4bda10e1083557833ae5c5da4(seed<br>ReadmeIssueTitle)
0c1ab2d4bda10e1083557833ae5c5da4 --> 0cf09dbc0b5bd4ec73d3fdd38bb54c3e
24a1136d076c239f151da2f4ca3c7825 --> 0790bfcf818aa9958a7924272c0ea10d
30ac8ac9e7295721a0587b15a98c4fdf --> 6f08eeac5dc9434f80829d548ee1a29b
93da91c143d2ee719207bd8642ec67fb --> b5ef7004cb12ebd34c891050b7c53e20
a76d82d2cc58665bd2ec3d4a7969004e --> b5ef7004cb12ebd34c891050b7c53e20
21ccfd2c550bd853d28581f0b0c9f9fe(seed<br>default.branch.name)
21ccfd2c550bd853d28581f0b0c9f9fe --> c2a16f0c5632ec0a12626c6f65f6bd43
93da91c143d2ee719207bd8642ec67fb --> c35eb2cb2de3f227f243a3825074568a
a76d82d2cc58665bd2ec3d4a7969004e --> c35eb2cb2de3f227f243a3825074568a
6fefd04e5dceb7b65fe9e1d74b431f54(seed<br>repo.string)
6fefd04e5dceb7b65fe9e1d74b431f54 --> 93cecf783409bbc954cecd53ccc294f2
271a24db335549c3a738fbd185e45700 --> 5c1de086764843eb34b7ac3f08a5b754
271a24db335549c3a738fbd185e45700 --> 03c75c343da6bc066628aa7fcac47323
b1495b37288052e990c4388f7a285976 --> 7440e73a8e8f864097f42162b74f2762
b1495b37288052e990c4388f7a285976 --> eed77b9eea541e0c378c67395351099c
a6ed501edbf561fda49a0a0a3ca310f0(seed<br>git_repo_ssh_key)
a6ed501edbf561fda49a0a0a3ca310f0 --> 8b5928cd265dd2c44d67d076f60c8b05
8e39b501b41c5d0e4596318f80a03210 --> 6a44de06a4a3518b939b27c790f6cdce
4e1d5ea96e050e46ebf95ebc0713d54c --> 181f1b33df4d795fbad2911ec7087e86
end
```

```
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: cdbd486a-4c6c-4644-be6b-86a804a28dc2(GitRepoSpec(directory='/tmp/dffml-feature-git-bxee21vb', URL='https://github.com/pdxjohnny/testa')) (now held by Operation(name='alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:contribute_readme_md', inputs={'repo': AliceGitRepo, 'base': repo.git.base.branch, 'commit_message': repo.readme.git.commit.message}, outputs={'result': repo.readme.git.branch}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:contribute_readme_md', validator=False, retry=0))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Stage: PROCESSING: alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:contribute_readme_md
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Inputs: {'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-bxee21vb', URL='https://github.com/pdxjohnny/testa'), 'base': 'main', 'commit_message': 'Recommended Community Standard: Add README'}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Conditions: {}
DEBUG:dffml.MemoryLockNetworkContext:Operation(name='alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body', inputs={'repo': AliceGitRepo, 'base': repo.git.base.branch, 'readme_path': ReadmePath, 'readme_issue': ReadmeIssue}, outputs={'result': MetaIssueBody}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body', validator=False, retry=0) acquiring: cdbd486a-4c6c-4644-be6b-86a804a28dc2(GitRepoSpec(directory='/tmp/dffml-feature-git-bxee21vb', URL='https://github.com/pdxjohnny/testa'))
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: cdbd486a-4c6c-4644-be6b-86a804a28dc2(GitRepoSpec(directory='/tmp/dffml-feature-git-bxee21vb', URL='https://github.com/pdxjohnny/testa')) (now held by Operation(name='alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body', inputs={'repo': AliceGitRepo, 'base': repo.git.base.branch, 'readme_path': ReadmePath, 'readme_issue': ReadmeIssue}, outputs={'result': MetaIssueBody}, stage=<Stage.PROCESSING: 'processing'>, conditions=[], expand=[], instance_name='alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body', validator=False, retry=0))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Stage: PROCESSING: alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:meta_issue_body
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Inputs: {'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-bxee21vb', URL='https://github.com/pdxjohnny/testa'), 'base': 'main', 'readme_path': PosixPath('/tmp/dffml-feature-git-bxee21vb/README.md'), 'readme_issue': None}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Conditions: {}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Outputs: {'result': '- [x] [README](https://github.com/pdxjohnny/testa/blob/main/README.md)'}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:[DISPATCH] alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:create_meta_issue
DEBUG:dffml.MemoryOrchestratorContext:[https://github.com/pdxjohnny/testa]: dispatch operation: alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:create_meta_issue
Traceback (most recent call last):
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1277, in run_dispatch
    outputs = await self.run(
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1242, in run
    return await self.run_no_retry(ctx, octx, operation, inputs)
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1220, in run_no_retry
    outputs = await opctx.run(inputs)
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/base.py", line 546, in run
    result = await func(**inputs)
  File "/home/pdxjohnny/Documents/python/dffml/entities/alice/alice/cli.py", line 217, in contribute_readme_md
    await dffml.run_command(
  File "/home/pdxjohnny/Documents/python/dffml/dffml/util/subprocess.py", line 137, in run_command
    async for _, _ in run_command_events(
  File "/home/pdxjohnny/Documents/python/dffml/dffml/util/subprocess.py", line 82, in run_command_events
    raise RuntimeError(
RuntimeError: ['git', 'checkout', 'main']: error: pathspec 'main' did not match any file(s) known to git


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1277, in run_dispatch
    outputs = await self.run(
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1242, in run
    return await self.run_no_retry(ctx, octx, operation, inputs)
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1220, in run_no_retry
    outputs = await opctx.run(inputs)
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/base.py", line 544, in run
    result = await result
  File "/home/pdxjohnny/Documents/python/dffml/entities/alice/alice/cli.py", line 309, in cli_run_on_repo
    await dffml.run_dataflow.run_custom(
  File "/home/pdxjohnny/Documents/python/dffml/dffml/operation/dataflow.py", line 203, in run_custom
    async for ctx, result in octx.run(subflow_inputs, parent=self.octx):
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1689, in run
    raise exception
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1857, in run_operations_for_ctx
    raise OperationException(
dffml.df.base.OperationException: alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayGit:contribute_readme_md({'repo': AliceGitRepo, 'base': repo.git.base.branch, 'commit_message': repo.readme.git.commit.message}): {'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-bxee21vb', URL='https://github.com/pdxjohnny/testa'), 'base': 'main', 'commit_message': 'Recommended Community Standard: Add README'}

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/pdxjohnny/.local/bin/alice", line 33, in <module>
    sys.exit(load_entry_point('alice', 'console_scripts', 'alice')())
  File "/home/pdxjohnny/Documents/python/dffml/dffml/util/cli/cmd.py", line 282, in main
    result = loop.run_until_complete(cls._main(*argv[1:]))
  File "/usr/lib/python3.9/asyncio/base_events.py", line 642, in run_until_complete
    return future.result()
  File "/home/pdxjohnny/Documents/python/dffml/dffml/util/cli/cmd.py", line 248, in _main
    return await cls.cli(*args)
  File "/home/pdxjohnny/Documents/python/dffml/dffml/util/cli/cmd.py", line 234, in cli
    return await cmd.do_run()
  File "/home/pdxjohnny/Documents/python/dffml/dffml/util/cli/cmd.py", line 213, in do_run
    return await self.run()
  File "/home/pdxjohnny/Documents/python/dffml/entities/alice/alice/cli.py", line 514, in run
    async for ctx, results in dffml.run(
  File "/home/pdxjohnny/Documents/python/dffml/dffml/high_level/dataflow.py", line 231, in run
    async for ctx, results in ctx.run(*input_sets, strict=strict):
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1689, in run
    raise exception
  File "/home/pdxjohnny/Documents/python/dffml/dffml/df/memory.py", line 1857, in run_operations_for_ctx
    raise OperationException(
dffml.df.base.OperationException: alice.cli.AlicePleaseContributeRecommendedCommunityStandardsOverlayCLI:cli_run_on_repo({'repo': CLIRunOnRepo}): {'repo': 'https://github.com/pdxjohnny/testa'}
```


- `AlicePleaseContributeRecommendedCommunityStandardsOverlayGitHubIssue:readme_issue` should go to 