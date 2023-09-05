## 2022-09-26 @pdxjohnny Engineering Logs

- Alice
  - State of the art updated to 98335d941116e76bbf4e07422adc2b5061e47934
  - Overlay of CI/CD library detection example: https://github.com/intel/dffml/commit/90d5c52f4dd64f046a2e2469d001e32ec2d53966

Install Alice: https://github.com/intel/dffml/tree/alice/entities/alice/

```console
$ python -m venv .venv
$ . .venv/bin/activate
$ python -m pip install -U pip setuptools wheel
$ export ALICE_STATE_OF_ART=98335d941116e76bbf4e07422adc2b5061e47934
$ python -m pip install \
    "[https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml](https://github.com/intel/dffml/archive/$%7BALICE_STATE_OF_ART%7D.zip#egg=dffml)" \
    "[https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml-feature-git&subdirectory=feature/git](https://github.com/intel/dffml/archive/$%7BALICE_STATE_OF_ART%7D.zip#egg=dffml-feature-git&subdirectory=feature/git)" \
    "[https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=shouldi&subdirectory=examples/shouldi](https://github.com/intel/dffml/archive/$%7BALICE_STATE_OF_ART%7D.zip#egg=shouldi&subdirectory=examples/shouldi)" \
    "[https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml-config-yaml&subdirectory=configloader/yaml](https://github.com/intel/dffml/archive/$%7BALICE_STATE_OF_ART%7D.zip#egg=dffml-config-yaml&subdirectory=configloader/yaml)" \
    "[https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml-operations-innersource&subdirectory=operations/innersource](https://github.com/intel/dffml/archive/$%7BALICE_STATE_OF_ART%7D.zip#egg=dffml-operations-innersource&subdirectory=operations/innersource)" \
    "[https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=alice&subdirectory=entities/alice](https://github.com/intel/dffml/archive/$%7BALICE_STATE_OF_ART%7D.zip#egg=alice&subdirectory=entities/alice)"
```

Install this overlay (from this commit in this example):

```console
$ python -m pip install --force-reinstall --upgrade "git+https://github.com/intel/dffml@d2a38d47445241fc99d26bc2a51184caa88bd033#subdirectory=entities/alice"
```

Collect metrics on a repo using `alice shouldi contribute`:

```console
$ alice -log debug shouldi contribute -keys https://github.com/pdxjohnny/httptest 2>&1 | tee .alice.shouldi.contribute.log.$(date "+%4Y-%m-%d-%H-%M").txt
$ alice -log debug shouldi contribute -record-def GitHubRepoID -keys 149512216 2>&1 | tee .alice.shouldi.contribute.log.$(date "+%4Y-%m-%d-%H-%M").txt
$ python -c 'import yaml, json, sys; print(yaml.dump(json.load(sys.stdin)))' < .tools/open-architecture/innersource/repos.json
untagged:
  https://github.com/aliceoa/example-github-action:
    features:
      alice.shouldi.contribute.cicd:cicd_action_library:
        result: true
      group_by:
        ActionYAMLFileWorkflowUnixStylePath:
        - my_action_name/action.yml
```

- Generating JSON schema
  - https://pydantic-docs.helpmanual.io/usage/schema/
  - https://pydantic-docs.helpmanual.io/install/
  - https://pydantic-docs.helpmanual.io/usage/model_config/
    - https://pydantic-docs.helpmanual.io/usage/schema/#schema-customization
  - Initial commit: 168a3e26c62d7e0c8dd92b1761ec5fad273fb9c6
  - Added `$schema` to make output schema a valid Manifest schema per ADR requirements
    - https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md
- KERI
  - https://keri.one
  - https://humancolossus.foundation/blog/thinking-of-did-keri-on/keri-resources/
- References
  - https://open-music.org/
  - https://github.com/fzipp/gocyclo
    - > Calculate cyclomatic complexities of functions in Go source code.

