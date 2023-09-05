## 2022-10-25 Alice Initiative welcome aboard!

- Harsh joining us to do some Python package analysis work
- Alice thread: https://github.com/intel/dffml/discussions/1406?sort=new
- This work feeds into the following tutorial
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0001_coach_alice/0001_down_the_dependency_rabbit_hole_again.md
- [shouldi: deptree: Create dependency tree of project · Issue #596 · intel/dffml](https://github.com/intel/dffml/issues/596)
  - https://github.com/intel/dffml/commits/shouldi_dep_tree
  - > The idea behind the work that was done so far in the above branch was to produce the full dependency tree for a given python package.
- Documentation writing process
  - https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0004_writing_the_wave.md#vision
- Contributing Documentation
  - https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst
- Troubleshooting — DFFML fd401e426 documentation
  - https://intel.github.io/dffml/main/troubleshooting.html#entrypointnotfound
- Next steps
  - Harsh will first focus on filling out the other two functions with unit tests for different file contents
    - These functions / files can be standalone at first, we can integrate later.
      - https://github.com/intel/dffml/blob/alice/entities/alice/CONTRIBUTING.rst#writing-an-overlay
    - Harsh to ping John as needed.
    - Harsh to comment in issue with commands run and errors and so forth so we can copy pate into the associated tutorial later.
      - Plans for automation of documentation writing: https://github.com/intel/dffml/commit/74781303fae19b03326878d184a49ac93543749c?short_path=76e9bfe#diff-76e9bfe1c05d4426559fada22595ca1f9a76fd0fc98609dfbbde353d10fa77db

https://github.com/intel/dffml/blob/0a2e053f5f8e361054f329a3f763982fb1e4d1f7/examples/shouldi/tests/test_dep_tree.py#L36-L71