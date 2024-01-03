## 2022-10-10 @pdxjohnny Engineering Logs

- OS DecentrAlice: dracut fstab
- [Volume 0: Chapter 5: Stream of Consciousness](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0005_stream_of_consciousness.md)
- [2022-10-10 IETF SCITT Weekly](https://github.com/intel/dffml/discussions/1406?sort=new#discussioncomment-3840337)
- [Dump GitHub Discussion to JSON 2022-10-10T17:58:31+00:00](https://gist.github.com/pdxjohnny/9f3dc18f0a42d3107aaa2363331d8faa)
- https://gist.github.com/pdxjohnny/a0dc3a58b4651dc3761bee65a198a80d#file-run-vm-sh-L174-L200
- https://gist.github.com/pdxjohnny/b5f757eee43d84b1600dce7896230c37
- https://github.com/systemd/systemd/issues/16714
- https://forums.raspberrypi.com/viewtopic.php?p=1632011
- https://en.wikipedia.org/wiki/Fstab
- KERI
  - https://github.com/WebOfTrust/vLEI
  - https://github.com/GLEIF-IT/sally
  - https://github.com/WebOfTrust/keripy
    - https://github.com/WebOfTrust/keripy/blob/development/ref/getting_started.md
  - https://github.com/decentralized-identity/keri-dht-py
  - https://github.com/orgs/WebOfTrust/projects/2
  - https://github.com/WebOfTrust/keripy/blob/development/ref/getting_started.md#direct-mode
- A Shell for a Ghost
  - https://rich.readthedocs.io/en/latest/live.html
- DID Method Registry
  - Open Architecture and Alice
    - Entrypoints as DIDs for dataflows and overlays, key / id is hash of system context to be executaed with negoation in cached state snapshots embeded into system ocontext (static or data flow seed)
      - GraphQL and something like Orie was doing with Cypher for visualization and or use JSON crack first for editing to allow for credential manifest definition and verification for overlays selected to load from network(s), the active lines of communication we have open at any given time even when ephemeral.
  - https://github.com/w3c/did-spec-registries/
  - https://github.com/w3c/did-spec-registries/blob/main/tooling/did-method-registry-entry.yml
  - https://github.com/pdxjohnny/did-spec-registries/new/open-architecture-and-alice/methods
- References
  - https://www.vim.org/download.php
    - https://github.com/vim/vim-win32-installer/releases/download/v9.0.0000/gvim_9.0.0000_x86_signed.exe
  - https://github.com/graph4ai/graph4nlp
  - https://gitlab.com/gitlab-org/gitlab/-/issues/371098
  - https://vulns.xyz/2022/05/auth-tarball-from-git/
  - https://github.com/kpcyrd/rebuilderd
  - https://stackoverflow.com/questions/10082517/simplest-tool-to-measure-c-program-cache-hit-miss-and-cpu-time-in-linux/10114325#10114325
  - https://www.nature.com/articles/nature22031
    - > Using numerical simulations and mathematical derivation, we identify how a discrete von Neumann cellular automaton emerges from a continuous Turing reaction–diffusion system.
    - Collective Intelligence

```console
$ ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@143.110.152.152 sudo rm -f /root/vm/image.qcow2 && scp -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no decentralice.sh $USER@143.110.152.152:./ && export REC_TITLE="Rolling Alice: Engineering Logs: OS DecentrAlice"; export REC_HOSTNAME="build.container.image.nahdig.com"; python3.9 -m asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@143.110.152.152 sudo bash decentralice.sh -kernel /root/vm/kernel -command 'console=ttyS0 systemd.log_level=9'" >(xz --stdout - > "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).json.xz")
```

```powershell
PS C:\Users\Johnny> python -m venv .venv.windows
PS C:\Users\Johnny> .\.venv.windows\Scripts\activate
You should consider upgrading via the 'C:\Users\Johnny\.venv.windows\Scripts\python.exe -m pip install --upgrade pip' command.
(.venv.windows) PS C:\Users\Johnny> python -m pip install -U pip setuptools wheel
Requirement already satisfied: pip in c:\users\johnny\.venv.windows\lib\site-packages (21.2.3)
Collecting pip
  Using cached pip-22.2.2-py3-none-any.whl (2.0 MB)
Requirement already satisfied: setuptools in c:\users\johnny\.venv.windows\lib\site-packages (57.4.0)
Collecting setuptools
  Using cached setuptools-65.4.1-py3-none-any.whl (1.2 MB)
Collecting wheel
  Using cached wheel-0.37.1-py2.py3-none-any.whl (35 kB)
Installing collected packages: wheel, setuptools, pip
  Attempting uninstall: setuptools
    Found existing installation: setuptools 57.4.0
    Uninstalling setuptools-57.4.0:
      Successfully uninstalled setuptools-57.4.0
  Attempting uninstall: pip
    Found existing installation: pip 21.2.3
    Uninstalling pip-21.2.3:
      Successfully uninstalled pip-21.2.3
Successfully installed pip-22.2.2 setuptools-65.4.1 wheel-0.37.1
PS C:\Users\Johnny> python -m pip install asciinema
Collecting asciinema
  Downloading asciinema-2.2.0-py3-none-any.whl (92 kB)
     |████████████████████████████████| 92 kB 202 kB/s
Installing collected packages: asciinema
Successfully installed asciinema-2.2.0
(.venv.windows) PS C:\Users\Johnny> cd .\Documents\python\dffml\
(.venv.windows) PS C:\Users\Johnny\Documents\python\dffml> dir


    Directory: C:\Users\Johnny\Documents\python\dffml


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         2/20/2022   3:11 PM                .ci
d-----          2/4/2022   9:26 PM                .github
d-----         2/20/2022   3:11 PM                .vscode
d-----          2/4/2022   9:26 PM                configloader
d-----         2/20/2022   3:14 PM                dffml
d-----         2/20/2022   3:11 PM                dffml.egg-info
d-----          2/4/2022   9:28 PM                dist
d-----         2/20/2022   3:14 PM                docs
d-----         2/20/2022   3:11 PM                examples
d-----          2/4/2022   9:26 PM                feature
d-----          2/4/2022   9:26 PM                model
d-----         2/20/2022   3:11 PM                news
d-----         2/20/2022   3:14 PM                operations
d-----         2/20/2022   3:11 PM                scripts
d-----          2/4/2022   9:26 PM                service
d-----         2/20/2022   3:14 PM                source
d-----         2/20/2022   3:14 PM                tests
-a----          2/4/2022   9:26 PM            170 .coveragerc
-a----          2/4/2022   9:26 PM            260 .deepsource.toml
-a----          2/4/2022   9:26 PM             42 .dockerignore
-a----          2/4/2022   9:26 PM             68 .gitattributes
-a----         2/20/2022   3:11 PM            519 .gitignore
-a----         2/20/2022   3:11 PM            431 .gitpod.yml
-a----         2/20/2022   3:11 PM            437 .lgtm.yml
-a----         2/20/2022   3:11 PM             97 .pre-commit-config.yaml
-a----          2/4/2022   9:26 PM             79 .pylintrc
-a----         2/20/2022   3:14 PM          29994 CHANGELOG.md
-a----          2/4/2022   9:26 PM            112 CONTRIBUTING.md
-a----         2/20/2022   3:11 PM           3425 Dockerfile
-a----          2/4/2022   9:26 PM           1088 LICENSE
-a----          2/4/2022   9:26 PM             68 MANIFEST.in
-a----         2/20/2022   3:14 PM            480 pyproject.toml
-a----         2/20/2022   3:14 PM           3002 README.md
-a----         2/20/2022   3:14 PM            370 requirements-dev.txt
-a----          2/4/2022   9:26 PM            641 SECURITY.md
-a----         2/20/2022   3:14 PM           7739 setup.py


(.venv.windows) PS C:\Users\Johnny\Documents\python\dffml> git status
Refresh index: 100% (1147/1147), done.
On branch manifest
Your branch is up to date with 'pdxjohnny/manifest'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   dffml/util/testing/consoletest/commands.py

no changes added to commit (use "git add" and/or "git commit -a")
(.venv.windows) PS C:\Users\Johnny\Documents\python\dffml> git diff
diff --git a/dffml/util/testing/consoletest/commands.py b/dffml/util/testing/consoletest/commands.py
index 7807c99ff..f83d3fb12 100644
--- a/dffml/util/testing/consoletest/commands.py
+++ b/dffml/util/testing/consoletest/commands.py
@@ -7,7 +7,6 @@ import sys
 import json
 import time
 import copy
-import fcntl
 import shlex
 import signal
 import atexit
(.venv.windows) PS C:\Users\Johnny\Documents\python\dffml> git log -n 1
commit 80dc54afb6ee201342ba216fecfaf5ae160686a7 (HEAD -> manifest, pdxjohnny/manifest)
Author: John Andersen <johnandersenpdx@gmail.com>
Date:   Sat Feb 19 20:35:22 2022 -0800

    operations: innersource: Fix tests to clone and check for workflows using git operations

    Signed-off-by: John Andersen <johnandersenpdx@gmail.com>
```