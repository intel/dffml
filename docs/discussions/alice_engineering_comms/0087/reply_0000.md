 ## 2022-11-15 @pdxjohnny Engineering Logs

- https://docs.joinmastodon.org/spec/activitypub/
- https://docs.joinmastodon.org/dev/setup/
  - > In the development environment, Mastodon will use PostgreSQL as the currently signed-in Linux user using the `ident` method, which usually works out of the box. The one command you need to run is rails `db:setup` which will create the databases `mastodon_development` and `mastodon_test`, load the schema into them, and then create seed data defined in `db/seed.rb` in `mastodon_development`. The only seed data is an admin account with the credentials `admin@localhost:3000` / `mastodonadmin`.
    - We'll change the `.env.production` user to match
- https://github.com/felx/mastodon-documentation/blob/master/Running-Mastodon/Docker-Guide.md

**.env.production**

```bash
# Generated with mastodon:setup on 2022-11-15 14:37:27 UTC

# Some variables in this file will be interpreted differently whether you are
# using docker-compose or not.

LOCAL_DOMAIN=localhost
SINGLE_USER_MODE=false
SECRET_KEY_BASE=1c60ddccf21afd66e355a85621767feb1ffe47d1b9ac9e8bab5ef283a0fa6c1cc9e7015409bb645551ef7ab4b9f09aed90069640e91500f0009887509d2e1f4f
OTP_SECRET=376e8655790cc05d973d6d427e1e37f98cee9ebc91f6c33eda6243b650fd8f8531a34a43d4c0d62940db6064ea8bdce581d11ff7a22e4ec81f7ffedaad0ad26f
VAPID_PRIVATE_KEY=M7FtL40N4rJ2BtbtyWFHN9b1jaWD4x8p2Pab-FGGb3M=
VAPID_PUBLIC_KEY=BP_BPQEpiSuv0Qri0XWSr54MC0ug5hHb905PPRLufPhu13QCF3D86cW3ReFnZ411VoDB5lDfuntBmYU0Ku65oVs=
DB_HOST=db
DB_PORT=5432
DB_NAME=mastodon_development
DB_USER=admin
DB_PASS=mastodonadmin
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
SMTP_SERVER=localhost
SMTP_PORT=25
SMTP_AUTH_METHOD=none
SMTP_OPENSSL_VERIFY_MODE=none
SMTP_ENABLE_STARTTLS=auto
SMTP_FROM_ADDRESS=Mastodon <notifications@localhost>
```

```console
$ grep POSTGRES_ docker-compose.yml
      - 'POSTGRES_DB=mastodon_development'
      - 'POSTGRES_USER=admin'
      - 'POSTGRES_PASSWORD=mastodonadmin'
$ time podman-compose run -e DISABLE_DATABASE_ENVIRONMENT_CHECK=1 web rails db:setup
... <copy paste config into .env.production> ...
$ time podman-compose run web bundle exec rake db:migrate
$ podman-compose up
$ curl -H "Host: https://localhost:3000/" -v http://localhost:3000/
*   Trying 127.0.0.1:3000...
* Connected to localhost (127.0.0.1) port 3000 (#0)
> GET / HTTP/1.1
> Host: https://localhost:3000/
> User-Agent: curl/7.85.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 403 Forbidden
< Content-Type: text/html; charset=UTF-8
< Content-Length: 0
< 
* Connection #0 to host localhost left intact
```

```console
$ podman-compose run web -e RAILS_ENV=production bin/tootctl accounts modify alice --role Owner
$ podman-compose run web -e RAILS_ENV=production bin/tootctl accounts create \
    alice \
    --email alice@chadig.com \
    --confirmed \
    --role Owner
```

- Okay giving up on Mastodon spin up, RSS feeds (+websub) probably best for SBOM and VEX
  streams anyway.
