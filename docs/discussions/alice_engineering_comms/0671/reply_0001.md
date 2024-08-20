## 2024-07-07 Engineering Logs

- fork is all you need (grep: fork + exec via activitypub)
  - try federation of forges to trigger fork workflows on synchronize. If it rebases clean, stage it via pr to pr. If it rebases dirty throw it in the ad hoc cve loop. Requires synchronization is an ad hoc cve
- webhook github attestations to federate to scitt
- Alice (the architecture) decentralizes the means of production
  - TCB schema for threat models

```console
$ python -m pip install -U pip setuptools wheel build && python -m pip install -e .
# Success!
$ git log -n 1
commit 4f9022420a33ef4a5d57ece1f82a0485e5b9ca14 (HEAD -> main, origin/main, origin/HEAD)
Author: Andrey <andrey@mindsdb.com>
Date:   Sat Jul 6 00:37:55 2024 +0300

    API handler tests and fixes (#9445)
$ python --version
Python 3.10.13
$ python -m mindsdb --api=http,mongodb,mysql --help
usage: __main__.py [-h] [--api API] [--config CONFIG] [--install-handlers INSTALL_HANDLERS] [--verbose] [--no_studio] [-v] [--ml_task_queue_consumer]

CL argument for mindsdb server

options:
  -h, --help            show this help message and exit
  --api API
  --config CONFIG
  --install-handlers INSTALL_HANDLERS
  --verbose
  --no_studio
  -v, --version
  --ml_task_queue_consumer
$ python -m pip install "https://github.com/mindsdb/mindsdb/archive/4f9022420a33ef4a5d57ece1f82a0485e5b9ca14.zip#egg=mindsdb"
```

- If you use the virtual network you should be able to secure tcp sockets at known ports over a custom network. This would make hooking bind events easily via ebpf.

[![asciicast](https://asciinema.org/a/667169.svg)](https://asciinema.org/a/667169)

- https://github.com/cloudflare/boringtun
  - forgejo keeps changing ports

[![asciicast](https://asciinema.org/a/667174.svg)](https://asciinema.org/a/667174)

- prompt: What is John working on and why?
  - https://github.com/pdxjohnny/dotfiles/commit/8d9850f85314a9f5c30f5bb7b8e47ba3857357be