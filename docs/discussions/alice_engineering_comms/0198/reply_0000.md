## 2023-03-06 @pdxjohnny Engineering Logs

- https://codeberg.org/forgejo/forgejo/src/commit/2fe3a45685545079eb4e82f1954eadf7e065333b/CONTRIBUTING/WORKFLOW.md
- https://codeberg.org/forgejo/forgejo/src/branch/forgejo/CONTRIBUTING/WORKFLOW.md#forgejo-branch
- https://github.com/goreleaser/goreleaser-action
- https://github.com/intel/project-example-for-python
  - Example online clones, pull request CI for basic python package build and test, submit pull request if federated CI/CD events result in built container for manifest.
- Add ssh key to codeberg/gittea

```console
$ echo -n 'f530738005ef4d09962beb8ad11dabe021f215cab37a3212fc81ed3513c42e99' | ssh-keygen -Y sign -n gitea -f ~/.ssh/id_rsa.pub
```

- https://codeberg.org/forgejo/forgejo/pulls/485#issuecomment-826512
  - https://codeberg.org/forgejo-contrib/soft-fork-tools
  - https://codeberg.org/forgejo/forgejo/src/branch/forgejo-development/CONTRIBUTING/WORKFLOW.md#development-workflow
  - https://docs.gitea.io/en-us/hacking-on-gitea/
    - https://docs.gitea.io/en-us/hacking-on-gitea/#building-gitea-basic
- `make test` hangs

```console
$ make test
npm install --no-save
npm WARN deprecated sourcemap-codec@1.4.8: Please use @jridgewell/sourcemap-codec instead

added 850 packages in 11s
npx vitest

 RUN  v0.27.2 /home/pdxjohnny/go/src/codeberg/forgejo/forgejo

 ✓ web_src/js/utils.test.js (13)
 ✓ web_src/js/features/repo-findfile.test.js (4)
 ✓ web_src/js/features/repo-code.test.js (2)
 ✓ web_src/js/svg.test.js (1)

 Test Files  4 passed (4)
      Tests  20 passed (20)
   Start at  04:30:40
   Duration  2.39s (transform 125ms, setup 61ms, collect 609ms, tests 73ms)
```

- Trying https://docs.gitea.io/en-us/hacking-on-gitea/#building-gitea-basic

```console
$ mkdir -p ~/go/src/codeberg/forgejo/
$ git clone -b v1.19/forgejo-ci https://codeberg.org/forgejo/forgejo ~/go/src/codeberg/forgejo/forgejo
$ cd ~/go/src/codeberg/forgejo/forgejo
$ make watch
$ git grep -i activitypub
$ git log -n 1
commit 823ab34c64b275bf57fa60fef25a67338d8cb26e (HEAD -> v1.19/forgejo-ci, origin/v1.19/forgejo-ci)

```

- Grep yields plenty of lines/results
- https://github.com/clearlinux-pkgs/libvirt
- Forgejo Actions runner
  - > Runs workflows found in .forgejo/workflows, using a format similar to GitHub actions but with a Free Software implementation. It is compatible with Forgejo v1.19.0-0-rc0
- From Vadim
  - https://code.themlsbook.com/
  - https://themlsbook.com/read
  - https://acrobat.adobe.com/link/review?uri=urn:aaid:scds:US:b7ad98b3-80ec-44cd-9d16-741f83ff2aaa#pageNum=12
- https://stedolan.github.io/jq/manual/#recurse(f)