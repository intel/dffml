## 2022-10-13 Rolling Alice: Architecting Alice: OS DecentrAlice: Engineering Logs

- New approch, fedora cloud `.iso` -> qmeu (`qemu convert .iso .qcow2`)
- `qemu-img resize fedora.qcow2 +10G`
- mess with partition tables to create new partition
- Dump wolfi to it
- Configure systemd to start sshd from wolfi
- Configure systemd to start actions runner from wolfi
- Run `alice shouldi contribute` data flows
- sigstore github actions OIDC token
  - self-attested (github assisted) scan data
  - SCITT OpenSSF Metrics Use Case
    - https://github.com/pdxjohnny/use-cases/blob/openssf_metrics/openssf_metrics.md
- Future
  - TPM secure boot on the VM
- References
  - https://www.qemu.org/docs/master/system/images.html
  - https://duckduckgo.com/?q=raw+to+qcow2&ia=web
    - https://www.aptgetlife.co.uk/kvm-converting-virtual-disks-from-raw-img-files-to-qcow2/
  - https://alt.fedoraproject.org/cloud/
    - https://download.fedoraproject.org/pub/fedora/linux/releases/36/Cloud/x86_64/images/Fedora-Cloud-Base-36-1.5.x86_64.raw.xz
      - Cloud Base compressed raw image
    - https://download.fedoraproject.org/pub/fedora/linux/releases/36/Cloud/x86_64/images/Fedora-Cloud-Base-36-1.5.x86_64.qcow2
      - Cloud Base image for Openstack

```console
$ qemu-img convert -O qcow2 -p Fedora-Cloud-Base-36-1.5.x86_64.raw Fedora-Cloud-Base-36-1.5.x86_64.qcow2
(0.00/100%)
```

```console
$ curl -sfLOC - https://download.fedoraproject.org/pub/fedora/linux/releases/36/Cloud/x86_64/images/Fedora-Cloud-Base-36-1.5.x86_64.qcow2
$ qemu-img resize Fedora-Cloud-Base-36-1.5.x86_64.qcow2 +10G
$ sudo dnf -y install guestfs-tools libvirt
$ sudo systemctl enable --now libvirtd
$ LIBGUESTFS_BACKEND=direct sudo -E virt-filesystems --long -h --all -a Fedora-Cloud-Base-36-1.5.x86_64.qcow2
Name                                      Type       VFS     Label  MBR Size  Parent
/dev/sda1                                 filesystem unknown -      -   1.0M  -
/dev/sda2                                 filesystem ext4    boot   -   966M  -
/dev/sda3                                 filesystem vfat    -      -   100M  -
/dev/sda4                                 filesystem unknown -      -   4.0M  -
/dev/sda5                                 filesystem btrfs   fedora -   3.9G  -
btrfsvol:/dev/sda5/root                   filesystem btrfs   fedora -   -     -
btrfsvol:/dev/sda5/home                   filesystem btrfs   fedora -   -     -
btrfsvol:/dev/sda5/root/var/lib/portables filesystem btrfs   fedora -   -     -
/dev/sda1                                 partition  -       -      -   1.0M  /dev/sda
/dev/sda2                                 partition  -       -      -   1000M /dev/sda
/dev/sda3                                 partition  -       -      -   100M  /dev/sda
/dev/sda4                                 partition  -       -      -   4.0M  /dev/sda
/dev/sda5                                 partition  -       -      -   3.9G  /dev/sda
/dev/sda                                  device     -       -      -   5.0G  -
$ qemu-img resize Fedora-Cloud-Base-36-1.5.x86_64.qcow2 +10G
Image resized.
$ LIBGUESTFS_BACKEND=direct sudo -E virt-filesystems --long -h --all -a Fedora-Cloud-Base-36-1.5.x86_64.qcow2
Name                                      Type       VFS     Label  MBR Size  Parent
/dev/sda1                                 filesystem unknown -      -   1.0M  -
/dev/sda2                                 filesystem ext4    boot   -   966M  -
/dev/sda3                                 filesystem vfat    -      -   100M  -
/dev/sda4                                 filesystem unknown -      -   4.0M  -
/dev/sda5                                 filesystem btrfs   fedora -   3.9G  -
btrfsvol:/dev/sda5/root                   filesystem btrfs   fedora -   -     -
btrfsvol:/dev/sda5/home                   filesystem btrfs   fedora -   -     -
btrfsvol:/dev/sda5/root/var/lib/portables filesystem btrfs   fedora -   -     -
/dev/sda1                                 partition  -       -      -   1.0M  /dev/sda
/dev/sda2                                 partition  -       -      -   1000M /dev/sda
/dev/sda3                                 partition  -       -      -   100M  /dev/sda
/dev/sda4                                 partition  -       -      -   4.0M  /dev/sda
/dev/sda5                                 partition  -       -      -   3.9G  /dev/sda
/dev/sda                                  device     -       -      -   15G   -
```

