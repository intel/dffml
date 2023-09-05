## 2023-01-30 Engineering Logs

- https://www.oasis-open.org/2022/11/21/new-version-of-csaf-standard/
- Entity Analysis Trinity (EAT) - Behavioral Analysis - Telemetry
  - https://docs.influxdata.com/telegraf/
  - https://collectd.org/
  - https://github.com/delimitrou/DeathStarBench
    - NUMA aware topologies **TODO** link
- https://slsa.dev/provenance/v0.2#example
- https://github.com/CLIP-HPC/SlurmCommander
- https://github.com/fathyb/carbonyl
  - > Carbonyl is a Chromium based browser built to run in a terminal.
  - https://github.com/mholt/caddy-l4
  - https://github.com/charmbracelet/wishlist
    - https://github.com/charmbracelet/wish
  - https://github.com/hackerschoice/segfault
  - https://github.com/intel/dffml/pull/1207#discussion_r1036680987
- https://github.com/CycloneDX/specification/pull/180/files#diff-fae062e182d2604bfaeba757d7d099f1de3b712fa4aea687961ca92df285b39bR192
  - https://dnssecuritytxt.org/
  - > Specifies a way to contact the maintainer, supplier, or provider in the event of a security incident. Common URIs include links to a disclosure procedure, a mailto (RFC-2368) that specifies an email address, a tel (RFC-3966) that specifies a phone number, or dns (RFC-4501]) that specifies the records containing DNS Security TXT.
- https://csarven.ca/web-science-from-404-to-200#be-the-change-towards-linked-research
- https://csarven.ca/linked-research-decentralised-web
  - We want Alice to carry out the scientific process
    - https://linkedresearch.org/annotation/csarven.ca/%23i/87bc9a28-9f94-4b1b-a4b9-503899795f6e
- https://github.com/CycloneDX/specification/pull/180
  - Prototyping our ActivityPubsecuritytxt expansion pack
  - https://mastodon.social/.well-known/webfinger?resource=acct:pdxjohnny@mastodon.social
  - https://mastodon.social/@pdxjohnny/109773521704256215
  - Let's try piggybacking off one attachment, which is the activitypubsecuritytxt
    - https://pdxjohnny.github.io/activitypubsecuritytxt/

```json
{
    "subject": "acct:pdxjohnny@mastodon.social",
    "aliases": [
        "https://mastodon.social/@pdxjohnny",
        "https://mastodon.social/users/pdxjohnny"
    ],
    "links": [
        {
            "rel": "http://webfinger.net/rel/profile-page",
            "type": "text/html",
            "href": "https://mastodon.social/@pdxjohnny"
        },
        {
            "rel": "self",
            "type": "application/activity+json",
            "href": "https://mastodon.social/users/pdxjohnny"
        },
        {
            "rel": "http://ostatus.org/schema/1.0/subscribe",
            "template": "https://mastodon.social/authorize_interaction?uri={uri}"
        }
    ]
}
```

- Just FYI, have been playing with the idea of using security.txt contact as an AcivityPub Actor to advertise things such as delegate Actors for various purposes. For example, list via attachments actors which publish content addresses of an orgs SBOMs This would enable leveraging ActivityPub as a means for definition and broadcast for entities delegated to various roles. We could do the same for the 3rd parties to advertise what actors are within which roles, aka are authorized to say this thing is FIPs certified. We could then attach SCITT receipts to these: https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4794771
  - The SCITT registry then becomes the quick lookup path (analogously database view) to verify this. This way end users don't have to traverse the full Knowledge Graph (Activity Pub in this case). Receipt we care about for verification would be is this `inReplyTo` DAG hop path valid, aka is `did:merkle` in SCITT.
  - Can have a thread linked in attachments for manifests, can discover from there
    - Can watch for replies and execute jobs based off listening for manifest instances `inReplyTo` to the manifest.
      - Post content addresses of manifest existing in oras.land (a container "image" registry)
        - `FROM scratch`
          - [Alice Engineering Comms: 2023-01-19 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4729296)
  - Do we even need ActivityPub for this beyond discovery?
    - Can we just use linked data?
      - We probably need a bridge between the two, so that we can enable the human way of interacting
      - Just finish what you started first!
  - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/advance-readings/Enhancing_DID_Privacy_through_shared_Credentials.md
  - https://github.com/WebOfTrustInfo/rwot11-the-hague/blob/master/draft-documents/did-merkle.md
- Looks like we can have four attachments, we can make one link to a post as an attachment, then replies to that to build more trees of data
- https://policymaker.disclose.io/policymaker/introduction


