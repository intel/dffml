# Alice, should I contribute? Data Flow

Cross post: https://gist.github.com/pdxjohnny/57b049c284e58f51d0a0d35d05d03d4a
Cross post: https://github.com/intel/dffml/discussions/1382#discussioncomment-4141177
Cross post: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4141183
Upstream: https://github.com/intel/dffml/tree/8847989eb4cc9f6aa484285ba9c11ff920113ed3

```console
$ export TITLE="Alice, should I contribute? Data Flow (upstream: https://github.com/intel/dffml/tree/8847989eb4cc9f6aa484285ba9c11ff920113ed3)";
$ (echo "${TITLE}" \
    && echo \
    && python -um dffml service dev export alice.cli:ALICE_COLLECTOR_DATAFLOW > alice_shouldi_contribute.json \
    && echo '```mermaid' \
    && python -um dffml dataflow diagram -stage processing -configloader json alice_shouldi_contribute.json \
    && echo '```' \
    && echo \
    && echo '```yaml' \
    && python -c "import sys, pathlib, json, yaml; print(yaml.dump(json.load(sys.stdin)))" < alice_shouldi_contribute.json \
    && echo '```' \
    && echo) \
    | gh gist create --public --desc "${TITLE}" -f ALICE_SHOULDI_CONTRIBUTE_THREATS.md -
```