```console
$ cp Fedora-Cloud-Base-36-1.5.x86_64.qcow2.bak Fedora-Cloud-Base-36-1.5.x86_64.qcow2                                   $ truncate -r Fedora-Cloud-Base-36-1.5.x86_64.qcow2 Fedora-Cloud-Base-36-1.5.x86_64.2.qcow2
$ truncate -s +20GB Fedora-Cloud-Base-36-1.5.x86_64.2.qcow2                                                            $ LIBGUESTFS_BACKEND=direct sudo -E virt-resize --resize /dev/sda5=+1G Fedora-Cloud-Base-36-1.5.x86_64.qcow2 Fedora-Cloud-Base-36-1.5.x86_64.2.qcow2
[   0.0] Examining Fedora-Cloud-Base-36-1.5.x86_64.qcow2
**********

Summary of changes:

virt-resize: /dev/sda1: This partition will be left alone.

virt-resize: /dev/sda2: This partition will be left alone.

virt-resize: /dev/sda3: This partition will be left alone.

virt-resize: /dev/sda4: This partition will be left alone.

virt-resize: /dev/sda5: This partition will be resized from 3.9G to 4.9G.

virt-resize: There is a surplus of 13.0G.  An extra partition will be
created for the surplus.

**********
[   7.9] Setting up initial partition table on Fedora-Cloud-Base-36-1.5.x86_64.2.qcow2
[  28.5] Copying /dev/sda1
[  28.5] Copying /dev/sda2
 100% ⟦▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒⟧ 00:00
[  37.0] Copying /dev/sda3
[  37.3] Copying /dev/sda4
[  37.4] Copying /dev/sda5
 100% ⟦▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒⟧ 00:00

virt-resize: Resize operation completed with no errors.  Before deleting
the old disk, carefully check that the resized disk boots and works
correctly.
```

- https://linux.die.net/man/1/virt-resize

```console
$ curl -sfLOC - https://download.fedoraproject.org/pub/fedora/linux/releases/36/Cloud/x86_64/images/Fedora-Cloud-Base-36-1.5.x86_64.qcow2
$ qemu-img resize Fedora-Cloud-Base-36-1.5.x86_64.qcow2 +10G
$ sudo dnf -y install guestfs-tools libvirt
$ sudo systemctl enable --now libvirtd
$ qemu-img resize Fedora-Cloud-Base-36-1.5.x86_64.qcow2 +20G
$ cp Fedora-Cloud-Base-36-1.5.x86_64.qcow2.bak Fedora-Cloud-Base-36-1.5.x86_64.qcow2
$ LIBGUESTFS_BACKEND=direct sudo -E virt-resize --resize /dev/sda5=+1G Fedora-Cloud-Base-36-1.5.x86_64.qcow2 Fedora-Cloud-Base-36-1.5.x86_64.2.qcow2
$ qemu-system-x86_64 -no-reboot -smp cpus=2 -m 4096M -enable-kvm -nographic -cpu host -drive file=/home/pdxjohnny/Fedora-Cloud-Base-36-1.5.x86_64.2.qcow2,if=v2
SeaBIOS (version 1.16.0-1.fc36)


iPXE (https://ipxe.org) 00:03.0 CA00 PCI2.10 PnP PMM+BFF8C110+BFECC110 CA00



Booting from Hard Disk...
GRUB loading.
Welcome to GRUB!

                             GNU GRUB  version 2.06

 ┌────────────────────────────────────────────────────────────────────────────┐
 │*Fedora Linux (5.17.5-300.fc36.x86_64) 36 (Cloud Edition)                   │
```

- Still seeing issues with bad superblocks
- https://gist.github.com/pdxjohnny/6063d1893c292d1ac0024fb14d1e627d

```
e2fsck: Bad magic number in super-block while trying to open /dev/nbd1p5
/dev/nbd1p5:
The superblock could not be read or does not describe a valid ext2/ext3/ext4
filesystem.  If the device is valid and it really contains an ext2/ext3/ext4
filesystem (and not swap or ufs or something else), then the superblock
is corrupt, and you might try running e2fsck with an alternate superblock:
    e2fsck -b 8193 <device>
 or
    e2fsck -b 32768 <device>

```

- New new approach, packer: https://www.packer.io/downloads
  - https://www.packer.io/plugins/builders/openstack
  - https://www.packer.io/plugins/builders/digitalocean
  - https://www.packer.io/plugins/builders/qemu
  - https://www.packer.io/plugins/datasources/git/commit
    - Manifest
  - https://www.packer.io/plugins/builders/digitalocean#user_data
    - https://gist.github.com/pdxjohnny/a0dc3a58b4651dc3761bee65a198a80d#file-run-vm-sh-L156-L205
    - Enable github actions on boot via systemd here
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- https://gist.github.com/nickjj/d63d1e0ee71f4226ac5000bf1022bb38
- https://gist.github.com/pdxjohnny/5f358e749181fac74a750a3d00a74b9e

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
