## 2022-07-20 @pdxjohnny Engineering Logs

- TODO
  - [x] Get involved in SCITT
    - [ ] Meetings
      - https://docs.google.com/document/d/1vf-EliXByhg5HZfgVbTqZhfaJFCmvMdQuZ4tC-Eq6wg/edit#
      - Weekly Monday at 8 AM Pacific
      - https://armltd.zoom.us/j/99133885299?pwd=b0w4aGorRkpjL3ZHa2NPSmRiNHpXUT09
    - [x] Mailing list
      - https://www.ietf.org/mailman/listinfo/scitt
      - https://mailarchive.ietf.org/arch/browse/scitt/
    - [ ] Slack
      - https://mailarchive.ietf.org/arch/msg/scitt/PbvoKOX996cNHJEOrjReaNlum64/
      - Going to email Orie Steele orie (at) transmute.industries to ask for an invite.
  - [x] Kick off OSS scans
    - Targeting collaboration with CRob on metrics insertion to OpenSSF DB
  - [ ] Finish Q3 plans (Gantt chart, meeting templates, etc.)
    - Generate template for auto creation to fill every meeting / fillable pre-meeting
  - [ ] Overlay to `alice shouldi contribute` to create git repos when found from forks of PyPi packages
    - [ ] Associated tutorial
      - [ ] Linked from `README`
  - [ ] Finish out `alice please contribute recommended community standards`
        dynamic opimp for meta issue body creation
    - [ ] Associated tutorial
      - [ ] Linked from `README` and `CONTRIBUTING`
- References
  - https://static.sched.com/hosted_files/ossna2022/9b/presentation.pdf
    - > We're starting to put everything in registries, container images, signatures, SBOMs, attestations, cat pictures, we need to slow down. Our CI pipelines are designed to pass things as directories and files between stages, why aren't we doing this with our container images? OCI already defines an Image Layout Specification that defines how to structure the data on disk, and we should normalize how this is used in our tooling. This talk looks at the value of using the OCI Layout spec, what you can do today, what issues we're facing, and a call to action for more standardization between tooling in this space.

---

Unsent

To: Jun and Mike and Yan

I commented on the OpenSFF Stream 8 doc recommending that DIDs be looked at
as a way to exchange vulnerability information.

We've been looking potentially at a hybrid DID plus rekor
architecture (DIDs eventually as a proxy to) 

References:
- https://github.com/sigstore/rekor
