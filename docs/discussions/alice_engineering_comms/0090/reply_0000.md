## 2022-11-18 @pdxjohnny Engineering Logs

- https://social-embed.git-pull.com/docs/wc/
  - This looks interesting
    - https://oembed.com/
      - > oEmbed is a format for allowing an embedded representation of a URL on third party sites. The simple API allows a website to display embedded content (such as photos or videos) when a user posts a link to that resource, without having to parse the resource directly.
- https://ocaml.org
  - Used for Linux kernel semantic patches
- https://github.com/cue-lang/cue
  - Need to play with Cue language
- GitHub Actions templates docs
  - [Reusable workflows]() are identified by the presence of [`on.workflow_call`](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#onworkflow_call) an example of a reusable workflow for container builds following the [manifest](https://github.com/intel/dffml/blob/alice/docs/arch/0008-Manifest.md) pattern can be found ​in the [`*build_images_containers.yml` files](https://github.com/intel/dffml/blob/main/.github/workflows/build_images_containers.yml).
- GitHub Action runner support SCITT receipts on containers / actions
- `podman` support SCITT recpits
- https://ariadne.space/2019/07/13/federation-what-flows-where-and-why/
  - > most of the risks described here are mitigated by telling mastodon to use authorized fetch mode.  please turn authorized fetch mode on, for your own good.
- https://hacker.solar/books/about-this-site/page/what-is-hacker-solar
- https://github.com/intel/cve-bin-tool/issues/2334#issuecomment-1315643093
  - https://social.treehouse.systems/@ariadne/109365116698192103
  - We are going to try to hybridize the authroized fetch mode with SCITT receipts and then bridge that into web5
  - Also touched on recent OIDC verification via notary
- Need to remove time from tmux for idle time to work so that it doesn't tick every second and make giant files when there is no new output other than the time
  - https://github.com/git-pull/tao-of-tmux/blob/master/manuscript/10-scripting.md#formats-formats

```console
$ nodemon -e py --exec 'clear; nvd_api_key=$NVD_API_KEY LONG_TESTS=1 timeout 10s python3.10 -um coverage run -m pytest -v --log-level=DEBUG --log-cli-level=DEBUG test/test_nvd_api.py::TestNVD_API::test_total_results_count -k 2.0; test 1'
...
___________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________ TestNVD_API.test_total_results_count[2.0-feed1-stats1] ____________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

self = <test.test_nvd_api.TestNVD_API object at 0x7f8dcaa7cf70>, api_version = '2.0', feed = <httptest.httptest.Server object at 0x7f8dcaa7c7c0>, stats = <httptest.httptest.Server object at 0x7f8dcaa7c700>
...
>               assert len(nvd_api.all_cve_entries) >= nvd_api.total_results
E               assert 0 >= 10
...
test/test_nvd_api.py:88: AssertionError
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Captured log setup ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DEBUG    asyncio:selector_events.py:54 Using selector: EpollSelector
DEBUG    asyncio:selector_events.py:54 Using selector: EpollSelector
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Captured stdout call ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Fetching incremental metadata from NVD... ━━━━━━━━━━━━━━━━━━━━━━━━━   0% -:--:--
Downloading Feeds from NVD... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Captured stderr call ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
127.0.0.1 - - [18/Nov/2022 08:38:09] "GET /?reporttype=countsbystatus HTTP/1.1" 200 -
127.0.0.1 - - [18/Nov/2022 08:38:09] "GET /2.0?startIndex=0&resultsPerPage=1 HTTP/1.1" 200 -
127.0.0.1 - - [18/Nov/2022 08:38:09] "GET /2.0?startIndex=0&resultsPerPage=2000&lastModStartDate=2022-11-16T16:36:09:895&lastModEndDate=2022-11-18T16:38:09:902 HTTP/1.1" 200 -
127.0.0.1 - - [18/Nov/2022 08:38:12] "GET /2.0?startIndex=0&resultsPerPage=2000&lastModStartDate=2022-11-16T16:36:09:895&lastModEndDate=2022-11-18T16:38:09:902 HTTP/1.1" 200 -
127.0.0.1 - - [18/Nov/2022 08:38:12] "GET /2.0?startIndex=2000&resultsPerPage=2000&lastModStartDate=2022-11-16T16:36:09:895&lastModEndDate=2022-11-18T16:38:09:902 HTTP/1.1" 200 -
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Captured log call ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INFO     cve_bin_tool.NVD_API:nvd_api.py:135 Fetching metadata from NVD...
DEBUG    alice.emulate.nvd.api:nvdstyle.py:158 ParseResult(scheme='', netloc='', path='/', params='', query='reporttype=countsbystatus', fragment='')
DEBUG    alice.emulate.nvd.api:nvdstyle.py:163 {'reporttype': ['countsbystatus']}
DEBUG    alice.emulate.nvd.api:nvdstyle.py:172 Serving stats...
INFO     cve_bin_tool.NVD_API:nvd_api.py:137 Got metadata from NVD: {'Total': 10, 'Rejected': 0, 'Received': 0, 'Modified': 0, 'Undergoing Analysis': 0, 'Awaiting Analysis': 0}
INFO     cve_bin_tool.NVD_API:nvd_api.py:140 self.total_results = Total: 10 - Rejected: 0
INFO     cve_bin_tool.NVD_API:nvd_api.py:144 Valiating NVD api...
DEBUG    alice.emulate.nvd.api:nvdstyle.py:158 ParseResult(scheme='', netloc='', path='/2.0', params='', query='startIndex=0&resultsPerPage=1', fragment='')
DEBUG    alice.emulate.nvd.api:nvdstyle.py:163 {'startIndex': ['0'], 'resultsPerPage': ['1']}
DEBUG    alice.emulate.nvd.api:nvdstyle.py:240 Serving validate NVD API: start_index: 0 results_per_page: 1...
DEBUG    alice.emulate.nvd.api:nvdstyle.py:274 Serving validate: results: {'format': 'NVD_CVE', 'resultsPerPage': 1, 'startIndex': 0, 'timestamp': '2022-11-18T08:38Z', 'totalResults': 10, 'version': '2.0', 'vulnerabilities': [{'cve': {'configurations': [{'nodes': [{'cpeMatch': [{'criteria': 'cpe:2.3:a:eric_allman:sendmail:5.58:*:*:*:*:*:*:*', 'matchCriteriaId': '1D07F493-9C8D-44A4-8652-F28B46CBA27C', 'vulnerable': True}], 'negate': False, 'operator': 'OR'}]}], 'descriptions': [{'lang': 'en', 'value': 'The debug command in Sendmail is enabled, allowing attackers to execute commands as root.'}, {'lang': 'es', 'value': 'El comando de depuración de Sendmail está activado, permitiendo a atacantes ejecutar comandos como root.'}], 'id': 'CVE-1999-0095', 'lastModified': '2019-06-11T20:29:00.263', 'metrics': {'cvssMetricV2': [{'acInsufInfo': False, 'cvssData': {'accessComplexity': 'LOW', 'accessVector': 'NETWORK', 'authentication': 'NONE', 'availabilityImpact': 'COMPLETE', 'baseScore': 10.0, 'baseSeverity': 'HIGH', 'confidentialityImpact': 'COMPLETE', 'integrityImpact': 'COMPLETE', 'vectorString': 'AV:N/AC:L/Au:N/C:C/I:C/A:C', 'version': '2.0'}, 'exploitabilityScore': 10.0, 'impactScore': 10.0, 'obtainAllPrivilege': True, 'obtainOtherPrivilege': False, 'obtainUserPrivilege': False, 'source': 'nvd@nist.gov', 'type': 'Primary', 'userInteractionRequired': False}]}, 'published': '1988-10-01T04:00:00.000', 'references': [{'source': 'cve@mitre.org', 'url': 'http://seclists.org/fulldisclosure/2019/Jun/16'}, {'source': 'cve@mitre.org', 'url': 'http://www.openwall.com/lists/oss-security/2019/06/05/4'}, {'source': 'cve@mitre.org', 'url': 'http://www.openwall.com/lists/oss-security/2019/06/06/1'}, {'source': 'cve@mitre.org', 'url': 'http://www.securityfocus.com/bid/1'}], 'sourceIdentifier': 'cve@mitre.org', 'vulnStatus': 'Modified', 'weaknesses': [{'description': [{'lang': 'en', 'value': 'NVD-CWE-Other'}], 'source': 'nvd@nist.gov', 'type': 'Primary'}]}}]}
INFO     cve_bin_tool.NVD_API:nvd_api.py:146 Valiated NVD api
INFO     cve_bin_tool.NVD_API:nvd_api.py:175 Fetching updated CVE entries after 2022-11-16T16:36:09:895
DEBUG    alice.emulate.nvd.api:nvdstyle.py:158 ParseResult(scheme='', netloc='', path='/2.0', params='', query='startIndex=0&resultsPerPage=2000&lastModStartDate=2022-11-16T16:36:09:895&lastModEndDate=2022-11-18T16:38:09:902', fragment='')
DEBUG    alice.emulate.nvd.api:nvdstyle.py:163 {'startIndex': ['0'], 'resultsPerPage': ['2000'], 'lastModStartDate': ['2022-11-16T16:36:09:895'], 'lastModEndDate': ['2022-11-18T16:38:09:902']}
DEBUG    alice.emulate.nvd.api:nvdstyle.py:284 Serving feed: start_index: 0 results_per_page: 2000...
DEBUG    alice.emulate.nvd.api:nvdstyle.py:336 Serving feed with 10 results
INFO     cve_bin_tool.NVD_API:nvd_api.py:189 Adding 10 CVE entries
DEBUG    alice.emulate.nvd.api:nvdstyle.py:158 ParseResult(scheme='', netloc='', path='/2.0', params='', query='startIndex=0&resultsPerPage=2000&lastModStartDate=2022-11-16T16:36:09:895&lastModEndDate=2022-11-18T16:38:09:902', fragment='')
DEBUG    alice.emulate.nvd.api:nvdstyle.py:158 ParseResult(scheme='', netloc='', path='/2.0', params='', query='startIndex=2000&resultsPerPage=2000&lastModStartDate=2022-11-16T16:36:09:895&lastModEndDate=2022-11-18T16:38:09:902', fragment='')
DEBUG    alice.emulate.nvd.api:nvdstyle.py:163 {'startIndex': ['0'], 'resultsPerPage': ['2000'], 'lastModStartDate': ['2022-11-16T16:36:09:895'], 'lastModEndDate': ['2022-11-18T16:38:09:902']}
DEBUG    alice.emulate.nvd.api:nvdstyle.py:163 {'startIndex': ['2000'], 'resultsPerPage': ['2000'], 'lastModStartDate': ['2022-11-16T16:36:09:895'], 'lastModEndDate': ['2022-11-18T16:38:09:902']}
DEBUG    alice.emulate.nvd.api:nvdstyle.py:284 Serving feed: start_index: 0 results_per_page: 2000...
DEBUG    alice.emulate.nvd.api:nvdstyle.py:284 Serving feed: start_index: 2000 results_per_page: 2000...
DEBUG    alice.emulate.nvd.api:nvdstyle.py:336 Serving feed with 10 results
DEBUG    alice.emulate.nvd.api:nvdstyle.py:336 Serving feed with 0 results
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- Captured log teardown --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DEBUG    asyncio:selector_events.py:54 Using selector: EpollSelector
=================================================================================================================================================================================================================================================================================================================== short test summary info ==============================================================================================================================================================  - 
=====================================================================================================================================================
FAILED test/test_nvd_api.py::TestNVD_API::test_total_results_count[2.0-feed1-stats1] - assert 0 >= 10
=============================================================================================================================================================================================================================================================================================================== 1 failed, 1 deselected in 6.51s ===============================================================================================================================================================================================================================================================================================================
[nodemon] clean exit - waiting for changes before restart
```

- Ah ha! Enabled debug logging because noticed we weren't seeing the
  "Send Request" log client side.

```diff
diff --git a/cve_bin_tool/log.py b/cve_bin_tool/log.py
index 85b7009..749b867 100644
--- a/cve_bin_tool/log.py
+++ b/cve_bin_tool/log.py
@@ -30,4 +30,4 @@ logging.basicConfig(
 root_logger = logging.getLogger()
 
 LOGGER = logging.getLogger(__package__)
-LOGGER.setLevel(logging.INFO)
+LOGGER.setLevel(logging.DEBUG)
diff --git a/cve_bin_tool/nvd_api.py b/cve_bin_tool/nvd_api.py
index 28bc102..0f82748 100644
--- a/cve_bin_tool/nvd_api.py
+++ b/cve_bin_tool/nvd_api.py
@@ -130,14 +130,20 @@ class NVD_API:
 
         if not self.session:
             connector = aiohttp.TCPConnector(limit_per_host=19)
-            self.session = RateLimiter(
-                aiohttp.ClientSession(connector=connector, trust_env=True)
-            )
+            self.session = aiohttp.ClientSession(connector=connector, trust_env=True)
 
         self.logger.info("Fetching metadata from NVD...")
         cve_count = await self.nvd_count_metadata(self.session, self.stats)
+        self.logger.info("Got metadata from NVD: %r", cve_count)
+
+        self.total_results = cve_count["Total"] - cve_count["Rejected"]
+        self.logger.info(
+            f'self.total_results = Total: {cve_count["Total"]} - Rejected: {cve_count["Rejected"]}'
+        )
 
+        self.logger.info("Valiating NVD api...")
         await self.validate_nvd_api()
+        self.logger.info("Valiated NVD api")
 
         if self.invalid_api:
             self.logger.warning(
@@ -180,8 +186,6 @@ class NVD_API:
                     progress.update(task)
                 progress.update(task, advance=1)
 
-            else:
-                self.total_results = cve_count["Total"] - cve_count["Rejected"]
             self.logger.info(f"Adding {self.total_results} CVE entries")
 
     async def validate_nvd_api(self):
@@ -227,7 +231,6 @@ class NVD_API:
                     self.logger.debug(f"Response received {response.status}")
                     if response.status == 200:
                         fetched_data = await response.json()
-
                         if start_index == 0:
                             # Update total results in case there is discrepancy between NVD dashboard and API
                             reject_count = (
@@ -238,6 +241,9 @@ class NVD_API:
                             self.total_results = (
                                 fetched_data["totalResults"] - reject_count
                             )
+                            self.logger.info(
+                                f'self.total_results = Total: {fetched_data["totalResults"]} - Rejected: {reject_count}'
+                            )
                         if self.api_version == "1.0":
                             self.all_cve_entries.extend(
                                 fetched_data["result"]["CVE_Items"]
diff --git a/test/test_nvd_api.py b/test/test_nvd_api.py
index 91cf1fb..e7e2a96 100644
--- a/test/test_nvd_api.py
+++ b/test/test_nvd_api.py
@@ -2,16 +2,26 @@
 # SPDX-License-Identifier: GPL-3.0-or-later
 
 import os
+import types
 import shutil
 import tempfile
+import contextlib
 from datetime import datetime, timedelta
 from test.utils import LONG_TESTS
 
 import pytest
+import aiohttp
+import httptest
+
+import alice.threats.vulns.serve.nvdstyle
 
 from cve_bin_tool.cvedb import CVEDB
 from cve_bin_tool.data_sources import nvd_source
-from cve_bin_tool.nvd_api import NVD_API
+from cve_bin_tool.nvd_api import (
+    NVD_API,
+    FEED as NVD_API_FEED,
+    NVD_CVE_STATUS,
+)
 
 
 class TestNVD_API:
@@ -42,14 +52,40 @@ class TestNVD_API:
         LONG_TESTS() != 1 or not os.getenv("nvd_api_key"),
         reason="NVD tests run only in long tests",
     )
-    async def test_total_results_count(self):
+    @pytest.mark.parametrize(
+        "api_version, feed, stats",
+        [
+            (
+                "1.0",
+                httptest.Server(alice.threats.vulns.serve.nvdstyle.NVDStyleHTTPHandler),
+                httptest.Server(alice.threats.vulns.serve.nvdstyle.NVDStyleHTTPHandler),
+            ),
+            (
+                "2.0",
+                httptest.Server(alice.threats.vulns.serve.nvdstyle.NVDStyleHTTPHandler),
+                httptest.Server(alice.threats.vulns.serve.nvdstyle.NVDStyleHTTPHandler),
+            ),
+        ],
+    )
+    async def test_total_results_count(self, api_version, feed, stats):
         """Total results should be greater than or equal to the current fetched cves"""
-        nvd_api = NVD_API(api_key=os.getenv("nvd_api_key") or "")
-        await nvd_api.get_nvd_params(
-            time_of_last_update=datetime.now() - timedelta(days=2)
-        )
-        await nvd_api.get()
-        assert len(nvd_api.all_cve_entries) >= nvd_api.total_results
+        # TODO alice.nvd.TestHTTPServer will become either
+        # alice.nvd.TestNVDVersion_1_0 or alice.nvd.TestNVDVersion_2_0
+        # lambda *args: alice.nvd.TestHTTPServer(*args, directory=pathlib.Path(__file__).parent)
+        with feed as feed_http_server, stats as stats_http_server:
+            async with aiohttp.ClientSession() as session:
+                nvd_api = NVD_API(
+                    feed=feed_http_server.url(),
+                    stats=stats_http_server.url(),
+                    api_key=os.getenv("nvd_api_key") or "",
+                    session=session,
+                    api_version=api_version,
+                )
+                await nvd_api.get_nvd_params(
+                    time_of_last_update=datetime.now() - timedelta(days=2)
+                )
+                await nvd_api.get()
+                assert len(nvd_api.all_cve_entries) >= nvd_api.total_results
 
     @pytest.mark.asyncio- 

     @pytest.mark.skipif(
```

- Enabling debug logging resulted in the following statement being logged.
  - This failure should probably be an `ERROR` level rather than `DEBUG` log.

```
DEBUG    cve_bin_tool.NVD_API:nvd_api.py:274 Failed to connect to NVD list indices must be integers or slices, not str
```

- Added traceback
- Is NVD2 code needing to index? `fetched_data["vulnerabilities"][index]["cve"]`?

```

ERROR    cve_bin_tool.NVD_API:nvd_api.py:276 Pausing requests for 3 seconds
DEBUG    cve_bin_tool.NVD_API:nvd_api.py:277 TypeError('list indices must be integers or slices, not str')
Traceback (most recent call last):
  File "/home/pdxjohnny/Documents/python/cve-bin-tool/cve_bin_tool/nvd_api.py", line 254, in load_nvd_request
    fetched_data["vulnerabilities"]["cve"]
TypeError: list indices must be integers or slices, not str
```

- Found and fixed two issues
  - intel/cve-bin-tool@afc4a9254683d2a7027bc6574e99d1b0d406d5bc
    - fix(nvd_api): Align v2 rejection handling with description schema updates
  - intel/cve-bin-tool@46cd825b126dd167158cae4f5e4ac7a32de2e08d
    - fix(nvd_api): extend all cve entries from v2 query top level vulnerabilities key

[![asciicast](https://asciinema.org/a/538712.svg)](https://asciinema.org/a/538712)

- Pushed 9f0a41ad55bdc7f295c435ebd51db77e3343b915
  - alice: threats: vulns: serve: nvdstyle: Fix serving of v2 style CVEs
- Liquid Time-constant Networks Adaptive Online Networks
  - https://arxiv.org/pdf/2006.04439v1.pdf
- TODO
  - [ ] Finish scorecard demo and intergate into shouldi
    - Put this in down the dependency rabbit hole again as one of the things we put in `THREATS.md`
  - [ ] `alice threats cicd` (`-keys https://github.com/intel/dffml`)
    - [ ] GitHub Actions workflow analysis overlays
      - [ ] Look for `runs-on:` and anything not GitHub hosted, then
            check `on:` triggers to ensure pull requests aren't being run.