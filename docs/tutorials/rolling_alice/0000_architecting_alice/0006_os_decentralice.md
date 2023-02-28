# Volume 0: Chapter 6: OS DecentrAlice

We'll leverage QEMU for our virtualized environment and
Dockerfiles to define the OS image contents.

- Context
  - We need a base of operations from which to build on
    as we deploy Alice in various contexts.
- Goals
  - We want to end up with something that can be used as a daily driver.
- Actions
  - We are going to take userspace from Wolfi and kernel from Fedora.
    We'll roll in SSI service binaries to auto start on boot.
- Future work
  - We'll see what we can do about TPM support / secure boot.
- References
  - This tutorial is covered in `OS DecentrAlice: Rolling an OS` **TODO** Update with link to recording once made.
  - The resulting commit from completion of this tutorial was: https://gist.github.com/pdxjohnny/5f358e749181fac74a750a3d00a74b9e
- Feedback
  - Please provide feedback / thoughts for extension / improvement about this tutorial in the following discussion thread: https://github.com/intel/dffml/discussions/1414

## Plan

- Start with a distro with a kernel
- Dump wolfi to it
  - Fedora @ `/`
    - Wofli @ `/wofli`
- Configure systemd to start sshd from wolfi
- Configure systemd to start actions runner from wolfi
- Run `alice shouldi contribute` data flows
- sigstore github actions OIDC token
  - self-attested (github assisted) scan data
  - SCITT OpenSSF Metrics Use Case
    - https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md
- Future
  - TPM secure boot on the VM
- Packer: https://www.packer.io/downloads
  - https://www.packer.io/plugins/builders/openstack
  - https://www.packer.io/plugins/builders/digitalocean
  - https://www.packer.io/plugins/builders/qemu
  - https://www.packer.io/plugins/datasources/git/commit
    - Manifest
  - https://www.packer.io/plugins/builders/digitalocean#user_data
    - https://gist.github.com/pdxjohnny/a0dc3a58b4651dc3761bee65a198a80d#file-run-vm-sh-L156-L205
    - Enable github actions on boot via systemd here

**osdecentralice.json**

```json
{
    "variables": {
        "version": "latest",
        "do_token": "{{env `DIGITALOCEAN_TOKEN`}}"
    },
    "builders": [
        {
            "type": "digitalocean",
            "api_token": "{{user `do_token`}}",
            "image": "fedora-36-x64",
            "region": "sfo3",
            "size": "m3-2vcpu-16gb",
            "ssh_username": "root",
            "droplet_name": "osdecentralice-{{user `version`}}",
            "snapshot_name": "osdecentralice-{{user `version`}}-{{timestamp}}"
        }
    ],
    "provisioners": [
        {
            "type": "shell",
            "inline": [
                "set -x",
                "set -e",
                "dnf upgrade -y",
                "dnf install -y podman",
                "curl -sfLC - -o Dockerfile https://gist.github.com/pdxjohnny/5f358e749181fac74a750a3d00a74b9e/raw/f93d3831f94f58751d85f71e8e266f6020042323/Dockerfile",
                "sha256sum -c -<<<'b5f31acb1ca47c55429cc173e08820af4a19a32685c5e6c2b1459249c517cbb5  Dockerfile'",
                "podman build -t osdecentralice:latest - < Dockerfile",
                "container=$(podman run --rm -d --entrypoint tail osdecentralice -F /dev/null);",
                "trap \"podman kill ${container}\" EXIT",
                "sleep 1",
                "podman cp \"${container}:/\" /wolfi"
            ]
        }
    ]
}
```

```console
$ sudo -E packer build osdecentralice.json
```