```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
            "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
            "toot": "http://joinmastodon.org/ns#",
            "featured": {
                "@id": "toot:featured",
                "@type": "@id"
            },
            "featuredTags": {
                "@id": "toot:featuredTags",
                "@type": "@id"
            },
            "alsoKnownAs": {
                "@id": "as:alsoKnownAs",
                "@type": "@id"
            },
            "movedTo": {
                "@id": "as:movedTo",
                "@type": "@id"
            },
            "schema": "http://schema.org#",
            "PropertyValue": "schema:PropertyValue",
            "value": "schema:value",
            "discoverable": "toot:discoverable",
            "Device": "toot:Device",
            "Ed25519Signature": "toot:Ed25519Signature",
            "Ed25519Key": "toot:Ed25519Key",
            "Curve25519Key": "toot:Curve25519Key",
            "EncryptedMessage": "toot:EncryptedMessage",
            "publicKeyBase64": "toot:publicKeyBase64",
            "deviceId": "toot:deviceId",
            "claim": {
                "@type": "@id",
                "@id": "toot:claim"
            },
            "fingerprintKey": {
                "@type": "@id",
                "@id": "toot:fingerprintKey"
            },
            "identityKey": {
                "@type": "@id",
                "@id": "toot:identityKey"
            },
            "devices": {
                "@type": "@id",
                "@id": "toot:devices"
            },
            "messageFranking": "toot:messageFranking",
            "messageType": "toot:messageType",
            "cipherText": "toot:cipherText",
            "suspended": "toot:suspended",
            "Hashtag": "as:Hashtag",
            "focalPoint": {
                "@container": "@list",
                "@id": "toot:focalPoint"
            }
        }
    ],
    "id": "https://mastodon.social/users/pdxjohnny",
    "type": "Person",
    "following": "https://mastodon.social/users/pdxjohnny/following",
    "followers": "https://mastodon.social/users/pdxjohnny/followers",
    "inbox": "https://mastodon.social/users/pdxjohnny/inbox",
    "outbox": "https://mastodon.social/users/pdxjohnny/outbox",
    "featured": "https://mastodon.social/users/pdxjohnny/collections/featured",
    "featuredTags": "https://mastodon.social/users/pdxjohnny/collections/tags",
    "preferredUsername": "pdxjohnny",
    "name": "John",
    "summary": "<p>Playing with words.</p><p>Bits and bytes of lossy streams of consciousness found here.</p><p>Humanity MUST (RFC 2119) work together!</p><p>Priority: \ud83d\uddfa\ufe0f Acceleration of happiness metric \ud83c\udde9\ud83c\uddf0\ud83d\ude01</p><p>This account != owners employer\u2019s views.</p><p><a href=\"https://mastodon.social/tags/%CA%BBIMILOA\" class=\"mention hashtag\" rel=\"tag\">#<span>\u02bbIMILOA</span></a> <a href=\"https://mastodon.social/tags/ChaoticGood\" class=\"mention hashtag\" rel=\"tag\">#<span>ChaoticGood</span></a></p><p>All content here from John is released into the public domain (CC0 1.0). Quote or don\u2019t quote it\u2019s not like there aren\u2019t \u267e\ufe0f Johns anyway.</p><p>Nihilist turned John 1:23 + \u2653\ufe0f</p><p>The Spirit is willing but the brain is in burnout.</p><p>Results of being CI guy</p>",
    "url": "https://mastodon.social/@pdxjohnny",
    "manuallyApprovesFollowers": false,
    "discoverable": true,
    "published": "2017-04-03T00:00:00Z",
    "devices": "https://mastodon.social/users/pdxjohnny/collections/devices",
    "publicKey": {
        "id": "https://mastodon.social/users/pdxjohnny#main-key",
        "owner": "https://mastodon.social/users/pdxjohnny",
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmgrgfu3yUWnCUisG7VSo\nhXXjGHjEPtW0HsdOQ/lUTflLQvBANcVAmgqNR1CxsfmlLJLy3OtLXMFUgbps+2tq\nuf1PuLvDuTVUM69NH+p/6P8GSAvpUc1Ubs/VmOyAd0EVWjh0wgT5sqAEt2wo/s1K\ndoV5j24qeWEkCaKZsvooDkq2yDOzXG2+eyq2964Wstw3zZXh7YflR6JPrTDrR2t2\nPOCBIJR2wkbtIX57TcHORziLu3kCwx7YsTboSMvp4bU0P+/2X2AgzVQRUIKcF38D\nLYG6TIe2nULu4WX1rk8kXzKyyQtiNoxFVJxgh5RB42HwCT+ikvhA8Nmv7BvJ+qNh\n5wIDAQAB\n-----END PUBLIC KEY-----\n"
    },
    "tag": [
        {
            "type": "Hashtag",
            "href": "https://mastodon.social/tags/chaoticgood",
            "name": "#chaoticgood"
        },
        {
            "type": "Hashtag",
            "href": "https://mastodon.social/tags/%CA%BBimiloa",
            "name": "#\u02bbimiloa"
        }
    ],
    "attachment": [
        {
            "type": "PropertyValue",
            "name": "activitypubsecuritytxt",
            "value": "<a href=\"https://mastodon.social/users/pdxjohnny/statuses/109323329037637680\" target=\"_blank\" rel=\"nofollow noopener noreferrer me\"><span class=\"invisible\">https://</span><span class=\"\">mastodon.social/users/pdxjohnny/statuses/109323329037637680</span><span class=\"invisible\"></span></a>"
        }
    ],
    "endpoints": {
        "sharedInbox": "https://mastodon.social/inbox"
    },
    "icon": {
        "type": "Image",
        "mediaType": "image/jpeg",
        "url": "https://files.mastodon.social/accounts/avatars/000/032/591/original/39cca57b3d892045.jpeg"
    },
    "image": {
        "type": "Image",
        "mediaType": "image/jpeg",
        "url": "https://files.mastodon.social/accounts/headers/000/032/591/original/165f3a3436816990.jpeg"
    }
}
```