```console
$ curl -sfL https://github.com/intel/dffml/ | grep octolytics-dimension-repository_id
  <meta name="octolytics-dimension-user_id" content="17888862" /><meta name="octolytics-dimension-user_login" content="intel" /><meta name="octolytics-dimension-repository_id" content="149512216" /><meta name="octolytics-dimension-repository_nwo" content="intel/dffml" /><meta name="octolytics-dimension-repository_public" content="true" /><meta name="octolytics-dimension-repository_is_fork" content="false" /><meta name="octolytics-dimension-repository_network_root_id" content="149512216" /><meta name="octolytics-dimension-repository_network_root_nwo" content="intel/dffml" />
coder@coder-john-s-andersen-alice:/src/dffml$ curl -sfL https://github.com/intel/dffml/ | grep octolytics-dimension-repository_id | sed -e 's/octolytics-dimension-repository_id" content="//'
  <meta name="octolytics-dimension-user_id" content="17888862" /><meta name="octolytics-dimension-user_login" content="intel" /><meta name="149512216" /><meta name="octolytics-dimension-repository_nwo" content="intel/dffml" /><meta name="octolytics-dimension-repository_public" content="true" /><meta name="octolytics-dimension-repository_is_fork" content="false" /><meta name="octolytics-dimension-repository_network_root_id" content="149512216" /><meta name="octolytics-dimension-repository_network_root_nwo" content="intel/dffml" />
coder@coder-john-s-andersen-alice:/src/dffml$ curl -sfL https://github.com/intel/dffml/ | grep octolytics-dimension-repository_id | sed -e 's/.*octolytics-dimension-repository_id" content="//'
149512216" /><meta name="octolytics-dimension-repository_nwo" content="intel/dffml" /><meta name="octolytics-dimension-repository_public" content="true" /><meta name="octolytics-dimension-repository_is_fork" content="false" /><meta name="octolytics-dimension-repository_network_root_id" content="149512216" /><meta name="octolytics-dimension-repository_network_root_nwo" content="intel/dffml" />
coder@coder-john-s-andersen-alice:/src/dffml$ curl -sfL https://github.com/intel/dffml/ | grep octolytics-dimension-repository_id | sed -e 's/.*octolytics-dimension-repository_id" content="//' -e 's/".*//'
149512216
coder@coder-john-s-andersen-alice:/src/dffml $ gh api https://api.github.com/repositories/149512216 | jq -r '.clone_url'
https://github.com/intel/dffml.git
```

Added GitHubRepoID to URL lookup via https://github.com/intel/dffml/commit/4d64f011ccdee8882adbc4b7447953c4416ceb64

Run the metric collection

```console
coder@coder-john-s-andersen-alice:/src/dffml$ alice -log debug shouldi contribute -record-def GitHubRepoID -keys 149512216
```

Convert to YAML for easy reading

```console
$ python -c 'import yaml, json, sys; print(yaml.dump(json.load(sys.stdin)))' < .tools/open-architecture/innersource/repos.json
untagged:
  https://github.com/trekhleb/javascript-algorithms:
    extra: {}
    features:
      dffml_operations_innersource.operations:badge_maintained:
        result: https://img.shields.io/badge/Maintainance-Active-green
      dffml_operations_innersource.operations:badge_unmaintained:
        result: https://img.shields.io/badge/Maintainance-Inactive-red
      group_by:
        GitHubActionsWorkflowUnixStylePath:
        - .github/workflows/CI.yml
        author_line_count:
        - Oleksii Trekhleb: 370
        bool:
        - true
        commit_shas:
        - d3c0ee6f7af3fce4a3a2bdc1c5be36d7c2d9793a
        release_within_period:
        - false
    key: https://github.com/trekhleb/javascript-algorithms
    last_updated: '2022-09-26T15:13:00Z'
```

