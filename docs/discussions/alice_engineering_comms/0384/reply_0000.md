- https://github.com/slsa-framework/slsa-github-generator/issues/358#issuecomment-1711894740
  - https://github.com/slsa-framework/slsa-github-generator/issues/131
  - Workflows in one repo but not another
    - `$ diff -u <(git ls-tree -r test -- .github/workflows/ | sed -e 's/.*\.github/.github/') <(git ls-tree -r main -- .github/workflows/ | sed -e 's/.*\.github/.github/') | grep -E '^-' | tail -n +2 | sed -e 's/^-//'`
- https://slsa.dev/blog/2022/08/slsa-github-workflows-generic-ga
- https://slsa.dev/spec/v1.0/future-directions
  - > The initial [draft version (v0.1)](https://slsa.dev/spec/v0.1/requirements) of SLSA defined a "SLSA 4" that included the following requirements, which may or may not be part of a future Build L4:
    >
    > - Pinned dependencies, which guarantee that each build runs on exactly the same set of inputs.
    > - Hermetic builds, which guarantee that no extraneous dependencies are used.
    > - All dependencies listed in the provenance, which enables downstream verifiers to recursively apply SLSA to dependencies.
    > - Reproducible builds, which enable other build platforms to corroborate the provenance.