```console
$ curl -sfL -H "Accept: application/activity+json" "https://mastodon.social/users/pdxjohnny/statuses/109323329037637680" | python3 -m json.tool
```

```json
{
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        {
            "ostatus": "http://ostatus.org#",
            "atomUri": "ostatus:atomUri",
            "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
            "conversation": "ostatus:conversation",
            "sensitive": "as:sensitive",
            "toot": "http://joinmastodon.org/ns#",
            "votersCount": "toot:votersCount",
            "Hashtag": "as:Hashtag"
        }
    ],
    "id": "https://mastodon.social/users/pdxjohnny/statuses/109323329037637680",
    "type": "Note",
    "summary": null,
    "inReplyTo": null,
    "published": "2022-11-11T04:40:17Z",
    "url": "https://mastodon.social/@pdxjohnny/109323329037637680",
    "attributedTo": "https://mastodon.social/users/pdxjohnny",
    "to": [
        "https://www.w3.org/ns/activitystreams#Public"
    ],
    "cc": [
        "https://mastodon.social/users/pdxjohnny/followers"
    ],
    "sensitive": false,
    "atomUri": "https://mastodon.social/users/pdxjohnny/statuses/109323329037637680",
    "inReplyToAtomUri": null,
    "conversation": "tag:mastodon.social,2022-11-11:objectId=329671901:objectType=Conversation",
    "content": "<p>I\u2019m John. I\u2019ve fallen down the open source supply chain security rabbit hole. <a href=\"https://mastodon.social/tags/introduction\" class=\"mention hashtag\" rel=\"tag\">#<span>introduction</span></a> My current focus is around leveraging threat model and architecture information to facilitate automated context aware decentralized gamification / continuous improvement of the security lifecycle / posture of open source projects.</p><p>  - <a href=\"https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866\" target=\"_blank\" rel=\"nofollow noopener noreferrer\"><span class=\"invisible\">https://</span><span class=\"ellipsis\">gist.github.com/pdxjohnny/07b8</span><span class=\"invisible\">c7b4a9e05579921aa3cc8aed4866</span></a><br />  - <a href=\"https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/README.md#rolling-alice-volume-0-introduction-and-context\" target=\"_blank\" rel=\"nofollow noopener noreferrer\"><span class=\"invisible\">https://</span><span class=\"ellipsis\">github.com/intel/dffml/blob/al</span><span class=\"invisible\">ice/docs/tutorials/rolling_alice/0000_architecting_alice/README.md#rolling-alice-volume-0-introduction-and-context</span></a></p><p><a href=\"https://mastodon.social/@pdxjohnny/109320563491316354\" target=\"_blank\" rel=\"nofollow noopener noreferrer\"><span class=\"invisible\">https://</span><span class=\"ellipsis\">mastodon.social/@pdxjohnny/109</span><span class=\"invisible\">320563491316354</span></a></p>",
    "contentMap": {
        "en": "<p>I\u2019m John. I\u2019ve fallen down the open source supply chain security rabbit hole. <a href=\"https://mastodon.social/tags/introduction\" class=\"mention hashtag\" rel=\"tag\">#<span>introduction</span></a> My current focus is around leveraging threat model and architecture information to facilitate automated context aware decentralized gamification / continuous improvement of the security lifecycle / posture of open source projects.</p><p>  - <a href=\"https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866\" target=\"_blank\" rel=\"nofollow noopener noreferrer\"><span class=\"invisible\">https://</span><span class=\"ellipsis\">gist.github.com/pdxjohnny/07b8</span><span class=\"invisible\">c7b4a9e05579921aa3cc8aed4866</span></a><br />  - <a href=\"https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/README.md#rolling-alice-volume-0-introduction-and-context\" target=\"_blank\" rel=\"nofollow noopener noreferrer\"><span class=\"invisible\">https://</span><span class=\"ellipsis\">github.com/intel/dffml/blob/al</span><span class=\"invisible\">ice/docs/tutorials/rolling_alice/0000_architecting_alice/README.md#rolling-alice-volume-0-introduction-and-context</span></a></p><p><a href=\"https://mastodon.social/@pdxjohnny/109320563491316354\" target=\"_blank\" rel=\"nofollow noopener noreferrer\"><span class=\"invisible\">https://</span><span class=\"ellipsis\">mastodon.social/@pdxjohnny/109</span><span class=\"invisible\">320563491316354</span></a></p>"
    },
    "updated": "2022-11-11T04:42:27Z",
    "attachment": [],
    "tag": [
        {
            "type": "Hashtag",
            "href": "https://mastodon.social/tags/introduction",
            "name": "#introduction"
        }
    ],
    "replies": {
        "id": "https://mastodon.social/users/pdxjohnny/statuses/109323329037637680/replies",
        "type": "Collection",
        "first": {
            "type": "CollectionPage",
            "next": "https://mastodon.social/users/pdxjohnny/statuses/109323329037637680/replies?min_id=109323386666400103&page=true",
            "partOf": "https://mastodon.social/users/pdxjohnny/statuses/109323329037637680/replies",
            "items": [
                "https://mastodon.social/users/pdxjohnny/statuses/109323386666400103"
            ]
        }
    }
}
```

