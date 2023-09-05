## 2022-10-24 @pdxjohnny Engineering Logs

- https://medium.com/mlearning-ai/enter-the-world-of-diffusion-models-4485fb5c5986
- https://github.com/martinthomson/i-d-template
- https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0007_an_image.md
  - Future
    - Lossy encoded software DNA transmitted via ad-hoc formed webrtc channels with data / component provenance encoded in-band (maybe SCITT receipts). Context aware collective intelligence is then enabled to iterate at high speed within conceptual impact bounds per group agreed policy.
      - Or multicast ;P
    - ![spaceballs-ludicous-speed](https://user-images.githubusercontent.com/5950433/197626110-69a6f9a3-9e2c-45fa-8ecc-784232c8e868.gif)
- https://twitter.com/pdxjohnny/status/1584657901414928385
  - https://asciinema.org/a/531762

[![asciicast](https://asciinema.org/a/531762.svg)](https://asciinema.org/a/531762)

- https://www.nps.gov/neri/planyourvisit/the-legend-of-john-henry-talcott-wv.htm
  - "If I can't beat this steam drill down, I'll die with this hammer in my hand!" [John Henry]

### Rolling Alice: Architecting Alice: An Image

- References
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0007_an_image.md
  - https://github.com/CleasbyCode/pdvzip
  - https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
  - https://satori-syntax-highlighter.vercel.app/api/highlighter?fontSize=4&lang=python&background=%23E36FB7&code=%22%22%22%0AUsage%0A%2A%2A%2A%2A%2A%0A%0A%2A%2ATODO%2A%2A%0A%0A-%20Packaging%0A%0A..%20code-block%3A%3A%20console%0A%0A%20%20%20%20%24%20echo%20Package%20python%20into%20wheel%20given%20entry%20points%20to%20overlay%20dffml.overlays.alice.please.contribute.recommended_community_standards%0A%20%20%20%20%24%20echo%20Embed%20JWK%0A%20%20%20%20%24%20echo%20JWK%20fulcio%20OIDC%3F%0A%20%20%20%20%24%20echo%20upload%20to%20twitter%20or%20somewhere%0A%20%20%20%20%24%20echo%20download%20and%20verify%20using%20JWK%2C%20show%20OIDC%20for%20online%20lookup%0A%20%20%20%20%24%20pip%20install%20package.zip%0A%20%20%20%20%24%20alice%20shouldi%20contribute%20-log%20debug%20-keys%20https%3A%2F%2Fexamples.com%2Frepowith%2Fmyconfigjson%0A%0A%22%22%22%0Aimport%20json%0Aimport%20pathlib%0Afrom%20typing%20import%20NewType%0A%0AMyConfig%20%3D%20NewType%28%22MyConfig%22%2C%20object%29%0AMyConfigUnvalidated%20%3D%20NewType%28%22MyConfigUnvalidated%22%2C%20object%29%0AMyConfigProjectName%20%3D%20NewType%28%22MyConfigProjectName%22%2C%20str%29%0AMyConfigDirectory%20%3D%20NewType%28%22MyConfigDirectory%22%2C%20str%29%0A%0A%0Adef%20read_my_config_from_directory_if_exists%28%0A%20%20%20%20directory%3A%20MyConfigDirectory%2C%0A%29%20-%3E%20MyConfigUnvalidated%3A%0A%20%20%20%20%22%22%22%0A%20%20%20%20%3E%3E%3E%20import%20json%0A%20%20%20%20%3E%3E%3E%20import%20pathlib%0A%20%20%20%20%3E%3E%3E%20import%20tempfile%0A%20%20%20%20%3E%3E%3E%0A%20%20%20%20%3E%3E%3E%20with%20tempfile.TemporaryDirectory%28%29%20as%20tempdir%3A%0A%20%20%20%20...%20%20%20%20%20_%20%3D%20pathlib.Path%28tempdir%2C%20%22.myconfig.json%22%29.write_text%28json.dumps%28%7B%22name%22%3A%20%22Hello%20World%22%7D%29%29%0A%20%20%20%20...%20%20%20%20%20print%28read_my_config_from_directory_if_exists%28tempdir%29%29%0A%20%20%20%20%7B%27name%27%3A%20%27Hello%20World%27%7D%0A%20%20%20%20%22%22%22%0A%20%20%20%20path%20%3D%20pathlib.Path%28directory%2C%20%22.myconfig.json%22%29%0A%20%20%20%20if%20not%20path.exists%28%29%3A%0A%20%20%20%20%20%20%20%20return%0A%20%20%20%20return%20json.loads%28path.read_text%28%29%29%0A%0A%0Adef%20validate_my_config%28%0A%20%20%20%20config%3A%20MyConfigUnvalidated%2C%0A%29%20-%3E%20MyConfig%3A%0A%20%20%20%20%23%20TODO%28security%29%20json%20schema%20valiation%20of%20myconfig%20%28or%0A%20%20%20%20%23%20make%20done%20automatically%20by%20operation%20manifest%20schema%0A%20%20%20%20%23%20validation%20on%20InputNetwork%2C%20maybe%2C%20just%20one%20option%2C%0A%20%20%20%20%23%20or%20maybe%20similar%20to%20how%20prioritizer%20gets%20applied%2C%0A%20%20%20%20%23%20or%20maybe%20this%20is%20an%20issue%20we%20already%20track%3A%20%231400%29%0A%20%20%20%20return%20config%0A%0A%0Adef%20my_config_project_name%28%0A%20%20%20%20config%3A%20MyConfig%2C%0A%29%20-%3E%20MyConfigProjectName%3A%0A%20%20%20%20%22%22%22%0A%20%20%20%20%3E%3E%3E%20print%28my_config_project_name%28%7B%22name%22%3A%20%22Hello%20World%22%7D%29%29%0A%20%20%20%20Hello%20World%0A%20%20%20%20%22%22%22%0A%20%20%20%20return%20config%5B%22name%22%5D%0A
    - `$ python -c 'import sys, urllib.parse; sys.stdout.write(urllib.parse.quote(sys.stdin.read(), safe=""))'`
      - Orie mentioned "Only twitter web client works for PNGs and they have to be under 900 pixels."
        - https://twitter.com/OR13b/status/1584669807827648512?s=20&t=Xec9v05emwSphzT6W0R8PA
  - https://github.com/ossf/scorecard/blob/main/options/flags.go

```console
$ git clone https://github.com/CleasbyCode/pdvzip
$ cd pdvzip/ && $ g++ pdvzip.cpp -o pdvzip
$ dffml service dev create blank alice-shouldi-contribute-openssf-scorecard
$ cd alice-shouldi-contribute-openssf-scorecard
$ sed -i 's/zip_safe = False/zip_safe = True/' setup.cfg
$ sed -i 's/# entry_points/entry_points/' setup.cfg
$ echo -e '[dffml.overlays.alice.shouldi.contribute]\nOpenSSFScorecard = alice_shouldi_contribute_openssf_scorecard.operations' | tee entry_points.txt
```

**alice_shouldi_contribute_openssf_scorecard/operations.py**

```python
"""
Usage
*****

**TODO**

- Packaging

.. code-block:: console

    $ echo Package python into wheel given entry points to overlay dffml.overlays.alice.please.contribute.recommended_community_standards
    $ echo Embed JWK
    $ echo JWK fulcio OIDC?
    $ echo upload to twitter or somewhere
    $ echo download and verify using JWK, show OIDC for online lookup
    $ pip install package.zip
    $ alice shouldi contribute -log debug -keys https://examples.com/repowith/myconfigjson

"""
import os
import json
import pathlib
import platform
import contextlib
from typing import Dict, NewType

import dffml
import dffml_feature_git.feature.definitions


@dffml.config
class EnsureScorecardConfig:
    cache_dir: pathlib.Path = dffml.field(
        "Cache directory to store downloads in",
        default_factory=lambda: pathlib.Path(os.getcwd()),
    )
    platform_urls: Dict[str, Dict[str, str]] = dffml.field(
        "Mapping of platform.system() return values to scorecard download URLs with hashes",
        default_factory=lambda: {
            "Linux": {
                "url": "https://github.com/ossf/scorecard/releases/download/v4.8.0/scorecard_4.8.0_linux_amd64.tar.gz",
                "expected_hash": "8e90236b3e863447fc98f6131118cd1f509942f985f30ba02825c5d67f2b9999f0ac5aa595bb737ef971788c48cd20c9",
            },
        },
    )


OpenSSFScorecardBinaryPath = NewType("OpenSSFScorecardBinaryPath", str)


@dffml.op(
    config_cls=EnsureScorecardConfig, imp_enter={"stack": contextlib.AsyncExitStack,},
)
async def ensure_scorecard(self) -> OpenSSFScorecardBinaryPath:
    scorecard = await dffml.cached_download_unpack_archive(
        **{
            "file_path": self.parent.config.cache_dir.joinpath("scorecard.tar.gz"),
            "directory_path": self.parent.config.cache_dir.joinpath("scorecard-download"),
            # Use whatever values are appropriate for the system we are on
            **self.parent.config.platform_urls[platform.system()],
        }
    )
    self.parent.stack.enter_context(dffml.prepend_to_path(scorecard))
    binary_path = list(scorecard.glob("scorecard*"))[0].resolve()
    return binary_path


# TODO https://koxudaxi.github.io/datamodel-code-generator/ from schema
OpenSSFScorecardResults = NewType("OpenSSFScorecardResults", dict)


@dffml.op
async def openssf_scorecard(
    self,
    scorecard_path: OpenSSFScorecardBinaryPath,
    repo: dffml_feature_git.feature.definitions.git_repository,
) -> OpenSSFScorecardResults:
    cmd = [
        scorecard_path,
        "--format=json",
        f"--local={repo.directory}"
    ]
    async for event, result in dffml.run_command_events(
        cmd,
        cwd=repo.directory,
        env={
            **os.environ,
        },
        events=[dffml.Subprocess.STDOUT],
        logger=self.logger,
    ):
        return json.loads(result.decode())

```

```conole
$ pip install -e .
$ dffml service dev entrypoints list dffml.overlays.alice.shouldi.contribute
OpenSSFScorecard = alice_shouldi_contribute_openssf_scorecard.operations -> alice-shouldi-contribute-openssf-scorecard 0.1.dev1+g614cd2a.d20221025 (/home/coder/.local/lib/python3.9/site-packages)
$ alice -log debug shouldi contribute -keys https://${GH_ACCESS_TOKEN}@github.com/pdxjohnny/httptest
DEBUG:dffml.MemoryOperationImplementationNetworkContext:Instantiating operation implementation alice_shouldi_contribute_openssf_scorecard.operations:ensure_scorecard(alice_shouldi_contribute_openssf_scorecard.operations:ensure_scorecard) with default config: EnsureScorecardConfig(cache_dir=PosixPath('/tmp/tmp.hgZT8hhxqR/didme.me/pdvzip/alice-shouldi-contribute-openssf-scorecard'), platform_urls={'Linux': {'url': 'https://github.com/ossf/scorecard/releases/download/v4.8.0/scorecard_4.8.0_linux_amd64.tar.gz', 'expected_hash': '8e90236b3e863447fc98f6131118cd1f509942f985f30ba02825c5d67f2b9999f0ac5aa595bb737ef971788c48cd20c9'}})
DEBUG:dffml.AliceShouldiContributeOpenssfScorecardOperations:EnsureScorecardImplementation:EnsureScorecardConfig(cache_dir=PosixPath('/tmp/tmp.hgZT8hhxqR/didme.me/pdvzip/alice-shouldi-contribute-openssf-scorecard'), platform_urls={'Linux': {'url': 'https://github.com/ossf/scorecard/releases/download/v4.8.0/scorecard_4.8.0_linux_amd64.tar.gz', 'expected_hash': '8e90236b3e863447fc98f6131118cd1f509942f985f30ba02825c5d67f2b9999f0ac5aa595bb737ef971788c48cd20c9'}})
```

- It's running the `ensure_scorecard` but not the scan.

```console
$ dffml service dev export alice.cli:ALICE_COLLECTOR_DATAFLOW | tee alice_shouldi_contribute.json
$ dffml dataflow diagram alice_shouldi_contribute.json | tee alice_shouldi_contribute.mmd
```

- Found that we are using `dffml_feature_git.feature.definitions`
  - Rather than we had first tried `AliceGitRepo`, we need to update the shouldi code to have Alice specifics.


```console
$ alice -log debug shouldi contribute -keys https://${GH_ACCESS_TOKEN}@github.com/pdxjohnny/httptest
Traceback (most recent call last):
  File "/src/dffml/dffml/df/memory.py", line 1291, in run_dispatch
    outputs = await self.run(
  File "/src/dffml/dffml/df/memory.py", line 1256, in run
    return await self.run_no_retry(ctx, octx, operation, inputs)
  File "/src/dffml/dffml/df/memory.py", line 1233, in run_no_retry
    outputs = await opctx.run(inputs)
  File "/src/dffml/dffml/df/base.py", line 547, in run
    result = await result
  File "/tmp/tmp.hgZT8hhxqR/didme.me/pdvzip/alice-shouldi-contribute-openssf-scorecard/alice_shouldi_contribute_openssf_scorecard/operations.py", line 64, in openssf_scorecard
    async for event, result in dffml.run_command_events(
  File "/src/dffml/dffml/util/subprocess.py", line 83, in run_command_events
    raise RuntimeError(
RuntimeError: [PosixPath('/tmp/tmp.hgZT8hhxqR/didme.me/pdvzip/alice-shouldi-contribute-openssf-scorecard/scorecard-download/scorecard-linux-amd64'), '--format=json', '--local=/tmp/dffml-feature-git-ly4u_eds']: Error: check runtime error: Dependency-Update-Tool: internal error: Search: unsupported feature
{"date":"2022-10-25","repo":{"name":"file:///tmp/dffml-feature-git-ly4u_eds","commit":"unknown"},"scorecard":{"version":"v4.8.0","commit":"c40859202d739b31fd060ac5b30d17326cd74275"},"score":6.8,"checks":[{"details":null,"score":10,"reason":"no dangerous workflow patterns detected","name":"Dangerous-Workflow","documentation":{"url":"https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#dangerous-workflow","short":"Determines if the project's GitHub Action workflows avoid dangerous patterns."}},{"details":null,"score":-1,"reason":"internal error: Search: unsupported feature","name":"Dependency-Update-Tool","documentation":{"url":"https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#dependency-update-tool","short":"Determines if the project uses a dependency update tool."}},{"details":null,"score":10,"reason":"license file detected","name":"License","documentation":{"url":"https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#license","short":"Determines if the project has defined a license."}},{"details":null,"score":9,"reason":"dependency not pinned by hash detected -- score normalized to 9","name":"Pinned-Dependencies","documentation":{"url":"https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#pinned-dependencies","short":"Determines if the project has declared and pinned the dependencies of its build process."}},{"details":null,"score":0,"reason":"non read-only tokens detected in GitHub workflows","name":"Token-Permissions","documentation":{"url":"https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#token-permissions","short":"Determines if the project's workflows follow the principle of least privilege."}}],"metadata":null}
2022/10/25 00:30:47 error during command execution: check runtime error: Dependency-Update-Tool: internal error: Search: unsupported feature


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/coder/.local/bin/alice", line 8, in <module>
    sys.exit(AliceCLI.main())
  File "/src/dffml/dffml/util/cli/cmd.py", line 286, in main
    result = loop.run_until_complete(cls._main(*argv[1:]))
  File "/.pyenv/versions/3.9.13/lib/python3.9/asyncio/base_events.py", line 647, in run_until_complete
    return future.result()
  File "/src/dffml/dffml/util/cli/cmd.py", line 252, in _main
    return await cls.cli(*args)
  File "/src/dffml/dffml/util/cli/cmd.py", line 238, in cli
    return await cmd.do_run()
  File "/src/dffml/dffml/util/cli/cmd.py", line 215, in do_run
    return [res async for res in self.run()]
  File "/src/dffml/dffml/util/cli/cmd.py", line 215, in <listcomp>
    return [res async for res in self.run()]
  File "/src/dffml/dffml/cli/dataflow.py", line 287, in run
    async for record in self.run_dataflow(
  File "/src/dffml/dffml/cli/dataflow.py", line 272, in run_dataflow
    async for ctx, results in octx.run(
  File "/src/dffml/dffml/df/memory.py", line 1713, in run
    raise exception
  File "/src/dffml/dffml/df/memory.py", line 1881, in run_operations_for_ctx
    raise OperationException(
dffml.df.base.OperationException: alice_shouldi_contribute_openssf_scorecard.operations:openssf_scorecard({'scorecard_path': OpenSSFScorecardBinaryPath, 'repo': git_repository}): {'scorecard_path': PosixPath('/tmp/tmp.hgZT8hhxqR/didme.me/pdvzip/alice-shouldi-contribute-openssf-scorecard/scorecard-download/scorecard-linux-amd64'), 'repo': GitRepoSpec(directory='/tmp/dffml-feature-git-ly4u_eds', URL='https://@github.com/pdxjohnny/httptest')}
$ python -c 'import yaml, json,sys; print(yaml.dump(json.loads(sys.stdin.read())))' < error.json
```

```yaml
checks:
- details: null
  documentation:
    short: Determines if the project's GitHub Action workflows avoid dangerous patterns.
    url: https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#dangerous-workflow
  name: Dangerous-Workflow
  reason: no dangerous workflow patterns detected
  score: 10
- details: null
  documentation:
    short: Determines if the project uses a dependency update tool.
    url: https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#dependency-update-tool
  name: Dependency-Update-Tool
  reason: 'internal error: Search: unsupported feature'
  score: -1
- details: null
  documentation:
    short: Determines if the project has defined a license.
    url: https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#license
  name: License
  reason: license file detected
  score: 10
- details: null
  documentation:
    short: Determines if the project has declared and pinned the dependencies of its
      build process.
    url: https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#pinned-dependencies
  name: Pinned-Dependencies
  reason: dependency not pinned by hash detected -- score normalized to 9
  score: 9
- details: null
  documentation:
    short: Determines if the project's workflows follow the principle of least privilege.
    url: https://github.com/ossf/scorecard/blob/c40859202d739b31fd060ac5b30d17326cd74275/docs/checks.md#token-permissions
  name: Token-Permissions
  reason: non read-only tokens detected in GitHub workflows
  score: 0
date: '2022-10-25'
metadata: null
repo:
  commit: unknown
  name: file:///tmp/dffml-feature-git-ly4u_eds
score: 6.8
scorecard:
  commit: c40859202d739b31fd060ac5b30d17326cd74275
  version: v4.8.0
```

- TODO
  - [ ] Portrait screenshots?
  - [ ] Split into two screenshots, one upstream, one overlay
    - [ ] Another screenshot serving as their manifest to do both