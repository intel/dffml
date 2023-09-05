## 2022-10-12 Rolling Alice: Architecting Alice: OS DecentrAlice: Engineering Logs

```console
$ mkdir -p $(dirname /boot/EFI/BOOT/BOOTX64.EFI)
$ cp boot/efi/EFI/Linux/linux-*.efi /boot/EFI/BOOT/BOOTX64.EFI
```

- New approch, fedora cloud `.iso` -> qmeu (`qemu convert .iso .qcow2`)
- `qemu-img resize fedora.qcow2 +10G`
- mess with partition tables to create new partition
- Dump wolfi to it
- Configure systemd to start sshd from wolfi
- John ran out of disk space again