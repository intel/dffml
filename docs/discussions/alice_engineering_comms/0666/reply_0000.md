- git + SCITT policy engine as CI / local CI / federated local instance pre-check before federating aka running workflows

```bash
# Commit should check that you have a SCITT receipt for your CI run of the `r-c/` for this commit (release canidate of commit, CI / validation against this commit)
# We should use DAG caching to determine commit ability, cannot commit unless CI has passed
# This way we can only commit working code unless we use --expect-failures
git commit --expect-failures