- References
  - https://github.com/BasixKOR/awesome-activitypub
    - https://github.com/dariusk/rss-to-activitypub
  - https://www.w3schools.com/xml/xml_rss.asp
  - https://github.com/chainfeeds/RSSAggregatorforWeb3
    - Here's a possible basis for our web2 -> web3/5
  - https://github.com/RoCry/feedcooker/releases/tag/latest
    - https://github.com/RoCry/feedcooker/releases/download/latest/Rust_News.xml
    - https://github.com/RoCry/feedcooker/issues/1
      - This is a nice aggregator we could use in the future
  - https://github.com/actionsflow/actionsflow-workflow-default
    - GitHub Actions workflows can trigger from RSS feeds via this third party framework
      not clear if it pools or not. websub and publish / serialize / configloader for
      `dffml dataflow run records set` output as RSS feed?
  - https://actionsflow.github.io/
  - https://mastodon.social/@pdxjohnny.rss
    - Example posted below
  - https://twit.social/@jr/109348004478960008
    - https://twit.social/tags/android.rss
      - Very cool Mastodon will serve RSS feeds for tags.
      - This would allow us to reply to tweets with given tags
        and then automated determine provenance (see deepfake detection),
        and reply with estimated provenance via SBOM / VEX with SCITT
        recpits encoded into (didme.me) image in response (or if
        we can put the CBOR in a JWK claim maybe that would serialize
        to a stupidly long string, then encode that to an image?)
  - https://mastodon.social/tags/scitt.rss
    - It would be nice if there was a multi-tag URL.
      - Example: https://mastodon.social/tags/alice,scitt,vex.rss
      - Example: https://mastodon.social/tags/scitt,vex.rss
      - Example: https://mastodon.social/tags/scitt,sbom.rss

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:webfeeds="http://webfeeds.org/rss/1.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>John</title>
    <description>Public posts from @pdxjohnny@mastodon.social</description>
    <link>https://mastodon.social/@pdxjohnny</link>
    <image>
      <url>https://files.mastodon.social/accounts/avatars/000/032/591/original/9c6c698d572049b4.jpeg</url>
      <title>John</title>
      <link>https://mastodon.social/@pdxjohnny</link>
    </image>
    <lastBuildDate>Tue, 15 Nov 2022 16:18:15 +0000</lastBuildDate>
    <webfeeds:icon>https://files.mastodon.social/accounts/avatars/000/032/591/original/9c6c698d572049b4.jpeg</webfeeds:icon>
    <generator>Mastodon v4.0.2</generator>
    <item>
      <guid isPermaLink="true">https://mastodon.social/@pdxjohnny/109348722777644811</guid>
      <link>https://mastodon.social/@pdxjohnny/109348722777644811</link>
      <pubDate>Tue, 15 Nov 2022 16:18:15 +0000</pubDate>
      <description>&lt;p&gt;RSS VEX feeds?&lt;/p&gt;&lt;p&gt;&lt;a href="https://twit.social/@jr/109345573865828477" target="_blank" rel="nofollow noopener noreferrer"&gt;&lt;span class="invisible"&gt;https://&lt;/span&gt;&lt;span class="ellipsis"&gt;twit.social/@jr/10934557386582&lt;/span&gt;&lt;span class="invisible"&gt;8477&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;p&gt;2022-11-15 Engineering Logs: &lt;a href="https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4146655" target="_blank" rel="nofollow noopener noreferrer"&gt;&lt;span class="invisible"&gt;https://&lt;/span&gt;&lt;span class="ellipsis"&gt;github.com/intel/dffml/discuss&lt;/span&gt;&lt;span class="invisible"&gt;ions/1406?sort=new#discussioncomment-4146655&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;</description>
    </item>
    <item>
      <guid isPermaLink="true">https://mastodon.social/@pdxjohnny/109320563491316354</guid>
      <link>https://mastodon.social/@pdxjohnny/109320563491316354</link>
      <pubDate>Thu, 10 Nov 2022 16:56:58 +0000</pubDate>
      <description>&lt;p&gt;The Alice thread continues!&lt;/p&gt;&lt;p&gt;We take one step further towards decentralization as we federate our way away from Twitter.&lt;/p&gt;&lt;p&gt;Today we&amp;#39;re playing with SCITT and ATProto: &lt;a href="https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4104302" target="_blank" rel="nofollow noopener noreferrer"&gt;&lt;span class="invisible"&gt;https://&lt;/span&gt;&lt;span class="ellipsis"&gt;github.com/intel/dffml/discuss&lt;/span&gt;&lt;span class="invisible"&gt;ions/1406?sort=new#discussioncomment-4104302&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;&lt;p&gt;Prev: &lt;a href="https://twitter.com/pdxjohnny/status/1585488415864557568" target="_blank" rel="nofollow noopener noreferrer"&gt;&lt;span class="invisible"&gt;https://&lt;/span&gt;&lt;span class="ellipsis"&gt;twitter.com/pdxjohnny/status/1&lt;/span&gt;&lt;span class="invisible"&gt;585488415864557568&lt;/span&gt;&lt;/a&gt;&lt;/p&gt;</description>
    </item>
  </channel>
