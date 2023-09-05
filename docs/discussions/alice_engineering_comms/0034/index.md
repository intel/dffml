# 2022-09-22 Engineering Logs

- Gnosticism & The Supreme Reality - Alan Watts
  - https://anchor.fm/sabrina-borja/episodes/Gnosticism--The-Supreme-Reality---Alan-Watts-eehqgr
  - https://anchor.fm/s/1351bf54/podcast/rss
  - https://d3ctxlq1ktw2nl.cloudfront.net/staging/2020-05-25/24a16eaddc18ff58c96e24bee0faf6b8.m4a
    - Time for whisper

```console
$ curl -sfL https://anchor.fm/s/1351bf54/podcast/rss | tee podcasts.rss.xml
$ grep -C 4 '\.m' podcasts.rss.xml | grep -A 5 Gnos
                        <link>https://anchor.fm/sabrina-borja/episodes/Gnosticism--The-Supreme-Reality---Alan-Watts-eehqgr</link>
                        <guid isPermaLink="false">6f19c9d0-5d94-4858-8387-1cec43c39569</guid>
                        <dc:creator><![CDATA[Sabrina Borja]]></dc:creator>
                        <pubDate>Mon, 25 May 2020 14:42:18 GMT</pubDate>
                        <enclosure url="https://anchor.fm/s/1351bf54/podcast/play/14264283/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fstaging%2F2020-05-25%2F24a16eaddc18ff58c96e24bee0faf6b8.m4a" length="50094380" type="audio/x-m4a"/>
                        <itunes:summary>&lt;p&gt;Alan Watts talks about the gnosticism and the supreme reality&lt;/p&gt;
```

- compute
  - to go from the state of unknown to the state of known
    - pursuit of knowledge