## 2023-02-24 @pdxjohnny Engineering Logs

- Something about the pinning #906
  - [Rolling Alice: Architecting Alice: Introduction and Context](https://github.com/intel/dffml/tree/alice/docs/tutorials/rolling_alice/0000_architecting_alice#rolling-alice-volume-0-introduction-and-context)
    - Together we'll build Alice the AI software architect. We'll be successful when Alice successfully maintains a codebase as the only maintainer for a year. *Debugging issues, writing fixes, reviewing code, accepting pull requests, refactoring the code base post PR merge, dealing with vulnerabilities, cutting releases, maintaining release branches, and completing development work in alignment with the plugin's living threat model* (leveraging the [Open Architecture](https://github.com/intel/dffml/blob/alice/docs/arch/0009-Open-Architecture.rst)). *She will modify, submit pull requests to, and track upstreaming of patches to her dependencies to achieve the cleanest architecture possible.* We'll interact with her as we would any other remote developer.
  - Fork
  - Work
  - PR to upstream with pin
    - #1061 this is the change of manifest
  - Does it adhear to THREATS.md straregic plans and principles? Ship it! (auto merge PR)
- Want feedback on your PRs? (or in flight dev trains of thought, )
  - Publish to activitypub!
  - In SSI fediverse, 2nd party feedback finds YOU!
    - https://github.com/pdxjohnny/pdxjohnny.github.io/issues/2
    - OpenVEX
    - #1061
    - https://github.com/LAION-AI/Open-Assistant/pull/1483/files#r1117649911
      - Reached out to this community again since we know about them already
      - We've been playing with ActivityPub as one option to enable multiple workers to provide feedback via `inReplyTo` and threads, mimicking human behavior. Wasn't sure where else to post so posting here. The hope is that our models can collectively respond, and the user or users AI agent can sift through and find the responses that are most helpful to them within the context of the conversation. Something like ActivityPub based communication (Rapunzel, ATProto come to mind) would enable folks AI's to collaboratively provide their responses.
        - References
          - [WIP: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/fd2828090482fe63a30a7ddd9e91bdb78892a01e/openssf_metrics.md#activitypub-extensions-for-securitytxt)
  - [2023-02-15 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-4983602) `job_url` -> GitHub API -> active PRs for commit
- Manifests assist with checkpoint and restore SLSA 4
  - TDX live migration
  - KERI watchers are all you need (they themselves are a "SCITT instance")
    - Thank you Ned! 🥳🥳🥳
      - Should have just asked him this explicitly months ago...
    - https://identity.foundation/keri/did_methods/#key-event-receipt-log
    - https://github.com/decentralized-identity/keri/blob/master/kids/kid0009.md
    - https://github.com/WebOfTrust/keripy/blob/development/tests/app/test_watching.py
    - https://github.com/WebOfTrust/keria/blob/main/tests/core/test_authing.py
    - https://github.com/WebOfTrust/keripy/blob/development/src/keri/demo/demo.md

```diff
diff --git a/entities/alice/entry_points.txt b/entities/alice/entry_points.txt
index 49426b5..9277df0 100644
--- a/entities/alice/entry_points.txt
+++ b/entities/alice/entry_points.txt
@@ -30,6 +30,7 @@ OverlayActionsValidator                        = dffml_operations_innersource.ac
 OverlayNPMGroovyLint                           = dffml_operations_innersource.npm_groovy_lint:npm_groovy_lint
 OverlayNPMGroovyLintStartCodeNarcServer        = dffml_operations_innersource.npm_groovy_lint:start_code_narc_server
 OverlayNPMGroovyLintStopCodeNarcServer         = dffml_operations_innersource.npm_groovy_lint:stop_code_narc_server
+OverlayRecommendedCommunityStandards           = alice.please.log.todos.todos:AlicePleaseLogTodosDataFlowRecommendedCommnuityStandardsGitHubIssues

 [dffml.overlays.alice.please.log.todos]
 OverlayCLI                                     = alice.please.log.todos.todos:OverlayCLI
```

- https://github.com/intel/dffml/issues/1394
- **HUZZAH!** IT WORKED!
- https://github.com/intel/dffml/issues/1440
- TODO
  - [ ] [Rolling Alice: Coach Alice: Strategic Principles as Game Plan](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0003_strategic_principles_as_game_plan.md)
    - https://github.com/issues?q=is%3Aopen+is%3Aissue+archived%3Afalse+sort%3Arelevance-desc+repo%3Aintel%2Fdffml+author%3Aaliceoa
    - https://github.com/TomWright/mermaid-server
      - For static dumps
  - [ ] `alice please log todos` overlays enabled on `alice shouldi contribute` for feedback
    - [ ] Dataflow output where `Input.value` becomes the operation name (grep recent logs)
    - [ ] `alice please log todos` as overlay
      - See diff, stuck on https://github.com/intel/dffml/issues/1394
  - [ ] Talk to Ryan per recent CVE Bin Tool meeting notes
    - Overlays for please contribute https://github.com/ossf/scorecard-action if badge not found