- https://wyman.us/public/unofficial-did-method-tag.html#resolving-a-tag-did-via-email

```console
$ rm -f db/database.sqlite3; PROTO=http HOSTNAME=localhost WEBHOOK_PATH=$(cat ../webhook) NODE_ENV=production PORT=8000 ACCOUNT=alice ADMIN_USERNAME=alice ADMIN_PASSWORD=$(cat ../password) PUBLIC_KEY=$(cat publickey.crt) PRIVATE_KEY=$(cat pkcs8.key) npm run dev
$ gh webhook forward --repo=intel/dffml --events=push --url=http://localhost:8000/webhook/$(cat ../webhook)
$ curl -s http://localhost:8000/alice/outbox | python -m json.tool | python -c 'import yaml, json, sys; print(yaml.dump(json.load(sys.stdin)))'
```

```json
{
    "@context": "https://www.w3.org/ns/activitystreams",
    "id": "http://localhost:8000/alice/outbox",
    "type": "OrderedCollection",
    "totalItems": 1,
    "orderedItems": [
        {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "published": "2023-01-30T22:16:14.000Z",
            "actor": "http://localhost:8000/alice",
            "to": [
                "https://www.w3.org/ns/activitystreams#Public"
            ],
            "cc": [],
            "object": {
                "attributedTo": "http://localhost:8000/alice",
                "published": "2023-01-30T22:16:14.151Z",
                "to": [
                    "https://www.w3.org/ns/activitystreams#Public"
                ],
                "cc": [
                    "http://localhost:8000/alice/followers"
                ],
                "type": "Note",
                "content": "{\"ref\":\"refs/heads/alice\",\"before\":\"8e02319e28b2f59c806e7f2a7b5ad202f51a2589\",\"after\":\"d77e2f697d806f71ab7dcf64a74cadfe5eb79598\",\"repository\":{\"id\":149512216,\"node_id\":\"MDEwOlJlcG9zaXRvcnkxNDk1MTIyMTY=\",\"name\":\"dffml\",\"full_name\":\"intel/dffml\",\"private\":false,\"owner\":{\"name\":\"intel\",\"email\":\"webadmin@linux.intel.com\",\"login\":\"intel\",\"id\":17888862,\"node_id\":\"MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/17888862?v=4\",\"gravatar_id\":\"\",\"url\":\"https://api.github.com/users/intel\",\"html_url\":\"https://github.com/intel\",\"followers_url\":\"https://api.github.com/users/intel/followers\",\"following_url\":\"https://api.github.com/users/intel/following{/other_user}\",\"gists_url\":\"https://api.github.com/users/intel/gists{/gist_id}\",\"starred_url\":\"https://api.github.com/users/intel/starred{/owner}{/repo}\",\"subscriptions_url\":\"https://api.github.com/users/intel/subscriptions\",\"organizations_url\":\"https://api.github.com/users/intel/orgs\",\"repos_url\":\"https://api.github.com/users/intel/repos\",\"events_url\":\"https://api.github.com/users/intel/events{/privacy}\",\"received_events_url\":\"https://api.github.com/users/intel/received_events\",\"type\":\"Organization\",\"site_admin\":false},\"html_url\":\"https://github.com/intel/dffml\",\"description\":\"The easiest way to use Machine Learning. Mix and match underlying ML libraries and data set sources. Generate new datasets or modify existing ones with ease.\",\"fork\":false,\"url\":\"https://github.com/intel/dffml\",\"forks_url\":\"https://api.github.com/repos/intel/dffml/forks\",\"keys_url\":\"https://api.github.com/repos/intel/dffml/keys{/key_id}\",\"collaborators_url\":\"https://api.github.com/repos/intel/dffml/collaborators{/collaborator}\",\"teams_url\":\"https://api.github.com/repos/intel/dffml/teams\",\"hooks_url\":\"https://api.github.com/repos/intel/dffml/hooks\",\"issue_events_url\":\"https://api.github.com/repos/intel/dffml/issues/events{/number}\",\"events_url\":\"https://api.github.com/repos/intel/dffml/events\",\"assignees_url\":\"https://api.github.com/repos/intel/dffml/assignees{/user}\",\"branches_url\":\"https://api.github.com/repos/intel/dffml/branches{/branch}\",\"tags_url\":\"https://api.github.com/repos/intel/dffml/tags\",\"blobs_url\":\"https://api.github.com/repos/intel/dffml/git/blobs{/sha}\",\"git_tags_url\":\"https://api.github.com/repos/intel/dffml/git/tags{/sha}\",\"git_refs_url\":\"https://api.github.com/repos/intel/dffml/git/refs{/sha}\",\"trees_url\":\"https://api.github.com/repos/intel/dffml/git/trees{/sha}\",\"statuses_url\":\"https://api.github.com/repos/intel/dffml/statuses/{sha}\",\"languages_url\":\"https://api.github.com/repos/intel/dffml/languages\",\"stargazers_url\":\"https://api.github.com/repos/intel/dffml/stargazers\",\"contributors_url\":\"https://api.github.com/repos/intel/dffml/contributors\",\"subscribers_url\":\"https://api.github.com/repos/intel/dffml/subscribers\",\"subscription_url\":\"https://api.github.com/repos/intel/dffml/subscription\",\"commits_url\":\"https://api.github.com/repos/intel/dffml/commits{/sha}\",\"git_commits_url\":\"https://api.github.com/repos/intel/dffml/git/commits{/sha}\",\"comments_url\":\"https://api.github.com/repos/intel/dffml/comments{/number}\",\"issue_comment_url\":\"https://api.github.com/repos/intel/dffml/issues/comments{/number}\",\"contents_url\":\"https://api.github.com/repos/intel/dffml/contents/{+path}\",\"compare_url\":\"https://api.github.com/repos/intel/dffml/compare/{base}...{head}\",\"merges_url\":\"https://api.github.com/repos/intel/dffml/merges\",\"archive_url\":\"https://api.github.com/repos/intel/dffml/{archive_format}{/ref}\",\"downloads_url\":\"https://api.github.com/repos/intel/dffml/downloads\",\"issues_url\":\"https://api.github.com/repos/intel/dffml/issues{/number}\",\"pulls_url\":\"https://api.github.com/repos/intel/dffml/pulls{/number}\",\"milestones_url\":\"https://api.github.com/repos/intel/dffml/milestones{/number}\",\"notifications_url\":\"https://api.github.com/repos/intel/dffml/notifications{?since,all,participating}\",\"labels_url\":\"https://api.github.com/repos/intel/dffml/labels{/name}\",\"releases_url\":\"https://api.github.com/repos/intel/dffml/releases{/id}\",\"deployments_url\":\"https://api.github.com/repos/intel/dffml/deployments\",\"created_at\":1537391194,\"updated_at\":\"2023-01-17T12:33:57Z\",\"pushed_at\":1675116972,\"git_url\":\"git://github.com/intel/dffml.git\",\"ssh_url\":\"git@github.com:intel/dffml.git\",\"clone_url\":\"https://github.com/intel/dffml.git\",\"svn_url\":\"https://github.com/intel/dffml\",\"homepage\":\"https://intel.github.io/dffml/main/\",\"size\":602687,\"stargazers_count\":201,\"watchers_count\":201,\"language\":\"Python\",\"has_issues\":true,\"has_projects\":true,\"has_downloads\":true,\"has_wiki\":true,\"has_pages\":true,\"has_discussions\":true,\"forks_count\":146,\"mirror_url\":null,\"archived\":false,\"disabled\":false,\"open_issues_count\":387,\"license\":{\"key\":\"mit\",\"name\":\"MIT License\",\"spdx_id\":\"MIT\",\"url\":\"https://api.github.com/licenses/mit\",\"node_id\":\"MDc6TGljZW5zZTEz\"},\"allow_forking\":true,\"is_template\":false,\"web_commit_signoff_required\":false,\"topics\":[\"ai-inference\",\"ai-machine-learning\",\"ai-training\",\"analytics\",\"asyncio\",\"dag\",\"data-flow\",\"dataflows\",\"datasets\",\"dffml\",\"event-based\",\"flow-based-programming\",\"frameworks\",\"hyperautomation\",\"libraries\",\"machine-learning\",\"models\",\"pipelines\",\"python\",\"swrepo\"],\"visibility\":\"public\",\"forks\":146,\"open_issues\":387,\"watchers\":201,\"default_branch\":\"main\",\"stargazers\":201,\"master_branch\":\"main\",\"organization\":\"intel\"},\"pusher\":{\"name\":\"pdxjohnny\",\"email\":\"johnandersenpdx@gmail.com\"},\"organization\":{\"login\":\"intel\",\"id\":17888862,\"node_id\":\"MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy\",\"url\":\"https://api.github.com/orgs/intel\",\"repos_url\":\"https://api.github.com/orgs/intel/repos\",\"events_url\":\"https://api.github.com/orgs/intel/events\",\"hooks_url\":\"https://api.github.com/orgs/intel/hooks\",\"issues_url\":\"https://api.github.com/orgs/intel/issues\",\"members_url\":\"https://api.github.com/orgs/intel/members{/member}\",\"public_members_url\":\"https://api.github.com/orgs/intel/public_members{/member}\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/17888862?v=4\",\"description\":\"\"},\"sender\":{\"login\":\"pdxjohnny\",\"id\":5950433,\"node_id\":\"MDQ6VXNlcjU5NTA0MzM=\",\"avatar_url\":\"https://avatars.githubusercontent.com/u/5950433?v=4\",\"gravatar_id\":\"\",\"url\":\"https://api.github.com/users/pdxjohnny\",\"html_url\":\"https://github.com/pdxjohnny\",\"followers_url\":\"https://api.github.com/users/pdxjohnny/followers\",\"following_url\":\"https://api.github.com/users/pdxjohnny/following{/other_user}\",\"gists_url\":\"https://api.github.com/users/pdxjohnny/gists{/gist_id}\",\"starred_url\":\"https://api.github.com/users/pdxjohnny/starred{/owner}{/repo}\",\"subscriptions_url\":\"https://api.github.com/users/pdxjohnny/subscriptions\",\"organizations_url\":\"https://api.github.com/users/pdxjohnny/orgs\",\"repos_url\":\"https://api.github.com/users/pdxjohnny/repos\",\"events_url\":\"https://api.github.com/users/pdxjohnny/events{/privacy}\",\"received_events_url\":\"https://api.github.com/users/pdxjohnny/received_events\",\"type\":\"User\",\"site_admin\":false},\"created\":false,\"deleted\":false,\"forced\":false,\"base_ref\":null,\"compare\":\"https://github.com/intel/dffml/compare/8e02319e28b2...d77e2f697d80\",\"commits\":[{\"id\":\"d77e2f697d806f71ab7dcf64a74cadfe5eb79598\",\"tree_id\":\"e46341b7cac3e821d68a73bf199efec27625ffcd\",\"distinct\":true,\"message\":\"alice: please: log: todos: Disable overlay to grab created issue URLs which is not yet fully validated\",\"timestamp\":\"2023-01-30T14:16:12-08:00\",\"url\":\"https://github.com/intel/dffml/commit/d77e2f697d806f71ab7dcf64a74cadfe5eb79598\",\"author\":{\"name\":\"John Andersen\",\"email\":\"johnandersenpdx@gmail.com\",\"username\":\"pdxjohnny\"},\"committer\":{\"name\":\"GitHub\",\"email\":\"noreply@github.com\",\"username\":\"web-flow\"},\"added\":[],\"removed\":[],\"modified\":[\"entities/alice/entry_points.txt\"]}],\"head_commit\":{\"id\":\"d77e2f697d806f71ab7dcf64a74cadfe5eb79598\",\"tree_id\":\"e46341b7cac3e821d68a73bf199efec27625ffcd\",\"distinct\":true,\"message\":\"alice: please: log: todos: Disable overlay to grab created issue URLs which is not yet fully validated\",\"timestamp\":\"2023-01-30T14:16:12-08:00\",\"url\":\"https://github.com/intel/dffml/commit/d77e2f697d806f71ab7dcf64a74cadfe5eb79598\",\"author\":{\"name\":\"John Andersen\",\"email\":\"johnandersenpdx@gmail.com\",\"username\":\"pdxjohnny\"},\"committer\":{\"name\":\"GitHub\",\"email\":\"noreply@github.com\",\"username\":\"web-flow\"},\"added\":[],\"removed\":[],\"modified\":[\"entities/alice/entry_points.txt\"]}}",
                "id": "http://localhost:8000/alice/posts/9a1d1dff-f25e-47a3-ac01-09e1f2e25ccd"
            },
            "id": "http://localhost:8000/alice/posts/155bb1d0-e74b-4995-892a-aaa472e25b3f"
        }
    ]
}
```