</rss>
```

- We could also httptest NIST API
  - https://github.com/intel/cve-bin-tool/issues/2334
    - Looks like 7 days ago cve-bin-tool community themselves (Terri in this case :) highlighed a similar need!
  - Trying to run tests
    - Need `NVD_API_KEY`
    - Request via email activation flow https://nvd.nist.gov/developers/request-an-api-key
    - Link in email to activation page (10 minute email websub rss? -> ATP)
    - Grab UUID which is token off page

```console
$ nvd_api_key=$NVD_API_KEY LONG_TESTS=1 python -um pytest -v --log-level=DEBUG --log-cli-level=DEBUG test/test_nvd_api.py 2>&1 | gh gist create -p -d 'Failure to launch NVD API tests: https://github.com/intel/cve-bin-tool/issues/2334'
```

- Output of above command: https://gist.github.com/pdxjohnny/dcfaecadd743e773c8aed3e1d323e0bd
  - `$ REC_TITLE="httptest NIST API: 2022-11-15 @pdxjohnny Engineering Logs: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4146655" exec bash`
    - https://github.com/pdxjohnny/dotfiles/blob/ccccfe8f55729bab6f00573a0b3c0358a3a77cf9/.asciinema_source
    - `$ unxz -d < ~/asciinema/fedora-rec-2022-11-15T10:05:02-08:00.json.xz | python -m asciinema upload /dev/stdin`
    - `$ unxz -d < $(ls ~/asciinema/$(hostname)-rec-* | tail -n 1) | python -m asciinema upload /dev/stdin`

[![asciicast-of-failure-to-run-test_nvd_api](https://asciinema.org/a/537871.svg)](https://asciinema.org/a/537871)

[![asciicast](https://asciinema.org/a/537888.svg)](https://asciinema.org/a/537888)

- Got the NVD tests parameterized to versions 1 and 2.

```diff
diff --git a/cve_bin_tool/nvd_api.py b/cve_bin_tool/nvd_api.py
index 6245c56..d151cd1 100644
--- a/cve_bin_tool/nvd_api.py
+++ b/cve_bin_tool/nvd_api.py
@@ -139,7 +139,7 @@ class NVD_API:
 
         if self.invalid_api:
             self.logger.warning(
-                f'Unable to access NVD using provided API key: {self.params["apiKey"]}'
+                f'Unable to access NVD using provided API key: {self.params.get("apiKey", "NO_API_KEY_GIVEN")}'
             )
         else:
             if time_of_last_update:
diff --git a/test/test_nvd_api.py b/test/test_nvd_api.py
index 29f14e9..109815c 100644
--- a/test/test_nvd_api.py
+++ b/test/test_nvd_api.py
@@ -8,6 +8,7 @@ from datetime import datetime, timedelta
 from test.utils import LONG_TESTS
 
 import pytest
+import aiohttp
 
 from cve_bin_tool.cvedb import CVEDB
 from cve_bin_tool.data_sources import nvd_source
@@ -42,14 +43,24 @@ class TestNVD_API:
         LONG_TESTS() != 1 or not os.getenv("nvd_api_key"),
         reason="NVD tests run only in long tests",
     )
