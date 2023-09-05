## 2023-03-22 OneAPI App CI/CD Working Session

- Every day we surf the chaos 🏄‍♂️
- References
  - #1392
  - #1391
- Michael developed a Sphinx site with some custom JS which has the database built via CI/CD ❤️
- https://github.com/oneapi-src/oneAPI-samples/
- Michael flipped the gh-pages switches
- https://oneapi-src.github.io/oneAPI-samples/
  - Blank right now
- Noticed it did the default build. We switch to deploy from gh-pages afterwards.

![image](https://user-images.githubusercontent.com/5950433/226976386-2d2f1761-6cf2-4cfe-9bd4-7b9e9a76d827.png)

- https://github.com/oneapi-src/oneAPI-samples/tree/app/dev
- https://github.com/oneapi-src/oneAPI-samples/pull/1457
- https://github.com/oneapi-src/oneAPI-samples/tree/531314589f766d8f93a312855cb627cd3692a41c
  - Looks like we don't have the `.nojekyll` file in the gh-pages branch
- https://github.com/oneapi-src/oneAPI-samples/blob/3ac2f6136f112db733afe0db5866e12a0fb6f4e8/.github/github-pages.yml#L67
  - We'll make a minor change here to trigger the workflow

```console
$ git checkout app/dev
$ git pull --rebase upstream app/dev
```

- Weird rebase conflicts, just going to reset to upstream because we have no other
  changes.

```console
$ git reset --hard upstream/app/dev
$ sed -i -e 's/{{github.repository}}/{{github.repository}}/g' .github/github-pages.yml
$ git add .github/github-pages.yml
$ git checkout -b app/dev upstream/app/dev
$ git push -u upstream app/dev && gh pr create --fill && gh pr merge --rebase --auto
```

- Not seeing workflow under actions page
  - https://github.com/oneapi-src/oneAPI-samples/actions
  - Noticed it needs to move under workflows directory
- [Error: .github#L1](https://github.com/oneapi-src/oneAPI-samples/commit/e85d5bdc376d4234ec8778f5a7b8cb9dd21dd04c#annotation_9919858013)
  - https://github.com/oneapi-src/oneAPI-samples/actions/runs/4492420124
    - > a step cannot have both the `uses` and `run` keys
  - We had a copy pasta with `actions/checkout`
  - https://github.com/oneapi-src/oneAPI-samples/commit/4141959c3f9328e72cf87197944af16b5d6fe832
- https://github.com/oneapi-src/oneAPI-samples/actions/runs/4492462722
- https://github.com/oneapi-src/oneAPI-samples/pull/1464
- https://github.com/oneapi-src/oneAPI-samples/actions/runs/4492509212/jobs/7902491740
  - Need to add sphinx to `requirements.txt`
- https://github.com/oneapi-src/oneAPI-samples/actions/runs/4492603075

```
Configuration error:
config directory doesn't contain a conf.py file (/home/runner/work/oneAPI-samples/oneAPI-samples/src)
```

- https://github.com/oneapi-src/oneAPI-samples/pull/1465
- https://github.com/oneapi-src/oneAPI-samples/actions/runs/4492670680
  - Clean build!
- https://github.com/oneapi-src/oneAPI-samples/pull/1466
- Deployed! WOOHOO!
- Adding Cascading Style Sheets
  - https://github.com/oneapi-src/oneAPI-samples/commit/0fec1533300818ecdcf09e28091c5d5d116c74a7
  - https://github.com/oneapi-src/oneAPI-samples/actions/runs/4493632962

![image](https://user-images.githubusercontent.com/5950433/227013474-3ac6a496-5831-4557-b45a-2f988b7d4258.png)

- CSS SUCCESS!
  - Some more to do still but we have UI!
- TODO
  - [x] Figure out why `.nojekyll` isn't there despite the touch being on line 70
    - We pushed to gh-pages manually and didn't run the workflow
  - [x] Workflow needs to move under `.github/workflows/`
  - [x] Move actions/checkout to it's own step
  - [x] Fix `runs-on` typo
  - [x] Add sphinx to `requirements.txt`
  - [x] Modify conditional around pushing docs to `gh-pages` to the `app/dev` branch for testing