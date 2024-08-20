## 2024-07-04 @pdxjohnny Engineering Logs

- https://docs.mindsdb.com/sdks/python/installation
- https://docs.mindsdb.com/setup/custom-config
- https://docs.mindsdb.com/setup/environment-vars
- https://docs.mindsdb.com/integrations/app-integrations/github
- https://docs.mindsdb.com/integrations/ai-engines/openai
- https://docs.mindsdb.com/integrations/ai-engines/rag
- https://docs.mindsdb.com/integrations/ai-engines/langchain
- https://docs.mindsdb.com/contribute/install#install-mindsdb-for-development
- Fallout new vegas as an RTS

```bash
python -m pip install -U mindsdb_sdk mindsdb
sudo caddy add-package github.com/greenpau/caddy-security
```


- TODO
  - [ ] Fix scorecard stuff
  - [ ] Dev env via API
    - [ ] #1207
      - [ ] "You are Alice, what do you have access to"
    - [ ] Add to dotfiles `forge-install.sh`
      - [ ] Some kind of fuse to oras layers thing
      - [ ] Coder deployment
      - [ ] Asciinema server deployment
        - [ ] https://docs.asciinema.org/manual/server/self-hosting/
      - [ ] local llm rust mistral execution engine or something
      - [ ] Headless (with display capability) chrome browser
        - [ ] Async Playwright
      - [ ] SCITT Policy Engine CWT Rebase
        - [ ] Federation
      - [ ] GUAC
      - [ ] kvm capable kubernetes in docker (kata)
      - [ ] blob storage
        - [ ] minio
      - [ ] SMTP
        - [x] prompt: Is there a production quality rust [memory safe language] SMTP server you know of?
          - https://stalw.art/docs/install/linux
      - [ ] FaaS
        - [ ] Patches and train of thought + history +_ asciiema to changelog and docs (as patches)
  - [ ] Start from `agi.py` event based approach
    - [ ] Focus on being able to live view Alice as she does development and jump in at any point
  - [ ] Format (reuse policy engine with stack frames captured as checkpoint restore?) to track train of thought
    - [ ] SCITT protected json-ld + ORAS trampoline resource loader