- Accidentally force pushed
  - Enabled branch protected on the `alice` branch
  - Went to PR and looked for "forced pushed" in logs
  - Grabbed the commit and found the compare because we can download the patchset but it won't let us create a branch off it that we could tell
    - https://github.com/intel/dffml/compare/alice...0c4b8191b13465980ced3fd1ddfbea30af3d1104.patch
  - Downloaded with curl
    - `curl -sfLO https://github.com/intel/dffml/compare/alice...0c4b8191b13465980ced3fd1ddfbea30af3d1104.patch`
  - Removed the first patch which we rebase squashed other commits into
    - `vim alice...0c4b8191b13465980ced3fd1ddfbea30af3d1104.patch`
  - Apply patches (there were 15 after removing the collecting Jenkins patch)
    - `git am < alice...0c4b8191b13465980ced3fd1ddfbea30af3d1104.patch`

```yaml
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
```

- Ah, forgot to call `COLLECTOR_DATAFLOW.update_by_origin()`
  - We always forget about this, we should probably call `dataflow.update_by_origin()` by default on orchestrator context entry.
- In progress on auto creation of JSON schema from single object or list of example objects

```diff
diff --git a/configloader/jsonschema/tests/test_config.py b/configloader/jsonschema/tests/test_config.py
index ea4852862..2a0b9ffa1 100644
--- a/configloader/jsonschema/tests/test_config.py
+++ b/configloader/jsonschema/tests/test_config.py
@@ -137,4 +137,6 @@ class TestConfig(AsyncTestCase):
             async with configloader() as ctx:
                 original = {"Test": ["dict"]}
                 reloaded = await ctx.loadb(await ctx.dumpb(original))
+                from pprint import pprint
+                pprint(reloaded)
                 self.assertEqual(original, TEST_0_SCHEMA_SHOULD_BE)
```

```console
$ python -m unittest discover -v
test_0_dumpb_loadb (tests.test_config.TestConfig) ... {'$schema': 'https://intel.github.io/dffml/manifest-format-name.0.0.2.schema.json',
 'definitions': {'FooBar': {'properties': {'count': {'title': 'Count',
                                                     'type': 'integer'},
                                           'size': {'title': 'Size',
                                                    'type': 'number'}},
                            'required': ['count'],
                            'title': 'FooBar',
                            'type': 'object'},
                 'Gender': {'description': 'An enumeration.',
                            'enum': ['male', 'female', 'other', 'not_given'],
                            'title': 'Gender',
                            'type': 'string'}},
 'description': 'This is the description of the main model',
 'properties': {'Gender': {'$ref': '#/definitions/Gender'},
                'foo_bar': {'$ref': '#/definitions/FooBar'},
                'snap': {'default': 42,
                         'description': 'this is the value of snap',
                         'exclusiveMaximum': 50,
                         'exclusiveMinimum': 30,
                         'title': 'The Snap',
                         'type': 'integer'}},
 'required': ['foo_bar'],
 'title': 'Main',
 'type': 'object'}
FAIL

======================================================================
FAIL: test_0_dumpb_loadb (tests.test_config.TestConfig)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/src/dffml/dffml/util/asynctestcase.py", line 115, in run_it
    result = self.loop.run_until_complete(coro(*args, **kwargs))
  File "/.pyenv/versions/3.9.13/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
    return future.result()
  File "/src/dffml/configloader/jsonschema/tests/test_config.py", line 142, in test_0_dumpb_loadb
    self.assertEqual(original, TEST_0_SCHEMA_SHOULD_BE)
AssertionError: {'Test': ['dict']} != {'title': 'Main', 'description': 'This is t[665 chars]g'}}}
Diff is 1276 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 1 test in 0.005s

FAILED (failures=1)
```

- TODO
  - [ ] Add option for output configloader similar to `-log` for all CLI commands.
    - [ ] Enables serialization of returned objects from `CMD.run()` methods into to arbitrary formats.
  - [ ] `JSONSchemaConfigLoaderConfig.multi: bool` could allow us to interpret the input as a set of inputs which the generated schema should conform to all.