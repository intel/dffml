## 2023-03-25 @pdxjohnny Engineering Logs

- https://mastodon.social/@pdxjohnny/110084611470680226
  - Phone seems be charging while plugged into monitor
    - [AliceIsHereLibrem5](https://user-images.githubusercontent.com/5950433/227727820-2ec703d9-7ea4-4b5f-801e-bb6d871328ea.jpeg)
  - Hoping to check power stats, drain, etc.
  - Ideally this would be a package, haven't checked, curious to static build
- https://wiki.archlinux.org/title/Powertop
- https://github.com/fenrus75/powertop
  - Might contribute CI/CD back here for others who want static builds for distros
    which don't package powertop. With our security.md/txt AcivityPub methodology
    we've setup the dependency trees of projects to enable notifications which would
    help ensure that static builds are kept up to date.
  - https://blog.madkoo.net/2022/09/09/Github-IssueOps/
    - We can allow others who are not members of the repo to re-trigger builds (or their
      relay'd event stream from our dependencies) via IssueOps. Only members can
      workflow_dispatch.
- https://github.com/pdxjohnny/static-builds/actions/runs/4519894447/jobs/7960651645

```
checking for libtracefs... no
configure: error: libtracefs is required but was not found
checking for library containing tracefs_local_events... no
```

- Installing libtracefs-dev for some reason didn't help :(
  - https://github.com/fenrus75/powertop/pull/122#issuecomment-1464898950
    - > racefs_event_file_exists() is missing in the [Debian libtracefs 1.0.2-1 package](https://sources.debian.org/src/libtracefs/).
    - https://wiki.debian.org/DebianTesting
      - We need to enable bookworm which is the next version of debian, but we're on ubuntu, we can have github actions run us on a debain container
      - https://docs.github.com/en/actions/using-jobs/running-jobs-in-a-container
- https://github.com/pdxjohnny/static-builds/actions/runs/4519990144
  - https://github.com/github/codeql-action/issues/572
  - https://sjramblings.io/github-actions-resource-not-accessible-by-integration?x-host=sjramblings.io

```
Error: Unhandled error: HttpError: Resource not accessible by integration
```

- https://github.com/Foxboron/sbctl/releases/tag/0.11
- https://social.coop/@J12t/110079945657098806
- https://getutm.app
  - Sent to Tom
- https://github.com/rsc/2fa
  - Need static builds of this too, cgo=0 tags netgo
- https://rhodesmill.org/brandon/2009/commands-with-comma/
  - context local commamd pdefixed ith comma
- https://github.com/github/codeql-action/issues/572#issuecomment-966291195
- https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs
- https://github.com/newreleasesio/cli-go#listing-available-notification-channels
  - This has webhook support

```console
$ curl -sfLO https://github.com/pdxjohnny/static-builds/releases/download/tmux/tmux
$ file tmux 
tmux: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, BuildID[sha1]=cd4960b3793f59321dba13c6525617ff83f0fbb4, for GNU/Linux 3.2.0, with debug_info, not stripped
$ curl -sfLO https://github.com/pdxjohnny/static-builds/releases/download/powertop/powertop
$ file powertop 
powertop: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=19912d09dfd14b2b18c9c0db010e06270915e416, for GNU/Linux 3.2.0, with debug_info, not stripped
```

- https://goreleaser.com/ci/actions/
- https://github.com/pdxjohnny/static-builds/blob/412070805cc81deb91921a1785e2a448130b0309/.github/workflows/2fa.yml
- https://github.com/pdxjohnny/static-builds/releases/tag/v1.2.0-1-g2479737

```console
$ cd ~/Downloads/
$ mkdir 2fa
$ cd 2fa
$ curl -sfL https://github.com/pdxjohnny/static-builds/releases/download/v1.2.0-1-g2479737/static-builds_1.2.0-1-g2479737_linux_arm64.tar.gz | tar xvz
LICENSE
README.md
static-builds
$ file ./static-builds
./static-builds: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), statically linked, Go BuildID=7SDPJG9GMNSWWh9yztI-/IyOawSUR8TC433dkmBdo/-WpXYH6ArEaytFRcP3sA/WyhpQ58888T7HZT92Z8I, stripped
$ mv ~/.local/bin/static-builds ~/.local/bin/2fa
$ 2fa -h
usage:
	2fa -add [-7] [-8] [-hotp] keyname
	2fa -list
	2fa [-clip] keyname
```

- TODO
  - [x] Fix tmux build
  - [x] powertop build
    - [ ] Fix static build
      - LOL just remembered this phone is ARM not x86
        - `¯\_(ツ)_/¯`
  - [x] 2fa aarch64 build
  - [ ] Dataflow in rust
    - [ ] https://github.com/RustPython/RustPython incremental
  - [ ] cve-bin-tool scan to get SBOM of static build -> newreleasesio webhook -> ActivityPub mirror -> ActivityPub follow as Code -> issue ops retriggers