```mermaid
graph TD
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
subgraph d367039fa2c485f55058105e7e0c0b6b[count_authors]
style d367039fa2c485f55058105e7e0c0b6b fill:#fff4de,stroke:#cece71
70c47962ba601f0df1890f4c72ae1b54[count_authors]
0637dcbe07cd05b96d0a6a2dfbb0c5ff(author_lines)
0637dcbe07cd05b96d0a6a2dfbb0c5ff --> 70c47962ba601f0df1890f4c72ae1b54
e1d1567e6b3a3e5d899b9543c693a66f(authors)
70c47962ba601f0df1890f4c72ae1b54 --> e1d1567e6b3a3e5d899b9543c693a66f
end
subgraph 7c3ab755010b5134c7c3c5be9fed1f1c[dffml_feature_git.feature.operations:git_grep]
style 7c3ab755010b5134c7c3c5be9fed1f1c fill:#fff4de,stroke:#cece71
7155c0a875a889898d6d6e0c7959649b[dffml_feature_git.feature.operations:git_grep]
1fc5390b128a11a95280a89ad371a5ae(repo)
1fc5390b128a11a95280a89ad371a5ae --> 7155c0a875a889898d6d6e0c7959649b
cc134251a8bdd1d0944ea69eafc239a4(search)
cc134251a8bdd1d0944ea69eafc239a4 --> 7155c0a875a889898d6d6e0c7959649b
8b7a73c5b4f92ff7fb362de5d8e90b3e(found)
7155c0a875a889898d6d6e0c7959649b --> 8b7a73c5b4f92ff7fb362de5d8e90b3e
end
subgraph 2863a5f2869f0187864ff7a8afcbc2f5[dffml_operations_innersource.cli:ensure_tokei]
style 2863a5f2869f0187864ff7a8afcbc2f5 fill:#fff4de,stroke:#cece71
a7fe94e6e97c131edebbf73cca7b8852[dffml_operations_innersource.cli:ensure_tokei]
3f6fe14c9392820b8562f809c7e2b8b4(result)
a7fe94e6e97c131edebbf73cca7b8852 --> 3f6fe14c9392820b8562f809c7e2b8b4
end
subgraph 1f8d333356c8981dfc553c7eb00bf366[dffml_operations_innersource.cli:github_repo_id_to_clone_url]
style 1f8d333356c8981dfc553c7eb00bf366 fill:#fff4de,stroke:#cece71
859feff15e5487fdad83ec4c42c506e7[dffml_operations_innersource.cli:github_repo_id_to_clone_url]
d2bc011260868bff46d1a206c404a549(repo_id)
d2bc011260868bff46d1a206c404a549 --> 859feff15e5487fdad83ec4c42c506e7
1f6ba749c4b65c55218b968bf308e4e2(result)
859feff15e5487fdad83ec4c42c506e7 --> 1f6ba749c4b65c55218b968bf308e4e2
end
subgraph f2b87480bbba5729364d76ad2fd5ef17[dffml_operations_innersource.operations:action_yml_files]
style f2b87480bbba5729364d76ad2fd5ef17 fill:#fff4de,stroke:#cece71
4de0ba6484f92eba7073404d21fb3598[dffml_operations_innersource.operations:action_yml_files]
847cd99cca177936d533aaa4918c6699(repo)
847cd99cca177936d533aaa4918c6699 --> 4de0ba6484f92eba7073404d21fb3598
7fa0f9133dfd9f00a90383b38c2ec840(result)
4de0ba6484f92eba7073404d21fb3598 --> 7fa0f9133dfd9f00a90383b38c2ec840
end
subgraph 98179e1c9444a758d9565431f371b232[dffml_operations_innersource.operations:code_of_conduct_present]
style 98179e1c9444a758d9565431f371b232 fill:#fff4de,stroke:#cece71
fb772128fdc785ce816c73128e0afd4d[dffml_operations_innersource.operations:code_of_conduct_present]
f333b126c62bdbf832dddf105278d218(repo)
f333b126c62bdbf832dddf105278d218 --> fb772128fdc785ce816c73128e0afd4d
1233aac886e50641252dcad2124003c9(result)
fb772128fdc785ce816c73128e0afd4d --> 1233aac886e50641252dcad2124003c9
end
subgraph d03657cbeff4a7501071526c5227d605[dffml_operations_innersource.operations:contributing_present]
style d03657cbeff4a7501071526c5227d605 fill:#fff4de,stroke:#cece71
8da2c8a3eddf27e38838c8b6a2cd4ad1[dffml_operations_innersource.operations:contributing_present]
2a1ae8bcc9add3c42e071d0557e98b1c(repo)
2a1ae8bcc9add3c42e071d0557e98b1c --> 8da2c8a3eddf27e38838c8b6a2cd4ad1
52544c54f59ff4838d42ba3472b02589(result)
8da2c8a3eddf27e38838c8b6a2cd4ad1 --> 52544c54f59ff4838d42ba3472b02589
end
subgraph 3ac62bbb02d944121299b756fc806782[dffml_operations_innersource.operations:get_current_datetime_as_git_date]
style 3ac62bbb02d944121299b756fc806782 fill:#fff4de,stroke:#cece71
913421183cb3f7803fb82a12e4ee711f[dffml_operations_innersource.operations:get_current_datetime_as_git_date]
e17cbcbbf2d11ed5ce43603779758076(result)
913421183cb3f7803fb82a12e4ee711f --> e17cbcbbf2d11ed5ce43603779758076
end
subgraph 5827679f9c689590302b3f46277551ec[dffml_operations_innersource.operations:github_workflows]
style 5827679f9c689590302b3f46277551ec fill:#fff4de,stroke:#cece71
160833350a633bb60ee3880fb824189e[dffml_operations_innersource.operations:github_workflows]
caaae91348f7c892daa1d05fbd221352(repo)
caaae91348f7c892daa1d05fbd221352 --> 160833350a633bb60ee3880fb824189e
882be05f5b4ede0846177f68fc70cfd4(result)
160833350a633bb60ee3880fb824189e --> 882be05f5b4ede0846177f68fc70cfd4
end
subgraph f1a14368132c9536201d6260d7fc6b63[dffml_operations_innersource.operations:groovy_files]
style f1a14368132c9536201d6260d7fc6b63 fill:#fff4de,stroke:#cece71
d86d2384b02c75979f3a21818187764e[dffml_operations_innersource.operations:groovy_files]
37b63c13bc63cddeaba57cee5dc3f613(repo)
37b63c13bc63cddeaba57cee5dc3f613 --> d86d2384b02c75979f3a21818187764e
6e31b041bad7c24fa5b0a793ff20890b(result)
d86d2384b02c75979f3a21818187764e --> 6e31b041bad7c24fa5b0a793ff20890b
end
subgraph 49272b4d054d834d0dfd08d62360a489[dffml_operations_innersource.operations:jenkinsfiles]
style 49272b4d054d834d0dfd08d62360a489 fill:#fff4de,stroke:#cece71
a31545bdef7e66159d0b56861e4a4fa3[dffml_operations_innersource.operations:jenkinsfiles]
449ec8a512ad1a002c5bbbd0fc8294e9(repo)
449ec8a512ad1a002c5bbbd0fc8294e9 --> a31545bdef7e66159d0b56861e4a4fa3
4963673c5f8ef045573769c58fc54a77(result)
a31545bdef7e66159d0b56861e4a4fa3 --> 4963673c5f8ef045573769c58fc54a77
end
subgraph 3ab6f933ff2c5d1c31f5acce50ace507[dffml_operations_innersource.operations:readme_present]
style 3ab6f933ff2c5d1c31f5acce50ace507 fill:#fff4de,stroke:#cece71
ae6634d141e4d989b0f53fd3b849b101[dffml_operations_innersource.operations:readme_present]
4d289d268d52d6fb5795893363300585(repo)
4d289d268d52d6fb5795893363300585 --> ae6634d141e4d989b0f53fd3b849b101
65fd35d17d8a7e96c9f7e6aaedb75e3c(result)
ae6634d141e4d989b0f53fd3b849b101 --> 65fd35d17d8a7e96c9f7e6aaedb75e3c
end
subgraph da39b149b9fed20f273450b47a0b65f4[dffml_operations_innersource.operations:security_present]
style da39b149b9fed20f273450b47a0b65f4 fill:#fff4de,stroke:#cece71
c8921544f4665e73080cb487aef7de94[dffml_operations_innersource.operations:security_present]
e682bbcfad20caaab15e4220c81e9239(repo)
e682bbcfad20caaab15e4220c81e9239 --> c8921544f4665e73080cb487aef7de94
5d69c4e5b3601abbd692ade806dcdf5f(result)
c8921544f4665e73080cb487aef7de94 --> 5d69c4e5b3601abbd692ade806dcdf5f
end
subgraph 062b8882104862540d584516edc60008[dffml_operations_innersource.operations:support_present]
style 062b8882104862540d584516edc60008 fill:#fff4de,stroke:#cece71
5cc75c20aee40e815abf96726508b66d[dffml_operations_innersource.operations:support_present]
f0e4cd91ca4f6b278478180a188a2f5f(repo)
f0e4cd91ca4f6b278478180a188a2f5f --> 5cc75c20aee40e815abf96726508b66d
46bd597a57e034f669df18ac9ae0a153(result)
5cc75c20aee40e815abf96726508b66d --> 46bd597a57e034f669df18ac9ae0a153
end
subgraph 208d072a660149b8e7b7e55de1b6d4dd[git_commits]
style 208d072a660149b8e7b7e55de1b6d4dd fill:#fff4de,stroke:#cece71
90b953c5527ed3a579912eea8b02b1be[git_commits]
e0d40a3d87e4946fdf517eaa40848e39(branch)
e0d40a3d87e4946fdf517eaa40848e39 --> 90b953c5527ed3a579912eea8b02b1be
44051d3d0587f293a2f36fb2fca3986e(repo)
44051d3d0587f293a2f36fb2fca3986e --> 90b953c5527ed3a579912eea8b02b1be
80b9ea20367299aca462989eb0356ccf(start_end)
80b9ea20367299aca462989eb0356ccf --> 90b953c5527ed3a579912eea8b02b1be
f75e51a2fca4258c207b5473f62e53e0(commits)
90b953c5527ed3a579912eea8b02b1be --> f75e51a2fca4258c207b5473f62e53e0
end
subgraph a6fadf4f2f5031106e26cfc42fa08fcd[git_repo_author_lines_for_dates]
style a6fadf4f2f5031106e26cfc42fa08fcd fill:#fff4de,stroke:#cece71
0afa2b3dbc72afa67170525d1d7532d7[git_repo_author_lines_for_dates]
3396a58cd186eda4908308395f2421c4(branch)
3396a58cd186eda4908308395f2421c4 --> 0afa2b3dbc72afa67170525d1d7532d7
5ca6153629c6af49e61eb6d5c95c64f2(repo)
5ca6153629c6af49e61eb6d5c95c64f2 --> 0afa2b3dbc72afa67170525d1d7532d7
fef3455ecf4fc7a993cb14c43d4d345f(start_end)
fef3455ecf4fc7a993cb14c43d4d345f --> 0afa2b3dbc72afa67170525d1d7532d7
3bf05667f7df95bb2ae3b614ea998cff(author_lines)
0afa2b3dbc72afa67170525d1d7532d7 --> 3bf05667f7df95bb2ae3b614ea998cff
end
subgraph 2a6fb4d7ae016ca95fcfc061d3d1b8ab[git_repo_checkout]
style 2a6fb4d7ae016ca95fcfc061d3d1b8ab fill:#fff4de,stroke:#cece71
02de40331374616f64ba4a92fbb33edd[git_repo_checkout]
2b82220f7c12c2e39d2dd6330ec875bd(commit)
2b82220f7c12c2e39d2dd6330ec875bd --> 02de40331374616f64ba4a92fbb33edd
95dc6c133455588bd30b1116c857b624(repo)
95dc6c133455588bd30b1116c857b624 --> 02de40331374616f64ba4a92fbb33edd
c762e289fa4f1cd4c4d96b57422f2a81(repo)
02de40331374616f64ba4a92fbb33edd --> c762e289fa4f1cd4c4d96b57422f2a81
end
subgraph d9401f19394958bb1ad2dd4dfc37fa79[git_repo_commit_from_date]
style d9401f19394958bb1ad2dd4dfc37fa79 fill:#fff4de,stroke:#cece71
7bbb97768b34f207c34c1f4721708675[git_repo_commit_from_date]
ba10b1d34771f904ff181cb361864ab2(branch)
ba10b1d34771f904ff181cb361864ab2 --> 7bbb97768b34f207c34c1f4721708675
13e4349f6f7f4c9f65ae38767fab1bd5(date)
13e4349f6f7f4c9f65ae38767fab1bd5 --> 7bbb97768b34f207c34c1f4721708675
0c19b6fe88747ef09defde05a60e8d84(repo)
0c19b6fe88747ef09defde05a60e8d84 --> 7bbb97768b34f207c34c1f4721708675
4941586112b4011d0c72c6264b816db4(commit)
7bbb97768b34f207c34c1f4721708675 --> 4941586112b4011d0c72c6264b816db4
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
subgraph f9155f693f3d5c1dd132e4f9e32175b8[git_repo_release]
style f9155f693f3d5c1dd132e4f9e32175b8 fill:#fff4de,stroke:#cece71
f01273bde2638114cff25a747963223e[git_repo_release]
a5df26b9f1fb4360aac38ee7ad6c5041(branch)
a5df26b9f1fb4360aac38ee7ad6c5041 --> f01273bde2638114cff25a747963223e
84255574141c7ee6735c88c70cb4dc35(repo)
84255574141c7ee6735c88c70cb4dc35 --> f01273bde2638114cff25a747963223e
b2e4d6aa4a5bfba38584dc028dfc35b8(start_end)
b2e4d6aa4a5bfba38584dc028dfc35b8 --> f01273bde2638114cff25a747963223e
2cd7c2339d5e783198a219f02af0240a(present)
f01273bde2638114cff25a747963223e --> 2cd7c2339d5e783198a219f02af0240a
end
subgraph b121cc70dccc771127b429709d55d6d5[lines_of_code_by_language]
style b121cc70dccc771127b429709d55d6d5 fill:#fff4de,stroke:#cece71
ef6d613ca7855a13865933156c79ddea[lines_of_code_by_language]
0b781c240b2945323081606938fdf136(repo)
0b781c240b2945323081606938fdf136 --> ef6d613ca7855a13865933156c79ddea
e51defd3debc1237bf64e6ae611595f7(lines_by_language)
ef6d613ca7855a13865933156c79ddea --> e51defd3debc1237bf64e6ae611595f7
f5eb786f700f1aefd37023db219961a1{str}
f5eb786f700f1aefd37023db219961a1 --> ef6d613ca7855a13865933156c79ddea
end
subgraph 35551a739c7d12be0fed88e1d92a296c[lines_of_code_to_comments]
style 35551a739c7d12be0fed88e1d92a296c fill:#fff4de,stroke:#cece71
b6e1f853d077365deddea22b2fdb890d[lines_of_code_to_comments]
669759049f3ac6927280566ef45cf980(langs)
669759049f3ac6927280566ef45cf980 --> b6e1f853d077365deddea22b2fdb890d
850cdec03e4988f119a67899cbc5f311(code_to_comment_ratio)
b6e1f853d077365deddea22b2fdb890d --> 850cdec03e4988f119a67899cbc5f311
end
subgraph 00b5efb50d0353b48966d833eabb1757[make_quarters]
style 00b5efb50d0353b48966d833eabb1757 fill:#fff4de,stroke:#cece71
7f20bd2c94ecbd47ab6bd88673c7174f[make_quarters]
89dd142dfced4933070ebf4ffaff2630(number)
89dd142dfced4933070ebf4ffaff2630 --> 7f20bd2c94ecbd47ab6bd88673c7174f
224e033ecd73401fc95efaa7d7fa799b(quarters)
7f20bd2c94ecbd47ab6bd88673c7174f --> 224e033ecd73401fc95efaa7d7fa799b
end
subgraph 87b1836daeb62eee5488373bd36b0c48[quarters_back_to_date]
style 87b1836daeb62eee5488373bd36b0c48 fill:#fff4de,stroke:#cece71
9dc9f9feff38d8f5dd9388d3a60e74c0[quarters_back_to_date]
00bf6f65f7fa0d1ffce8e87585fae1b5(date)
00bf6f65f7fa0d1ffce8e87585fae1b5 --> 9dc9f9feff38d8f5dd9388d3a60e74c0
8a2fb544746a0e8f0a8984210e6741dc(number)
8a2fb544746a0e8f0a8984210e6741dc --> 9dc9f9feff38d8f5dd9388d3a60e74c0
cf114d5eea4795cef497592d0632bad7(date)
9dc9f9feff38d8f5dd9388d3a60e74c0 --> cf114d5eea4795cef497592d0632bad7
9848c2c8981da29ca1cbce32c1a4e457(start_end)
9dc9f9feff38d8f5dd9388d3a60e74c0 --> 9848c2c8981da29ca1cbce32c1a4e457
end
subgraph 6d61616898ab2c6024fd2a04faba8e02[work]
style 6d61616898ab2c6024fd2a04faba8e02 fill:#fff4de,stroke:#cece71
67e92c8765a9bc7fb2d335c459de9eb5[work]
91794b0e2b5307720bed41f22724c339(author_lines)
91794b0e2b5307720bed41f22724c339 --> 67e92c8765a9bc7fb2d335c459de9eb5
8fd602a64430dd860b0a280217d8ccef(work)
67e92c8765a9bc7fb2d335c459de9eb5 --> 8fd602a64430dd860b0a280217d8ccef
end
1f6ba749c4b65c55218b968bf308e4e2 --> 7440e73a8e8f864097f42162b74f2762
7ec43cbbf66e6d893180645d5e929bb4(seed<br>URL)
style 7ec43cbbf66e6d893180645d5e929bb4 fill:#f6dbf9,stroke:#a178ca
7ec43cbbf66e6d893180645d5e929bb4 --> 7440e73a8e8f864097f42162b74f2762
1f6ba749c4b65c55218b968bf308e4e2 --> eed77b9eea541e0c378c67395351099c
7ec43cbbf66e6d893180645d5e929bb4(seed<br>URL)
style 7ec43cbbf66e6d893180645d5e929bb4 fill:#f6dbf9,stroke:#a178ca
7ec43cbbf66e6d893180645d5e929bb4 --> eed77b9eea541e0c378c67395351099c
a6ed501edbf561fda49a0a0a3ca310f0(seed<br>git_repo_ssh_key)
style a6ed501edbf561fda49a0a0a3ca310f0 fill:#f6dbf9,stroke:#a178ca
a6ed501edbf561fda49a0a0a3ca310f0 --> 8b5928cd265dd2c44d67d076f60c8b05
8e39b501b41c5d0e4596318f80a03210 --> 6a44de06a4a3518b939b27c790f6cdce
3bf05667f7df95bb2ae3b614ea998cff --> 0637dcbe07cd05b96d0a6a2dfbb0c5ff
4e1d5ea96e050e46ebf95ebc0713d54c --> 1fc5390b128a11a95280a89ad371a5ae
0690fdb25283b1e0a09016a28aa08c08(seed<br>git_grep_search)
style 0690fdb25283b1e0a09016a28aa08c08 fill:#f6dbf9,stroke:#a178ca
0690fdb25283b1e0a09016a28aa08c08 --> cc134251a8bdd1d0944ea69eafc239a4
090b151d70cc5b37562b42c64cb16bb0(seed<br>GitHubRepoID)
style 090b151d70cc5b37562b42c64cb16bb0 fill:#f6dbf9,stroke:#a178ca
090b151d70cc5b37562b42c64cb16bb0 --> d2bc011260868bff46d1a206c404a549
c762e289fa4f1cd4c4d96b57422f2a81 --> 847cd99cca177936d533aaa4918c6699
c762e289fa4f1cd4c4d96b57422f2a81 --> f333b126c62bdbf832dddf105278d218
c762e289fa4f1cd4c4d96b57422f2a81 --> 2a1ae8bcc9add3c42e071d0557e98b1c
c762e289fa4f1cd4c4d96b57422f2a81 --> caaae91348f7c892daa1d05fbd221352
c762e289fa4f1cd4c4d96b57422f2a81 --> 37b63c13bc63cddeaba57cee5dc3f613
c762e289fa4f1cd4c4d96b57422f2a81 --> 449ec8a512ad1a002c5bbbd0fc8294e9
c762e289fa4f1cd4c4d96b57422f2a81 --> 4d289d268d52d6fb5795893363300585
c762e289fa4f1cd4c4d96b57422f2a81 --> e682bbcfad20caaab15e4220c81e9239
c762e289fa4f1cd4c4d96b57422f2a81 --> f0e4cd91ca4f6b278478180a188a2f5f
57651c1bcd24b794dfc8d1794ab556d5 --> e0d40a3d87e4946fdf517eaa40848e39
4e1d5ea96e050e46ebf95ebc0713d54c --> 44051d3d0587f293a2f36fb2fca3986e
9848c2c8981da29ca1cbce32c1a4e457 --> 80b9ea20367299aca462989eb0356ccf
57651c1bcd24b794dfc8d1794ab556d5 --> 3396a58cd186eda4908308395f2421c4
4e1d5ea96e050e46ebf95ebc0713d54c --> 5ca6153629c6af49e61eb6d5c95c64f2
9848c2c8981da29ca1cbce32c1a4e457 --> fef3455ecf4fc7a993cb14c43d4d345f
4941586112b4011d0c72c6264b816db4 --> 2b82220f7c12c2e39d2dd6330ec875bd
4e1d5ea96e050e46ebf95ebc0713d54c --> 95dc6c133455588bd30b1116c857b624
57651c1bcd24b794dfc8d1794ab556d5 --> ba10b1d34771f904ff181cb361864ab2
cf114d5eea4795cef497592d0632bad7 --> 13e4349f6f7f4c9f65ae38767fab1bd5
4e1d5ea96e050e46ebf95ebc0713d54c --> 0c19b6fe88747ef09defde05a60e8d84
4e1d5ea96e050e46ebf95ebc0713d54c --> 181f1b33df4d795fbad2911ec7087e86
2334372b57604cd06ceaf611e1c4a458(no_git_branch_given)
2334372b57604cd06ceaf611e1c4a458 --> 4c3cdd5f15b7a846d291aac089e8a622
57651c1bcd24b794dfc8d1794ab556d5 --> a5df26b9f1fb4360aac38ee7ad6c5041
4e1d5ea96e050e46ebf95ebc0713d54c --> 84255574141c7ee6735c88c70cb4dc35
9848c2c8981da29ca1cbce32c1a4e457 --> b2e4d6aa4a5bfba38584dc028dfc35b8
c762e289fa4f1cd4c4d96b57422f2a81 --> 0b781c240b2945323081606938fdf136
3c4eda0137cefa5452a87052978523ce --> f5eb786f700f1aefd37023db219961a1
176c8001e30dae223370012eeb537711 --> f5eb786f700f1aefd37023db219961a1
3f6fe14c9392820b8562f809c7e2b8b4 --> f5eb786f700f1aefd37023db219961a1
e51defd3debc1237bf64e6ae611595f7 --> 669759049f3ac6927280566ef45cf980
a8b3d979c7c66aeb3b753408c3da0976(seed<br>quarters)
style a8b3d979c7c66aeb3b753408c3da0976 fill:#f6dbf9,stroke:#a178ca
a8b3d979c7c66aeb3b753408c3da0976 --> 89dd142dfced4933070ebf4ffaff2630
e17cbcbbf2d11ed5ce43603779758076 --> 00bf6f65f7fa0d1ffce8e87585fae1b5
224e033ecd73401fc95efaa7d7fa799b --> 8a2fb544746a0e8f0a8984210e6741dc
3bf05667f7df95bb2ae3b614ea998cff --> 91794b0e2b5307720bed41f22724c339
```

