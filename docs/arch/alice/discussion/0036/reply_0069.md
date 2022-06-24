- Uh oh, we've run into an issue with the managed locking code. At least it seems so right now. Saw this bug about a month ago and forgot about it, dismissed the locking bug as a one off, as if. LOL.

```
$ python -m pdb -m alice shouldi contribute -keys ~/Documents/python/cve-bin-tool -log debug
... OUTPUT CLIPED FOR BREVITY ...
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cv[145/1363$
'))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Outputs: {'lines_by_language': {'autoconf': {'files': 1, 'lines': 5, 'code': 5, 'comment': 0, 'blanks': 0}, 'batch': {'files': 1, 'lines
': 35, 'code': 26, 'comment': 1, 'blanks': 8}, 'css': {'files': 2, 'lines': 215, 'code': 179, 'comment': 22, 'blanks': 14}, 'html': {'files': 9, 'lines': 19054, 'code': 17221, 'comment': 41, '
blanks': 1792}, 'javascript': {'files': 4, 'lines': 107, 'code': 44, 'comment': 59, 'blanks': 4}, 'json': {'files': 3, 'lines': 82, 'code': 82, 'comment': 0, 'blanks': 0}, 'makefile': {'files'
:...
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryLockNetworkContext:Acquired: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool'
))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Stage: PROCESSING: lines_of_code_by_language
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Inputs: {'repo': GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool',
 commit='7cb90d6009d047dfc08dead28110f2314d8c016a')}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Conditions: {'dffml_operations_innersource.cli:ensure_tokei.outputs.result': True}
DEBUG:dffml_feature_git.util:proc.create: ('tokei', '/tmp/dffml-feature-git-1rzly4rx')
DEBUG:dffml.MemoryLockNetworkContext:Acquired: 04e71460-8c4b-4977-ae39-2e838a4431c5(GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve
-bin-tool', commit='4def96cf64c4f58178368f4d1d0118c2e425ccf6'))
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool
'))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:[DISPATCH] lines_of_code_to_comments
DEBUG:dffml.MemoryOrchestratorContext:[/home/pdxjohnny/Documents/python/cve-bin-tool]: dispatch operation: lines_of_code_to_comments
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool
'))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Outputs: {'lines_by_language': {'autoconf': {'files': 1, 'lines': 5, 'code': 5, 'comment': 0, 'blanks': 0}, 'batch': {'files': 1, 'lines
': 35, 'code': 26, 'comment': 1, 'blanks': 8}, 'css': {'files': 2, 'lines': 215, 'code': 179, 'comment': 22, 'blanks': 14}, 'html': {'files': 9, 'lines': 19054, 'code': 17221, 'comment': 41, '
blanks': 1792}, 'javascript': {'files': 4, 'lines': 107, 'code': 44, 'comment': 59, 'blanks': 4}, 'json': {'files': 3, 'lines': 82, 'code': 82, 'comment': 0, 'blanks': 0}, 'makefile': {'files'
:...
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryLockNetworkContext:Acquired: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool'
))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Stage: PROCESSING: lines_of_code_by_language
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Inputs: {'repo': GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool',
 commit='1cfc167fff2df5c598ba0852e91ca8b6d1dde86f')}
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Conditions: {'dffml_operations_innersource.cli:ensure_tokei.outputs.result': True}
DEBUG:dffml_feature_git.util:proc.create: ('tokei', '/tmp/dffml-feature-git-1rzly4rx')
DEBUG:dffml.MemoryLockNetworkContext:Acquired: 022cf49a-dc30-42c5-9679-efb1ea2670ec(GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve
-bin-tool', commit='7cb90d6009d047dfc08dead28110f2314d8c016a'))
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool
'))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:[DISPATCH] lines_of_code_to_comments
DEBUG:dffml.MemoryOrchestratorContext:[/home/pdxjohnny/Documents/python/cve-bin-tool]: dispatch operation: lines_of_code_to_comments
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool
'))
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Outputs: {'lines_by_language': {'autoconf': {'files': 1, 'lines': 5, 'code': 5, 'comment': 0, 'blanks': 0}, 'batch': {'files': 1, 'lines': 35, 'code': 26, 'comment': 1, 'blanks': 8}, 'css': {'files': 2, 'lines': 215, 'code': 179, 'comment': 22, 'blanks': 14}, 'html': {'files': 9, 'lines': 19054, 'code': 17221, 'comment': 41, 'blanks': 1792}, 'javascript': {'files': 4, 'lines': 107, 'code': 44, 'comment': 59, 'blanks': 4}, 'json': {'files': 3, 'lines': 82, 'code': 82, 'comment': 0, 'blanks': 0}, 'makefile': {'files':...                                                                                                                                                                                            DEBUG:dffml.MemoryOperationImplementationNetworkContext:---                                                                                                                                     DEBUG:dffml.MemoryLockNetworkContext:Acquired: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool'))                                                                                                                                                                                              DEBUG:dffml.MemoryOperationImplementationNetworkContext:---
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Stage: PROCESSING: dffml_operations_innersource.operations:contributing_present
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Inputs: {'repo': GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool',
 commit='1d9157b5aec950355aa5793b62d5c9d81e8f575e')}                                                                                                                                            DEBUG:dffml.MemoryOperationImplementationNetworkContext:Conditions: {}                                                                                                                          DEBUG:dffml.MemoryOperationImplementationNetworkContext:Outputs: {'result': False}                                                                                                              DEBUG:dffml.MemoryOperationImplementationNetworkContext:---                                                                                                                                     DEBUG:dffml.MemoryLockNetworkContext:Acquired: 89c0d902-98e8-4bff-8386-c3d9bcf502eb(GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool', commit='1cfc167fff2df5c598ba0852e91ca8b6d1dde86f'))                                                                                                                                 DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool'))                                                                                                                                                                                             DEBUG:dffml.MemoryLockNetworkContext:Acquired: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool'))                                                                                                                                                                                              DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 6eac7b5b-878e-4c68-9d41-9cc4b37c5139(GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool', commit='1d9157b5aec950355aa5793b62d5c9d81e8f575e'))                                                                                                                                DEBUG:dffml.MemoryLockNetworkContext:Acquired: 6eac7b5b-878e-4c68-9d41-9cc4b37c5139(GitRepoCheckedOutSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool', commit='1d9157b5aec950355aa5793b62d5c9d81e8f575e'))                                                                                                                                 DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool'))                                                                                                                                                                                             DEBUG:dffml.MemoryOperationImplementationNetworkContext:[DISPATCH] lines_of_code_to_comments                                                                                                    DEBUG:dffml.MemoryOrchestratorContext:[/home/pdxjohnny/Documents/python/cve-bin-tool]: dispatch operation: lines_of_code_to_comments
DEBUG:dffml.MemoryLockNetworkContext:Acquiring: 85851278-0d74-4baf-9020-35b078ecd1a7(GitRepoSpec(directory='/tmp/dffml-feature-git-1rzly4rx', URL='/home/pdxjohnny/Documents/python/cve-bin-tool
'))
^C
Program interrupted. (Use 'cont' to resume).
```