-    async def test_total_results_count(self):
+    @pytest.mark.parametrize(
+        "api_version, feed",
+        [
+            ("1.0", None),
+            ("2.0", None),
+        ],
+    )
+    async def test_total_results_count(self, api_version, feed):
         """Total results should be greater than or equal to the current fetched cves"""
-        nvd_api = NVD_API(api_key=os.getenv("nvd_api_key") or "")
-        await nvd_api.get_nvd_params(
-            time_of_last_update=datetime.now() - timedelta(days=2)
-        )
-        await nvd_api.get()
-        assert len(nvd_api.all_cve_entries) >= nvd_api.total_results
+        async with aiohttp.ClientSession() as session:
+            nvd_api = NVD_API(api_key=os.getenv("nvd_api_key") or "",
+                              session=session)
+            nvd_api.logger.info("api_version: %s, feed: %s", api_version, feed)
+            await nvd_api.get_nvd_params(
+                time_of_last_update=datetime.now() - timedelta(days=2)
+            )
+            await nvd_api.get()
+            assert len(nvd_api.all_cve_entries) >= nvd_api.total_results
 
     @pytest.mark.asyncio
     @pytest.mark.skipif(
```

[![asciicast](https://asciinema.org/a/537921.svg)](https://asciinema.org/a/537921)

[![asciicast](https://asciinema.org/a/537925.svg)](https://asciinema.org/a/537925)

[![asciicast-stash-p](https://asciinema.org/a/537931.svg)](https://asciinema.org/a/537931)

- Reverse engineering NIST API by dumping request response

[![asciicast](https://asciinema.org/a/537936.svg)](https://asciinema.org/a/537936)

```console
$ gh gist create -p -d 'intel/cve-bin-tool: tests: add tests for NVD 2.0 API: https://github.com/intel/cve-bin-tool/issues/2334#issuecomment-1315643093: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4146655' /tmp/feed-f232077c4b0644a8f77acb0c63c3d30bb59eff3be774e3e37d00c7b15cfe95079d8d80b48fede725a2f0f19cba0c9496-params.json /tmp/feed-f232077c4b0644a8f77acb0c63c3d30bb59eff3be774e3e37d00c7b15cfe95079d8d80b48fede725a2f0f19cba0c9496.json /tmp/stats.json /tmp/feed-e459d6f8805bad4c8f3097dd5071732478d08e2a6ad50c734199bc24983f49c2d1567ea11bbf2993de662af4736113c4-params.json /tmp/feed-e459d6f8805bad4c8f3097dd5071732478d08e2a6ad50c734199bc24983f49c2d1567ea11bbf2993de662af4736113c4.json /tmp/validate-283492d554c095740c199f739dd4944bfab86a6db800993e16494209c1420061fe7c0e174570715ff7bd9132d26e9b47*
```

- Dumped request response format: https://gist.github.com/pdxjohnny/599b453dffc799f1c4dd8d8024b0f60e
- Started on https://github.com/pdxjohnny/httptest server

[![asciicast](https://asciinema.org/a/537938.svg)](https://asciinema.org/a/537938)

- TODO
  - [ ] ~~Spin up Mastodon~~
  - [ ] Investigate https://docs.joinmastodon.org/spec/webfinger/#example
  - [ ] NIST vuln feed as VEX/VDR API via httptest then integrate as additional vuln feed to cve-bin-tool then publish to via another project (pytss) then to rss then rss-to-activitypub and then see if that integrates with Mastodon then rss to web3/5
    - If we can get something federated working then Alice can send SBOM and VEX updates
      - https://github.com/intel/cve-bin-tool/pull/1698
- Future
  - [ ] Reuse ephemeral ssh server spun up across data flows running on different hosts
  - [ ] Document asciicast-stash-p https://asciinema.org/a/537931 as refactoring method
  - [ ] Multi context logging (multiple Sources? in output query / method / data flow as class?)
    - Examples
      - Posting updates on status of CVE Bin Tool VEX via NVD API style feed
        as well as https://github.com/intel/cve-bin-tool/issues/2334#issuecomment-1315643093