<details>
<summary>Full dataflow</summary>

```yaml
configs:
  dffml_operations_innersource.cli:ensure_tokei:
    cache_dir: .tools/open-architecture/innersource/.cache/tokei
    platform_urls:
      Darwin:
        expected_hash: 8c8a1d8d8dd4d8bef93dabf5d2f6e27023777f8553393e269765d7ece85e68837cba4374a2615d83f071dfae22ba40e2
        url: https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-apple-darwin.tar.gz
      Linux:
        expected_hash: 22699e16e71f07ff805805d26ee86ecb9b1052d7879350f7eb9ed87beb0e6b84fbb512963d01b75cec8e80532e4ea29a
        url: https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-unknown-linux-gnu.tar.gz
definitions:
  ActionYAMLFileWorkflowUnixStylePath:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: ActionYAMLFileWorkflowUnixStylePath
    primitive: str
  CICDLibrary:
    links:
    - - - name
        - dict
      - - primitive
        - map
    name: CICDLibrary
    primitive: dict
  FileCodeOfConductPresent:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: FileCodeOfConductPresent
    primitive: bool
  FileContributingPresent:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: FileContributingPresent
    primitive: bool
  FileReadmePresent:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: FileReadmePresent
    primitive: bool
  FileSecurityPresent:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: FileSecurityPresent
    primitive: bool
  FileSupportPresent:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: FileSupportPresent
    primitive: bool
  GitHubActionsWorkflowUnixStylePath:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: GitHubActionsWorkflowUnixStylePath
    primitive: str
  GitHubRepoID:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: GitHubRepoID
    primitive: str
  GroovyFileWorkflowUnixStylePath:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: GroovyFileWorkflowUnixStylePath
    primitive: str
  IsCICDGitHubActionsLibrary:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: IsCICDGitHubActionsLibrary
    primitive: bool
  IsCICDJenkinsLibrary:
    links:
    - - - name
        - bool
      - - primitive
        - bool
    name: IsCICDJenkinsLibrary
    primitive: bool
  JenkinsfileWorkflowUnixStylePath:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: JenkinsfileWorkflowUnixStylePath
    primitive: str
  URL:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: URL
    primitive: str
  author_count:
    name: author_count
    primitive: int
  author_line_count:
    name: author_line_count
    primitive: Dict[str, int]
  bool:
    name: bool
    primitive: bool
  commit_count:
    name: commit_count
    primitive: int
  date:
    name: date
    primitive: string
  date_pair:
    name: date_pair
    primitive: List[date]
  git_branch:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: git_branch
    primitive: str
  git_commit:
    name: git_commit
    primitive: string
  git_grep_found:
    name: git_grep_found
    primitive: string
  git_grep_search:
    name: git_grep_search
    primitive: string
  git_remote:
    links:
    - - - name
        - str
      - - primitive
        - str
    name: git_remote
    primitive: str
  git_repo_ssh_key:
    default: null
    name: git_repo_ssh_key
    primitive: string
  git_repository:
    lock: true
    name: git_repository
    primitive: Dict[str, str]
    spec:
      defaults:
        URL: null
      name: GitRepoSpec
      types:
        URL: str
        directory: str
    subspec: false
  git_repository_checked_out:
    lock: true
    name: git_repository_checked_out
    primitive: Dict[str, str]
    spec:
      defaults:
        URL: null
        commit: null
      name: GitRepoCheckedOutSpec
      types:
        URL: str
        commit: str
        directory: str
    subspec: false
  group_by_output:
    name: group_by_output
    primitive: Dict[str, List[Any]]
  group_by_spec:
    name: group_by_spec
    primitive: Dict[str, Any]
  language_to_comment_ratio:
    name: language_to_comment_ratio
    primitive: int
  lines_by_language_count:
    name: lines_by_language_count
    primitive: Dict[str, Dict[str, int]]
  no_git_branch_given:
    name: no_git_branch_given
    primitive: boolean
  quarter:
    name: quarter
    primitive: int
  quarter_start_date:
    name: quarter_start_date
    primitive: int
  quarters:
    name: quarters
    primitive: int
  release_within_period:
    name: release_within_period
    primitive: bool
  str:
    name: str
    primitive: str
  valid_git_repository_URL:
    name: valid_git_repository_URL
    primitive: boolean
  work_spread:
    name: work_spread
    primitive: int
flow:
  alice.shouldi.contribute.cicd:cicd_action_library:
    inputs:
      action_file_paths:
      - dffml_operations_innersource.operations:action_yml_files: result
  alice.shouldi.contribute.cicd:cicd_jenkins_library:
    inputs:
      groovy_file_paths:
      - dffml_operations_innersource.operations:groovy_files: result
  alice.shouldi.contribute.cicd:cicd_library:
    inputs:
      cicd_action_library:
      - alice.shouldi.contribute.cicd:cicd_action_library: result
      cicd_jenkins_library:
      - alice.shouldi.contribute.cicd:cicd_jenkins_library: result
  check_if_valid_git_repository_URL:
    inputs:
      URL:
      - dffml_operations_innersource.cli:github_repo_id_to_clone_url: result
      - seed
  cleanup_git_repo:
    inputs:
      repo:
      - clone_git_repo: repo
  clone_git_repo:
    conditions:
    - check_if_valid_git_repository_URL: valid
    inputs:
      URL:
      - dffml_operations_innersource.cli:github_repo_id_to_clone_url: result
      - seed
      ssh_key:
      - seed
  count_authors:
    inputs:
      author_lines:
      - git_repo_author_lines_for_dates: author_lines
  dffml_feature_git.feature.operations:git_grep:
    inputs:
      repo:
      - clone_git_repo: repo
      search:
      - seed
  dffml_operations_innersource.cli:ensure_tokei:
    inputs: {}
  dffml_operations_innersource.cli:github_repo_id_to_clone_url:
    inputs:
      repo_id:
      - seed
  dffml_operations_innersource.operations:action_yml_files:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:badge_maintained:
    conditions:
    - dffml_operations_innersource.operations:maintained: result
    - dffml_operations_innersource.operations:unmaintained: result
    inputs: {}
  dffml_operations_innersource.operations:badge_unmaintained:
    conditions:
    - dffml_operations_innersource.operations:maintained: result
    - dffml_operations_innersource.operations:unmaintained: result
    inputs: {}
  dffml_operations_innersource.operations:code_of_conduct_present:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:contributing_present:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:get_current_datetime_as_git_date:
    inputs: {}
  dffml_operations_innersource.operations:github_workflows:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:groovy_files:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:jenkinsfiles:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:maintained:
    inputs:
      results:
      - group_by: output
  dffml_operations_innersource.operations:readme_present:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:security_present:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:support_present:
    inputs:
      repo:
      - git_repo_checkout: repo
  dffml_operations_innersource.operations:unmaintained:
    inputs:
      results:
      - group_by: output
  git_commits:
    inputs:
      branch:
      - git_repo_default_branch: branch
      repo:
      - clone_git_repo: repo
      start_end:
      - quarters_back_to_date: start_end
  git_repo_author_lines_for_dates:
    inputs:
      branch:
      - git_repo_default_branch: branch
      repo:
      - clone_git_repo: repo
      start_end:
      - quarters_back_to_date: start_end
  git_repo_checkout:
    inputs:
      commit:
      - git_repo_commit_from_date: commit
      repo:
      - clone_git_repo: repo
  git_repo_commit_from_date:
    inputs:
      branch:
      - git_repo_default_branch: branch
      date:
      - quarters_back_to_date: date
      repo:
      - clone_git_repo: repo
  git_repo_default_branch:
    conditions:
    - seed
    inputs:
      repo:
      - clone_git_repo: repo
  git_repo_release:
    inputs:
      branch:
      - git_repo_default_branch: branch
      repo:
      - clone_git_repo: repo
      start_end:
      - quarters_back_to_date: start_end
  group_by:
    inputs:
      spec:
      - seed
  lines_of_code_by_language:
    conditions:
    - dffml_operations_innersource.operations:badge_maintained: result
    - dffml_operations_innersource.operations:badge_unmaintained: result
    - dffml_operations_innersource.cli:ensure_tokei: result
    inputs:
      repo:
      - git_repo_checkout: repo
  lines_of_code_to_comments:
    inputs:
      langs:
      - lines_of_code_by_language: lines_by_language
  make_quarters:
    inputs:
      number:
      - seed
  quarters_back_to_date:
    inputs:
      date:
      - dffml_operations_innersource.operations:get_current_datetime_as_git_date: result
      number:
      - make_quarters: quarters
  work:
    inputs:
      author_lines:
      - git_repo_author_lines_for_dates: author_lines
linked: true
operations:
  alice.shouldi.contribute.cicd:cicd_action_library:
    inputs:
      action_file_paths: ActionYAMLFileWorkflowUnixStylePath
    name: alice.shouldi.contribute.cicd:cicd_action_library
    outputs:
      result: IsCICDGitHubActionsLibrary
    retry: 0
    stage: output
  alice.shouldi.contribute.cicd:cicd_jenkins_library:
    inputs:
      groovy_file_paths: GroovyFileWorkflowUnixStylePath
    name: alice.shouldi.contribute.cicd:cicd_jenkins_library
    outputs:
      result: IsCICDJenkinsLibrary
    retry: 0
    stage: output
  alice.shouldi.contribute.cicd:cicd_library:
    inputs:
      cicd_action_library: IsCICDGitHubActionsLibrary
      cicd_jenkins_library: IsCICDJenkinsLibrary
    name: alice.shouldi.contribute.cicd:cicd_library
    outputs:
      result: CICDLibrary
    retry: 0
    stage: output
  check_if_valid_git_repository_URL:
    inputs:
      URL: URL
    name: check_if_valid_git_repository_URL
    outputs:
      valid: valid_git_repository_URL
    retry: 0
    stage: processing
  cleanup_git_repo:
    inputs:
      repo: git_repository
    name: cleanup_git_repo
    outputs: {}
    retry: 0
    stage: cleanup
  clone_git_repo:
    conditions:
    - valid_git_repository_URL
    inputs:
      URL: URL
      ssh_key: git_repo_ssh_key
    name: clone_git_repo
    outputs:
      repo: git_repository
    retry: 0
    stage: processing
  count_authors:
    inputs:
      author_lines: author_line_count
    name: count_authors
    outputs:
      authors: author_count
    retry: 0
    stage: processing
  dffml_feature_git.feature.operations:git_grep:
    inputs:
      repo: git_repository
      search: git_grep_search
    name: dffml_feature_git.feature.operations:git_grep
    outputs:
      found: git_grep_found
    retry: 0
    stage: processing
  dffml_operations_innersource.cli:ensure_tokei:
    inputs: {}
    name: dffml_operations_innersource.cli:ensure_tokei
    outputs:
      result: str
    retry: 0
    stage: processing
  dffml_operations_innersource.cli:github_repo_id_to_clone_url:
    inputs:
      repo_id: GitHubRepoID
    name: dffml_operations_innersource.cli:github_repo_id_to_clone_url
    outputs:
      result: URL
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:action_yml_files:
    expand:
    - result
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:action_yml_files
    outputs:
      result: ActionYAMLFileWorkflowUnixStylePath
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:badge_maintained:
    conditions:
    - bool
    inputs: {}
    name: dffml_operations_innersource.operations:badge_maintained
    outputs:
      result: str
    retry: 0
    stage: output
  dffml_operations_innersource.operations:badge_unmaintained:
    conditions:
    - bool
    inputs: {}
    name: dffml_operations_innersource.operations:badge_unmaintained
    outputs:
      result: str
    retry: 0
    stage: output
  dffml_operations_innersource.operations:code_of_conduct_present:
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:code_of_conduct_present
    outputs:
      result: FileCodeOfConductPresent
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:contributing_present:
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:contributing_present
    outputs:
      result: FileContributingPresent
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:get_current_datetime_as_git_date:
    inputs: {}
    name: dffml_operations_innersource.operations:get_current_datetime_as_git_date
    outputs:
      result: quarter_start_date
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:github_workflows:
    expand:
    - result
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:github_workflows
    outputs:
      result: GitHubActionsWorkflowUnixStylePath
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:groovy_files:
    expand:
    - result
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:groovy_files
    outputs:
      result: GroovyFileWorkflowUnixStylePath
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:jenkinsfiles:
    expand:
    - result
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:jenkinsfiles
    outputs:
      result: JenkinsfileWorkflowUnixStylePath
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:maintained:
    inputs:
      results: group_by_output
    name: dffml_operations_innersource.operations:maintained
    outputs:
      result: bool
    retry: 0
    stage: output
  dffml_operations_innersource.operations:readme_present:
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:readme_present
    outputs:
      result: FileReadmePresent
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:security_present:
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:security_present
    outputs:
      result: FileSecurityPresent
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:support_present:
    inputs:
      repo: git_repository_checked_out
    name: dffml_operations_innersource.operations:support_present
    outputs:
      result: FileSupportPresent
    retry: 0
    stage: processing
  dffml_operations_innersource.operations:unmaintained:
    inputs:
      results: group_by_output
    name: dffml_operations_innersource.operations:unmaintained
    outputs:
      result: bool
    retry: 0
    stage: output
  git_commits:
    inputs:
      branch: git_branch
      repo: git_repository
      start_end: date_pair
    name: git_commits
    outputs:
      commits: commit_count
    retry: 0
    stage: processing
  git_repo_author_lines_for_dates:
    inputs:
      branch: git_branch
      repo: git_repository
      start_end: date_pair
    name: git_repo_author_lines_for_dates
    outputs:
      author_lines: author_line_count
    retry: 0
    stage: processing
  git_repo_checkout:
    inputs:
      commit: git_commit
      repo: git_repository
    name: git_repo_checkout
    outputs:
      repo: git_repository_checked_out
    retry: 0
    stage: processing
  git_repo_commit_from_date:
    inputs:
      branch: git_branch
      date: date
      repo: git_repository
    name: git_repo_commit_from_date
    outputs:
      commit: git_commit
    retry: 0
    stage: processing
  git_repo_default_branch:
    conditions:
    - no_git_branch_given
    inputs:
      repo: git_repository
    name: git_repo_default_branch
    outputs:
      branch: git_branch
      remote: git_remote
    retry: 0
    stage: processing
  git_repo_release:
    inputs:
      branch: git_branch
      repo: git_repository
      start_end: date_pair
    name: git_repo_release
    outputs:
      present: release_within_period
    retry: 0
    stage: processing
  group_by:
    inputs:
      spec: group_by_spec
    name: group_by
    outputs:
      output: group_by_output
    retry: 0
    stage: output
  lines_of_code_by_language:
    conditions:
    - str
    inputs:
      repo: git_repository_checked_out
    name: lines_of_code_by_language
    outputs:
      lines_by_language: lines_by_language_count
    retry: 0
    stage: processing
  lines_of_code_to_comments:
    inputs:
      langs: lines_by_language_count
    name: lines_of_code_to_comments
    outputs:
      code_to_comment_ratio: language_to_comment_ratio
    retry: 0
    stage: processing
  make_quarters:
    expand:
    - quarters
    inputs:
      number: quarters
    name: make_quarters
    outputs:
      quarters: quarter
    retry: 0
    stage: processing
  quarters_back_to_date:
    expand:
    - date
    - start_end
    inputs:
      date: quarter_start_date
      number: quarter
    name: quarters_back_to_date
    outputs:
      date: date
      start_end: date_pair
    retry: 0
    stage: processing
  work:
    inputs:
      author_lines: author_line_count
    name: work
    outputs:
      work: work_spread
    retry: 0
    stage: processing
seed:
- definition: quarters
  origin: seed
  value: 10
- definition: no_git_branch_given
  origin: seed
  value: true
- definition: group_by_spec
  origin: seed
  value:
    ActionYAMLFileWorkflowUnixStylePath:
      by: quarter
      group: ActionYAMLFileWorkflowUnixStylePath
      nostrict: true
    FileCodeOfConductPresent:
      by: quarter
      group: FileCodeOfConductPresent
      nostrict: true
    FileContributingPresent:
      by: quarter
      group: FileContributingPresent
      nostrict: true
    FileReadmePresent:
      by: quarter
      group: FileReadmePresent
      nostrict: true
    FileSecurityPresent:
      by: quarter
      group: FileSecurityPresent
      nostrict: true
    FileSupportPresent:
      by: quarter
      group: FileSupportPresent
      nostrict: true
    GitHubActionsWorkflowUnixStylePath:
      by: quarter
      group: GitHubActionsWorkflowUnixStylePath
      nostrict: true
    GroovyFileWorkflowUnixStylePath:
      by: quarter
      group: GroovyFileWorkflowUnixStylePath
      nostrict: true
    JenkinsfileWorkflowUnixStylePath:
      by: quarter
      group: JenkinsfileWorkflowUnixStylePath
      nostrict: true
    author_line_count:
      by: quarter
      group: author_line_count
      nostrict: true
    commit_shas:
      by: quarter
      group: git_commit
      nostrict: true
    release_within_period:
      by: quarter
      group: release_within_period
      nostrict: true

```

</details>