![image](https://user-images.githubusercontent.com/5950433/195759634-4493d348-fb66-41ba-a531-330e7e5662c7.png)

```console
    digitalocean: --> 7b72b288ae3
    digitalocean: [2/2] STEP 8/8: ENTRYPOINT bash
    digitalocean: [2/2] COMMIT osdecentralice:latest
    digitalocean: --> 919ae809e98
    digitalocean: Successfully tagged localhost/osdecentralice:latest
    digitalocean: 919ae809e9841893f046cd49950c4515b04bb24db5d87f1de52168275860ebec
==> digitalocean: ++ podman run --rm -d --entrypoint tail osdecentralice -F /dev/null
==> digitalocean: + container=0c0d3ad9125c981aff17b78ee38c539229b444e546a4e346bc1f86d7ca0480fb
==> digitalocean: + trap 'podman kill 0c0d3ad9125c981aff17b78ee38c539229b444e546a4e346bc1f86d7ca0480fb' EXIT
==> digitalocean: + sleep 1
==> digitalocean: + podman cp 0c0d3ad9125c981aff17b78ee38c539229b444e546a4e346bc1f86d7ca0480fb:/ /wolfi
==> digitalocean: + podman kill 0c0d3ad9125c981aff17b78ee38c539229b444e546a4e346bc1f86d7ca0480fb
    digitalocean: 0c0d3ad9125c981aff17b78ee38c539229b444e546a4e346bc1f86d7ca0480fb
==> digitalocean: Gracefully shutting down droplet...
==> digitalocean: Creating snapshot: osdecentralice-latest-1665722921
==> digitalocean: Waiting for snapshot to complete...
==> digitalocean: Destroying droplet...
==> digitalocean: Deleting temporary ssh key...
Build 'digitalocean' finished after 10 minutes 12 seconds.

==> Wait completed after 10 minutes 12 seconds

==> Builds finished. The artifacts of successful builds are:
--> digitalocean: A snapshot was created: 'osdecentralice-latest-1665722921' (ID: 118836442) in regions 'sfo3'
++ history -a
pdxjohnny@fedora-s-4vcpu-8gb-sfo3-01 ~ $
```

![image](https://user-images.githubusercontent.com/5950433/195765976-fe432d96-b2ca-4a10-a595-b82acaf0f463.png)

- Now to install github actions runner in wolfi, and configure systemd to auto start it.
  - Ideally we figure out how to deploy a bunch of these, terraform?
  - They need to be ephemeral and shutdown after each job
    - Treat vector: Comprimise by threat actor results in system not triggering shutdown.
      - Mitigation: Reap out of band

![image](https://user-images.githubusercontent.com/5950433/195766172-7898c5ce-de9a-48cc-a2d4-331a7e614dd3.png)

[![mindset-security](https://img.shields.io/badge/mindset-security-critical)](https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_easter_eggs.md#mindset-security-)

- Why it's a time traveling Python 3.10.7! It says it's from the UNIX epoch!
  - This is due to trying to make builds reproducable, meaning "bit for bit" if rebuilt later.
    - https://twitter.com/lorenc_dan/status/1570855501356998657?s=20&t=90RQmd1IPUv103XgHakE7A
    - https://github.com/intel/dffml/blob/b892cfab9bd152c47a709e8708491c95b8c3ec8e/tests/util/test_net.py#L18-L44

```console
[root@osdecentralice-latest-1665722921-s-4vcpu-8gb-sfo3-01 ~]# chroot /wolfi /usr/bin/python
Python 3.10.7 (main, Jan  1 1970, 00:00:00) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pathlib
>>> print(pathlib.Path("/etc/os-release").read_text())
ID=wolfi
NAME="Wolfi"
PRETTY_NAME="Wolfi"
VERSION_ID="20220913"
HOME_URL="https://wolfi.dev"

>>>
```

[![asciicast](https://asciinema.org/a/528221.svg)](https://asciinema.org/a/528221)

[![asciicast](https://asciinema.org/a/528220.svg)](https://asciinema.org/a/528220)

[![asciicast](https://asciinema.org/a/528223.svg)](https://asciinema.org/a/528223)

## Notes

- TODO
  - [ ] Build QEMU images
  - [ ] confidential containers?
  - [ ] Updates for fedora packages (aka kernel) will need to be handled.
    - We might just re-roll and pull only the layers with kernel stuff? TBD
  - [ ] Add custom bootloader image
    - slice image from alice unbirthday gif-2-cli gif and convert to bitmap
    - References
      - https://man7.org/linux/man-pages/man8/dracut.8.html
        - > `--uefi-splash-image <FILE>`
          >   - Specifies the UEFI stub loader’s splash image. Requires
          >     bitmap (.bmp) image format.
  - [ ] motd?
- References
  - Chainguard
    - https://edu.chainguard.dev/chainguard/chainguard-images/how-to-use-chainguard-images/
    - https://edu.chainguard.dev/open-source/melange/getting-started-with-melange/
      - We should use melange and apko and setup a secure factory to build images.
  - Images
    - https://dnf-plugins-core.readthedocs.io/en/latest/download.html
    - https://github.com/srossross/rpmfile
  - QEMU
    - https://pdxjohnny.github.io/linux-kernel/
    - https://pdxjohnny.github.io/qemu/
    - https://archlinux.org/releng/netboot/
    - https://gist.github.com/pdxjohnny/6063d1893c292d1ac0024fb14d1e627d
  - Install Guide
    - https://wiki.archlinux.org/title/Installation_guide
      - https://archlinux.org/releng/netboot/
      - https://wiki.archlinux.org/title/Installation_guide#Boot_loader
      - https://wiki.archlinux.org/title/Installation_guide#Example_layouts
  - Bootloader
    - https://man.archlinux.org/man/bootctl.1
      - `root@archiso ~ # bootctl --esp-path=/mnt/boot install`
    - https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT/
      - Type #2 EFI Unified Kernel Images
    - https://systemd.io/BOOT_LOADER_SPECIFICATION/
    - https://wiki.archlinux.org/title/Installation_guide#Boot_loader
    - https://github.com/nwildner/dracut-uefi-simple
  - sysadmin
    - https://github.com/aurae-runtime/auraed/tree/main/hack
      - https://github.com/aurae-runtime/auraed/blob/main/hack/initramfs/mk-initramfs
    - https://gist.github.com/pdxjohnny/a0dc3a58b4651dc3761bee65a198a80d#file-run-vm-sh-L125-L141
  - ssi-service
    - https://github.com/TBD54566975/ssi-service/pull/111
    - https://edu.chainguard.dev/open-source/melange/getting-started-with-melange/
      - For packaging
  - python
    - https://github.com/pypa/get-pip
  - TPM
    - https://systemd.network/linuxx64.efi.stub.html#TPM2%20PCR%20Notes
  - Secure Boot
    - https://fedoraproject.org/wiki/Secureboot
    - https://github.com/rhboot/pesign
    - https://github.com/rhboot/shim
  - We'll be doing a DID -> ActivityPub -> aurae grpc & kcp job execution proxy
    - https://github.com/aurae-runtime/aurae
    - [WIP: RFCv2: IETF SCITT: Use Case: OpenSSF Metrics: activitypub extensions for security.txt](https://github.com/ietf-scitt/use-cases/blob/f936e3acf4182a264382eedb755416b1130b4ff8/openssf_metrics.md#activitypub-extensions-for-securitytxt)
