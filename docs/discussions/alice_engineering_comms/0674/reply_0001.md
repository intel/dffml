## 2024-07-11 @pdxjohnny Engineering Logs

- Assistants API in Rust, ingest all links and docs and repos for Alice work.
  - Have Her refactor the existing docs in same writing style / voice
  - prompt: How would I use the openai assistants API async in rust to upload files, download git repos and upload all the files from all the HEADs of all the branches, and inform the AI of the relationships between this data using neo4j, and have it write documentation based on existing documentation using all it's knowledge? Use pyo3 to create a Python package which wraps the main function and passes neo4j connection paramters, repo url and temp directory for all the repos and the openai credentials, using pydantic classes on the python side

```bash
mkdir ~/Documents/python/scitt-api-emulator-rust-policy-engine
cd ~/Documents/python/scitt-api-emulator-rust-policy-engine
python -m venv .venv \
  && . .venv/bin/activate \
  && python -m pip install -U pip setuptools wheel \
  && python -m pip install maturin \
  && maturin init --bindings pyo3 \
  && maturin develop
```

- rust compiler errors as json
  - feedback loop
  - https://rustc-dev-guide.rust-lang.org/diagnostics.html#json-diagnostic-output
    - > `rustc ... --error-format json`
- https://duckduckgo.com/?q=site%3Amaturin.rs+rustc&ia=web
  - https://www.maturin.rs/config#cargo-options

[![asciicast](https://asciinema.org/a/667688.svg)](https://asciinema.org/a/667688)

- https://github.com/openai/GPTs-are-GPTs/blob/36af7ac78d218158fd2070bd8775c86a99f222da/code/gpts_are_gpts_script2.ipynb
  - > Something weird (Monorepo requires Python 3.11 or later) has happened while importing numpy.exceptions.
    - *deranged Pythonic laughter*
- https://github.com/pdxjohnny/scitt-api-emulator/pull/7
- echo We want an async python lib that is bindings to rust We'll implement the policy engine within rust

[![asciicast](https://asciinema.org/a/667695.svg)](https://asciinema.org/a/667695)

- Let's hook up the policy engine with check suites to compile the rust code
  - Later let's hook it up to forgejo
- Got workflow structs compiling
  - https://github.com/pdxjohnny/scitt-api-emulator/commit/612b5c498c2a9244001f9be0a092d706945bdef6

[![asciicast](https://asciinema.org/a/667709.svg)](https://asciinema.org/a/667709)

- https://docs.rs/pyo3-log/latest/pyo3_log/#interaction-with-python-gil
- TODO
  - [x] Clean compile and run and validation of policy engine request objects