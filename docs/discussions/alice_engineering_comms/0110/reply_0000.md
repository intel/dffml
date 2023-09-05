## 2022-12-08 @pdxjohnny Engineering Logs

- Racing laptop setup and Android Container VM based outlook sign in to join in progress meetings
- Laptop broken
- New laptop is here
- Need old laptop to activate new laptop...
  - Calling TAC
    - Call dropped
  - Initiating setup
    - Three finger swipe bypasses fullscreen lock of setup
    - Moved client config to new desktop, we're back in!
      - Outlook doesn't work...
      - Teams keeps dropping...
      - Teams does not show video or allow for chat. lol
- Laptop works for audio calls, whatever
- https://github.com/google/android-emulator-container-scripts
  - https://github.com/google/android-emulator-container-scripts/search?q=web+container
    - This looks very promising for being a long awaited way to remotely view QEMU
  - Docker compose also has a concept of overlays
  - https://asciinema.org/a/544103
  - https://asciinema.org/a/544110
  - https://asciinema.org/a/544117
- Failures to bellow instructions: 1
  - `while alignment_threshold_last < ctx.alignment_threshold_fulfilled: goto deref_prev_instruction_ptr()`
    - Laptop failure doesn't count

```console
; job=$(qsub -l nodes=1:gpu:ppn=2 -d . github-actions-runner.sh); done=1; while test "$done"; do done=$(qstat -n -1 | grep "$job" | wc -l); sleep 0.2; done; clear; tail -n 10000 github-actions-runner.sh*
```

- TODO
  - [ ] hangouts callcenter -> https://voice.google.com/u/0/voicemail via CLI whisper stream pipe output webrtc alice shell style stream processing
  - [ ] Generic setup and teardown actions with setup as audit, have alice audit audit
  - [ ] https://hyperonomy.files.wordpress.com/2022/12/didcomm-agent-architecture-reference-model-0.25f.pdf
  - [ ] https://github.com/megagonlabs/ditto
  - [x] Got runner spun in DevCloud
    - [operation: run datafow: DevCloud intel/dffml#1247: 2022-12-08 @pdxjohnny Engineering Logs](https://github.com/intel/dffml/issues/1247#issuecomment-1343102902)
      - :turtle: [*so if we get more compute, you know, then you know... then we can use more compute*](https://www.youtube.com/watch?v=dI1oGv7K21A&list=PLtzAOVTpO2jYt71umwc-ze6OmwwCIMnLw&t=194s)
  - [ ] Automate spin up via bootstrapping github actions flow