- Try loading content

```console
$ curl -s http://localhost:8000/alice/outbox | jq --unbuffered -r '.orderedItems[].object.content' | jq
```

```json
{
    "ref": "refs/heads/alice",
    "before": "8e02319e28b2f59c806e7f2a7b5ad202f51a2589",
    "after": "d77e2f697d806f71ab7dcf64a74cadfe5eb79598",
    "repository": {
        "id": 149512216,
        "node_id": "MDEwOlJlcG9zaXRvcnkxNDk1MTIyMTY=",
        "name": "dffml",
        "full_name": "intel/dffml",
        "private": false,
        "owner": {
            "name": "intel",
            "email": "webadmin@linux.intel.com",
            "login": "intel",
            "id": 17888862,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy",
            "avatar_url": "https://avatars.githubusercontent.com/u/17888862?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/intel",
            "html_url": "https://github.com/intel",
            "followers_url": "https://api.github.com/users/intel/followers",
            "following_url": "https://api.github.com/users/intel/following{/other_user}",
            "gists_url": "https://api.github.com/users/intel/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/intel/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/intel/subscriptions",
            "organizations_url": "https://api.github.com/users/intel/orgs",
            "repos_url": "https://api.github.com/users/intel/repos",
            "events_url": "https://api.github.com/users/intel/events{/privacy}",
            "received_events_url": "https://api.github.com/users/intel/received_events",
            "type": "Organization",
            "site_admin": false
        },
        "html_url": "https://github.com/intel/dffml",
        "description": "The easiest way to use Machine Learning. Mix and match underlying ML libraries and data set sources. Generate new datasets or modify existing ones with ease.",
        "fork": false,
        "url": "https://github.com/intel/dffml",
        "forks_url": "https://api.github.com/repos/intel/dffml/forks",
        "keys_url": "https://api.github.com/repos/intel/dffml/keys{/key_id}",
        "collaborators_url": "https://api.github.com/repos/intel/dffml/collaborators{/collaborator}",
        "teams_url": "https://api.github.com/repos/intel/dffml/teams",
        "hooks_url": "https://api.github.com/repos/intel/dffml/hooks",
        "issue_events_url": "https://api.github.com/repos/intel/dffml/issues/events{/number}",
        "events_url": "https://api.github.com/repos/intel/dffml/events",
        "assignees_url": "https://api.github.com/repos/intel/dffml/assignees{/user}",
        "branches_url": "https://api.github.com/repos/intel/dffml/branches{/branch}",
        "tags_url": "https://api.github.com/repos/intel/dffml/tags",
        "blobs_url": "https://api.github.com/repos/intel/dffml/git/blobs{/sha}",
        "git_tags_url": "https://api.github.com/repos/intel/dffml/git/tags{/sha}",
        "git_refs_url": "https://api.github.com/repos/intel/dffml/git/refs{/sha}",
        "trees_url": "https://api.github.com/repos/intel/dffml/git/trees{/sha}",
        "statuses_url": "https://api.github.com/repos/intel/dffml/statuses/{sha}",
        "languages_url": "https://api.github.com/repos/intel/dffml/languages",
        "stargazers_url": "https://api.github.com/repos/intel/dffml/stargazers",
        "contributors_url": "https://api.github.com/repos/intel/dffml/contributors",
        "subscribers_url": "https://api.github.com/repos/intel/dffml/subscribers",
        "subscription_url": "https://api.github.com/repos/intel/dffml/subscription",
        "commits_url": "https://api.github.com/repos/intel/dffml/commits{/sha}",
        "git_commits_url": "https://api.github.com/repos/intel/dffml/git/commits{/sha}",
        "comments_url": "https://api.github.com/repos/intel/dffml/comments{/number}",
        "issue_comment_url": "https://api.github.com/repos/intel/dffml/issues/comments{/number}",
        "contents_url": "https://api.github.com/repos/intel/dffml/contents/{+path}",
        "compare_url": "https://api.github.com/repos/intel/dffml/compare/{base}...{head}",
        "merges_url": "https://api.github.com/repos/intel/dffml/merges",
        "archive_url": "https://api.github.com/repos/intel/dffml/{archive_format}{/ref}",
        "downloads_url": "https://api.github.com/repos/intel/dffml/downloads",
        "issues_url": "https://api.github.com/repos/intel/dffml/issues{/number}",
        "pulls_url": "https://api.github.com/repos/intel/dffml/pulls{/number}",
        "milestones_url": "https://api.github.com/repos/intel/dffml/milestones{/number}",
        "notifications_url": "https://api.github.com/repos/intel/dffml/notifications{?since,all,participating}",
        "labels_url": "https://api.github.com/repos/intel/dffml/labels{/name}",
        "releases_url": "https://api.github.com/repos/intel/dffml/releases{/id}",
        "deployments_url": "https://api.github.com/repos/intel/dffml/deployments",
        "created_at": 1537391194,
        "updated_at": "2023-01-17T12:33:57Z",
        "pushed_at": 1675116972,
        "git_url": "git://github.com/intel/dffml.git",
        "ssh_url": "git@github.com:intel/dffml.git",
        "clone_url": "https://github.com/intel/dffml.git",
        "svn_url": "https://github.com/intel/dffml",
        "homepage": "https://intel.github.io/dffml/main/",
        "size": 602687,
        "stargazers_count": 201,
        "watchers_count": 201,
        "language": "Python",
        "has_issues": true,
        "has_projects": true,
        "has_downloads": true,
        "has_wiki": true,
        "has_pages": true,
        "has_discussions": true,
        "forks_count": 146,
        "mirror_url": null,
        "archived": false,
        "disabled": false,
        "open_issues_count": 387,
        "license": {
            "key": "mit",
            "name": "MIT License",
            "spdx_id": "MIT",
            "url": "https://api.github.com/licenses/mit",
            "node_id": "MDc6TGljZW5zZTEz"
        },
        "allow_forking": true,
        "is_template": false,
        "web_commit_signoff_required": false,
        "topics": [
            "ai-inference",
            "ai-machine-learning",
            "ai-training",
            "analytics",
            "asyncio",
            "dag",
            "data-flow",
            "dataflows",
            "datasets",
            "dffml",
            "event-based",
            "flow-based-programming",
            "frameworks",
            "hyperautomation",
            "libraries",
            "machine-learning",
            "models",
            "pipelines",
            "python",
            "swrepo"
        ],
        "visibility": "public",
        "forks": 146,
        "open_issues": 387,
        "watchers": 201,
        "default_branch": "main",
        "stargazers": 201,
        "master_branch": "main",
        "organization": "intel"
    },
    "pusher": {
        "name": "pdxjohnny",
        "email": "johnandersenpdx@gmail.com"
    },
    "organization": {
        "login": "intel",
        "id": 17888862,
        "node_id": "MDEyOk9yZ2FuaXphdGlvbjE3ODg4ODYy",
        "url": "https://api.github.com/orgs/intel",
        "repos_url": "https://api.github.com/orgs/intel/repos",
        "events_url": "https://api.github.com/orgs/intel/events",
        "hooks_url": "https://api.github.com/orgs/intel/hooks",
        "issues_url": "https://api.github.com/orgs/intel/issues",
        "members_url": "https://api.github.com/orgs/intel/members{/member}",
        "public_members_url": "https://api.github.com/orgs/intel/public_members{/member}",
        "avatar_url": "https://avatars.githubusercontent.com/u/17888862?v=4",
        "description": ""
    },
    "sender": {
        "login": "pdxjohnny",
        "id": 5950433,
        "node_id": "MDQ6VXNlcjU5NTA0MzM=",
        "avatar_url": "https://avatars.githubusercontent.com/u/5950433?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/pdxjohnny",
        "html_url": "https://github.com/pdxjohnny",
        "followers_url": "https://api.github.com/users/pdxjohnny/followers",
        "following_url": "https://api.github.com/users/pdxjohnny/following{/other_user}",
        "gists_url": "https://api.github.com/users/pdxjohnny/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/pdxjohnny/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/pdxjohnny/subscriptions",
        "organizations_url": "https://api.github.com/users/pdxjohnny/orgs",
        "repos_url": "https://api.github.com/users/pdxjohnny/repos",
        "events_url": "https://api.github.com/users/pdxjohnny/events{/privacy}",
        "received_events_url": "https://api.github.com/users/pdxjohnny/received_events",
        "type": "User",
        "site_admin": false
    },
    "created": false,
    "deleted": false,
    "forced": false,
    "base_ref": null,
    "compare": "https://github.com/intel/dffml/compare/8e02319e28b2...d77e2f697d80",
    "commits": [
        {
            "id": "d77e2f697d806f71ab7dcf64a74cadfe5eb79598",
            "tree_id": "e46341b7cac3e821d68a73bf199efec27625ffcd",
            "distinct": true,
            "message": "alice: please: log: todos: Disable overlay to grab created issue URLs which is not yet fully validated",
            "timestamp": "2023-01-30T14:16:12-08:00",
            "url": "https://github.com/intel/dffml/commit/d77e2f697d806f71ab7dcf64a74cadfe5eb79598",
            "author": {
                "name": "John Andersen",
                "email": "johnandersenpdx@gmail.com",
                "username": "pdxjohnny"
            },
            "committer": {
                "name": "GitHub",
                "email": "noreply@github.com",
                "username": "web-flow"
            },
            "added": [],
            "removed": [],
            "modified": [
                "entities/alice/entry_points.txt"
            ]
        }
    ],
    "head_commit": {
        "id": "d77e2f697d806f71ab7dcf64a74cadfe5eb79598",
        "tree_id": "e46341b7cac3e821d68a73bf199efec27625ffcd",
        "distinct": true,
        "message": "alice: please: log: todos: Disable overlay to grab created issue URLs which is not yet fully validated",
        "timestamp": "2023-01-30T14:16:12-08:00",
        "url": "https://github.com/intel/dffml/commit/d77e2f697d806f71ab7dcf64a74cadfe5eb79598",
        "author": {
            "name": "John Andersen",
            "email": "johnandersenpdx@gmail.com",
            "username": "pdxjohnny"
        },
        "committer": {
            "name": "GitHub",
            "email": "noreply@github.com",
            "username": "web-flow"
        },
        "added": [],
        "removed": [],
        "modified": [
            "entities/alice/entry_points.txt"
        ]
    }
}
```

- Okay, we now have the basis for federated downstream validation
- TODO
  - [ ] GitOps allowlist with priority for not AcivityPub fail-to-ban style
  - [ ] Watchers which just add to knowledge graph