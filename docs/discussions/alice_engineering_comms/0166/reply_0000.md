## 2023-02-02 @pdxjohnny Engineering Logs

- Don't worry about DIDs, you can put ActivityPub over DID methods instead of HTTP later
- https://cdk8s.io/
- https://github.com/permitio/OPToggles
- https://github.com/chef/automate/tree/master/components/authz-service#authz-with-opa
- https://docs.github.com/en/rest/git?apiVersion=2022-11-28#about-git-database
  - https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-your-git-database?apiVersion=2022-11-28
  - DID/ActivityPub/ATP analogy API?
- https://wijmans.xyz/publication/eom/
  - Vol 2: Cartography
- https://github.com/asciinema/asciinema-server/wiki/Installation-guide
  - Okay fuck yes, just closed the loop, then we bdrige this to activitypub, stream of consiousness is a go
    - Daniel didn't reply about using DWNs, and DID Comm agents look good as a next step there.
- ssh git push to deploy anything
  - proxy does translation into take push as single commit of dir (could piggyback off pgp or cowign or other commit signing as well)
  - 
- open architecture
  - context-to-context analysis
    - Analysis based on `Input.origin`, ensure `Input` flow through operations ensures validation for
      - workflow-to-workflow
      - workflow-to-job
      - job-to-job
        - Artifacts
      - job-to-action
- Investigate GitHub approved workflows per env
  - https://docs.github.com/en/actions/managing-workflow-runs/reviewing-deployments#about-required-reviews-in-workflows
- https://git-scm.com/docs/git-filter-branch#_examples
- Similar to parse_ast.py Python ast example, export all groovy functions to `features`
- https://github.com/intel/dffml/pull/1061#discussion_r1095079133
  - We don't need to nessicarily update status checks via API, can just have a pipeline within PR workflows which says this other PR must be merged in an upstrema or downstrema before this one can auto merge