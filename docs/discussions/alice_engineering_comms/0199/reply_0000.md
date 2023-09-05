## 2023-03-07 @pdxjohnny Engineering Logs

- https://www.fastcompany.com/90859722/you-can-poison-ai-datasets-for-just-60-a-new-study-shows
- https://github.com/Azure-Samples/active-directory-verifiable-credentials-python
- Cleaned up random forks used for testing
- Investigating existing activitypub code within forgejo
  - To facilitate comms (Continuous Delivery of Living Threat Models) as part of Alice's Stream of Consciousness
    - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md
- https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md?plain=1

[![use-the-source](https://img.shields.io/badge/use%20the-source-blueviolet)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#use-the-source-)

```console
$ git status
On branch v1.19/forgejo-ci
Your branch is up to date with 'origin/v1.19/forgejo-ci'.

nothing to commit, working tree clean
$ git log -n 1
commit 823ab34c64b275bf57fa60fef25a67338d8cb26e (HEAD -> v1.19/forgejo-ci, origin/v1.19/forgejo-ci)
Author: Loïc Dachary <loic@dachary.org>
Date:   Mon Feb 20 23:17:52 2023 +0100

    [CI] set PASSWORD_HASH_ALGO = argon2 for integration tests
    
    (cherry picked from commit 1d7ce2a39c841e77492ef08c0e86c3544ecca88d)
    (cherry picked from commit 1abfc0c0a17a429102ba5f70b874263cc7b2ecf8)
$ git grep -i activitypub
CHANGELOG.md:  * User keypairs and HTTP signatures for ActivityPub federation using go-ap (#19133)
assets/go-licenses.json:    "name": "github.com/go-ap/activitypub",
assets/go-licenses.json:    "path": "github.com/go-ap/activitypub/LICENSE",
go.mod:	github.com/go-ap/activitypub v0.0.0-20221209114049-1ceafda50f9f
go.sum:github.com/go-ap/activitypub v0.0.0-20221209114049-1ceafda50f9f h1:UV5kupaU8AP8g8Bbsn53q87XCufW/E8wvnTHDKqjoR4=
go.sum:github.com/go-ap/activitypub v0.0.0-20221209114049-1ceafda50f9f/go.mod h1:1oVD0h0aPT3OEE1ZoSUoym/UGKzxe+e0y8K2AkQ1Hqs=
models/user/setting_keys.go:	// UserActivityPubPrivPem is user's private key
models/user/setting_keys.go:	UserActivityPubPrivPem = "activitypub.priv_pem"
models/user/setting_keys.go:	// UserActivityPubPubPem is user's public key
models/user/setting_keys.go:	UserActivityPubPubPem = "activitypub.pub_pem"
modules/activitypub/client.go:package activitypub
modules/activitypub/client_test.go:package activitypub
modules/activitypub/client_test.go:func TestActivityPubSignedPost(t *testing.T) {
modules/activitypub/main_test.go:package activitypub
modules/activitypub/user_settings.go:package activitypub
modules/activitypub/user_settings.go:	settings, err = user_model.GetSettings(user.ID, []string{user_model.UserActivityPubPrivPem, user_model.UserActivityPubPubPem})
modules/activitypub/user_settings.go:		if err = user_model.SetUserSetting(user.ID, user_model.UserActivityPubPrivPem, priv); err != nil {
modules/activitypub/user_settings.go:		if err = user_model.SetUserSetting(user.ID, user_model.UserActivityPubPubPem, pub); err != nil {
modules/activitypub/user_settings.go:		priv = settings[user_model.UserActivityPubPrivPem].SettingValue
modules/activitypub/user_settings.go:		pub = settings[user_model.UserActivityPubPubPem].SettingValue
modules/activitypub/user_settings_test.go:package activitypub
modules/structs/activitypub.go:// ActivityPub type
modules/structs/activitypub.go:type ActivityPub struct {
routers/api/v1/activitypub/person.go:package activitypub
routers/api/v1/activitypub/person.go:	"code.gitea.io/gitea/modules/activitypub"
routers/api/v1/activitypub/person.go:	ap "github.com/go-ap/activitypub"
routers/api/v1/activitypub/person.go:	// swagger:operation GET /activitypub/user/{username} activitypub activitypubPerson
routers/api/v1/activitypub/person.go:	//     "$ref": "#/responses/ActivityPub"
routers/api/v1/activitypub/person.go:	link := strings.TrimSuffix(setting.AppURL, "/") + "/api/v1/activitypub/user/" + ctx.ContextUser.Name
routers/api/v1/activitypub/person.go:	publicKeyPem, err := activitypub.GetPublicKey(ctx.ContextUser)
routers/api/v1/activitypub/person.go:	ctx.Resp.Header().Add("Content-Type", activitypub.ActivityStreamsContentType)
routers/api/v1/activitypub/person.go:	// swagger:operation POST /activitypub/user/{username}/inbox activitypub activitypubPersonInbox
routers/api/v1/activitypub/reqsignature.go:package activitypub
routers/api/v1/activitypub/reqsignature.go:	"code.gitea.io/gitea/modules/activitypub"
routers/api/v1/activitypub/reqsignature.go:	ap "github.com/go-ap/activitypub"
routers/api/v1/activitypub/reqsignature.go:	req.Header("Accept", activitypub.ActivityStreamsContentType)
routers/api/v1/api.go:	"code.gitea.io/gitea/routers/api/v1/activitypub"
routers/api/v1/api.go:			m.Group("/activitypub", func() {
routers/api/v1/api.go:					m.Get("", activitypub.Person)
routers/api/v1/api.go:					m.Post("/inbox", activitypub.ReqHTTPSignature(), activitypub.PersonInbox)
routers/api/v1/misc/nodeinfo.go:		Protocols: []string{"activitypub"},
routers/api/v1/swagger/activitypub.go:// ActivityPub
routers/api/v1/swagger/activitypub.go:// swagger:response ActivityPub
routers/api/v1/swagger/activitypub.go:type swaggerResponseActivityPub struct {
routers/api/v1/swagger/activitypub.go:	Body api.ActivityPub `json:"body"`
routers/web/webfinger.go:		appURL.String() + "api/v1/activitypub/user/" + url.PathEscape(u.Name),
routers/web/webfinger.go:			Href: appURL.String() + "api/v1/activitypub/user/" + url.PathEscape(u.Name),
templates/swagger/v1_json.tmpl:    "/activitypub/user/{username}": {
templates/swagger/v1_json.tmpl:          "activitypub"
templates/swagger/v1_json.tmpl:        "operationId": "activitypubPerson",
templates/swagger/v1_json.tmpl:            "$ref": "#/responses/ActivityPub"
templates/swagger/v1_json.tmpl:    "/activitypub/user/{username}/inbox": {
templates/swagger/v1_json.tmpl:          "activitypub"
templates/swagger/v1_json.tmpl:        "operationId": "activitypubPersonInbox",
templates/swagger/v1_json.tmpl:    "ActivityPub": {
templates/swagger/v1_json.tmpl:      "description": "ActivityPub type",
templates/swagger/v1_json.tmpl:    "ActivityPub": {
templates/swagger/v1_json.tmpl:      "description": "ActivityPub",
templates/swagger/v1_json.tmpl:        "$ref": "#/definitions/ActivityPub"
tests/integration/api_activitypub_person_test.go:	"code.gitea.io/gitea/modules/activitypub"
tests/integration/api_activitypub_person_test.go:	ap "github.com/go-ap/activitypub"
tests/integration/api_activitypub_person_test.go:func TestActivityPubPerson(t *testing.T) {
tests/integration/api_activitypub_person_test.go:		req := NewRequestf(t, "GET", fmt.Sprintf("/api/v1/activitypub/user/%s", username))
tests/integration/api_activitypub_person_test.go:		assert.Regexp(t, fmt.Sprintf("activitypub/user/%s$", username), keyID)
tests/integration/api_activitypub_person_test.go:		assert.Regexp(t, fmt.Sprintf("activitypub/user/%s/outbox$", username), person.Outbox.GetID().String())
tests/integration/api_activitypub_person_test.go:		assert.Regexp(t, fmt.Sprintf("activitypub/user/%s/inbox$", username), person.Inbox.GetID().String())
tests/integration/api_activitypub_person_test.go:func TestActivityPubMissingPerson(t *testing.T) {
tests/integration/api_activitypub_person_test.go:		req := NewRequestf(t, "GET", "/api/v1/activitypub/user/nonexistentuser")
tests/integration/api_activitypub_person_test.go:func TestActivityPubPersonInbox(t *testing.T) {
tests/integration/api_activitypub_person_test.go:		user1url := fmt.Sprintf("%s/api/v1/activitypub/user/%s#main-key", srv.URL, username1)
tests/integration/api_activitypub_person_test.go:		c, err := activitypub.NewClient(user1, user1url)
tests/integration/api_activitypub_person_test.go:		user2inboxurl := fmt.Sprintf("%s/api/v1/activitypub/user/%s/inbox", srv.URL, username2)
tests/integration/schemas/nodeinfo_2.1.json:          "activitypub",
tests/integration/webfinger_test.go:	assert.ElementsMatch(t, []string{user.HTMLURL(), appURL.String() + "api/v1/activitypub/user/" + url.PathEscape(user.Name)}, jrd.Aliases)
```

- Conceptual analogies of #1315 / ActivityPub security.txt methodology for graph traversal
  - Similar to GitHub discussion
    - Each day is a thread from an activitypub group
      - grep: time: now
      - Towards context local time
    - An entity can reply to the group (or another entity) and use that as their daily log, they add the group's daily log as a reply. This is like how we link issues and if we'll have them auto backref to the discussion thread using downstream watchers. This is the same way we can facilitate the review system notifications, the SARIF CD eventing.
      - https://github.com/cli/cli/issues/5659#issuecomment-1138028169
- https://grafeas.io/blog/introducing-grafeas
  - > Decentralization and continuous delivery: The move to decentralize engineering and ship software continuously (e.g., “push on green”) accelerates development velocity, but makes it difficult to follow best practices and standards.
  - Grafeas might have schema bits that would be good to look to source into F3 if licensing permits
  - https://www.infoq.com/presentations/supply-grafeas-kritis/
  - Keynote: Software Supply Chains for Devops - Aysylu Greenberg, Google
    - https://www.youtube.com/watch?v=2Wl0hoEt47E
  - Keynote: Project Trebuchet: How SolarWinds is Using Open Source to Secure Their Supply Chain in the Wake of the Sunburst Hack - Trevor Rosen, SolarWinds
    - https://youtu.be/1-tMRxqMwTQ?t=1413
      - Also talks about having a second build system building in parallel
      - They also do vuln analysis with OPA
        - This looks aligned to what we're trying to do, only we want federation protocol event space for interoperability rather than cloudevents
- https://tekton.dev/docs/pipelines/hermetic/
- https://github.com/tektoncd/community/issues/435
- https://github.com/tektoncd/experimental/pull/754
- https://github.com/tektoncd/community/blob/main/teps/0008-support-knative-service-for-triggers-eventlistener-pod.md
  - **ALINGED**
    - KCP CRDs
- https://github.com/tektoncd/triggers/pull/958
  - Should we just go straight to the source and do the KCP/k8s manifest shim style translation?
- https://github.com/w3c-ccg/traceability-interop/issues/468#issuecomment-1459024175
- https://github.com/tektoncd/experimental/blob/ce7bf94997343f44e46b0f7290573968af81df34/cloudevents/README.md
- https://cdevents.dev/
- https://github.com/cdevents/spec/blob/8e8b3e0c4bf7656abd32a258a4a86b97e2d4d6f5/spec.md
  - 2022-10-24: spec v0.1.1 released
- https://github.com/afrittoli
- Continuous Delivery Foundation (CDF) 2023
  - https://twitter.com/LoriLorusso/status/1584917240834670592/photo/2
  - > ![image](https://user-images.githubusercontent.com/5950433/223585282-09b2c638-76e7-4540-ab40-0fae0cd428e5.png)
- https://github.com/guacsec/guac/issues/251
- https://github.com/guacsec/guac/issues/460
  - https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/http-webhook.md
  - We could translate this into the federated CD event space
- https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md
- https://github.com/cloudevents/spec/pull/712
- https://github.com/cloudevents/spec/issues/1146#issuecomment-1404225644
- https://github.com/cloudevents/spec/issues/1162
- https://gist.github.com/clemensv/b7d4c7e1f93f88021fa2f0edc0dee459
  - `Channel Identifier` in our case is the posts we include in `replies` or via `inReplyTo`
- https://github.com/cloudevents/spec/issues/1146#issuecomment-1403630146
  - Conversion of events
- https://www.drogue.io/
- https://github.com/cloudevents/spec/issues/830
- https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/severity.md
- https://github.com/cloudevents/spec/blob/3877083f8396cfb01b7b3e8adf1738f248af3aff/subscriptions/subscriptions-openapi.yaml#L209
  - Can we introduce ActivityPub here?
- https://github.com/cdevents/spec/blob/main/cloudevents-binding.md
- https://github.com/cdevents/spec/blob/main/spec.md#cdevents-custom-data
- https://github.com/cdevents/spec/blob/main/continuous-deployment-pipeline-events.md
- https://github.com/cdfoundation/sig-mlops/blob/main/roadmap/2022/MLOpsRoadmap2022.md
- https://github.com/epec254/gpt-intuition
- https://github.com/evidentlyai/evidently
- https://github.com/w3c-ccg/traceability-interop/issues/485#issuecomment-1458700562
- TODO
  - [ ] GUAC federated event integration
    - https://docs.google.com/document/d/15Kb3I3SWhq-9_R7WYhSjsIxn_FykYgPyFlQWlLgF4fA/edit
    - https://docs.google.com/document/d/1BUEi7q2i-KXlAhsh1adYvL1fkWN-q8FrgLyEre7c5kg/edit?resourcekey=0-02sC5-9IbTfwJckze_CDQw#
      - Very aligned
  - [ ] GraphQL-LD with iter over outputs of flows converted from manifests into LDF
  - [ ] Update OA WG chapters on federation
    - https://codeberg.org/forgejo-contrib/discussions/issues/12
      - https://codeberg.org/forgejo/runner/issues/5#issuecomment-826244