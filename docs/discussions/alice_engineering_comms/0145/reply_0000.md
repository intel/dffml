- https://twitter.com/hausman_k/status/1613544873050931200
  - good summary of chain of thought work in 2022
- https://twitter.com/SergioRocks/status/1613554012627820544
  - AI assisted dev recommendations
- Lucidity oh lucidity
  - https://danijar.com/project/dreamerv3/
- An Image, stenography on non-re-encoded
  - https://mastodon.social/@bbbbbr@mastodon.gamedev.place/109672633992508412
- https://github.com/google/balloon-learning-environment
  - > https://mobile.twitter.com/danijarh: Replying to [@pcastr](https://mobile.twitter.com/pcastr) Hi Pablo, thanks! Not specific to pixels at all, it supports images, vectors, and combinations of them as input. For example, DreamerV3 outperforms DDPG, SAC, D4PG, MPO, DMPO on continuous control from states.
  - https://twitter.com/danijarh/status/1613503430135365632

```console
$ dffml service dev export alice.shouldi.contribute.cicd:cicd_library.op
```

```json
{
    "inputs": {
        "cicd_action_library": {
            "links": [
                [
                    [
                        "name",
                        "bool"
                    ],
                    [
                        "primitive",
                        "bool"
                    ]
                ]
            ],
            "name": "IsCICDGitHubActionsLibrary",
            "primitive": "bool"
        },
        "cicd_jenkins_library": {
            "links": [
                [
                    [
                        "name",
                        "bool"
                    ],
                    [
                        "primitive",
                        "bool"
                    ]
                ]
            ],
            "name": "IsCICDJenkinsLibrary",
            "primitive": "bool"
        }
    },
    "name": "alice.shouldi.contribute.cicd:cicd_library",
    "outputs": {
        "result": {
            "links": [
                [
                    [
                        "name",
                        "dict"
                    ],
                    [
                        "primitive",
                        "map"
                    ]
                ]
            ],
            "name": "CICDLibrary",
            "primitive": "dict"
        }
    },
    "retry": 0,
    "stage": "output"
}
```