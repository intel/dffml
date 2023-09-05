## 2022-09-25 @pdxjohnny Engineering Log

- Architecting Alice: COPY Linux Kernel
- [Architecting Alice: OS DecentrAlice](https://github.com/intel/dffml/discussions/1406#discussioncomment-3720703)

```console
$ cat > fedora.sh <<'EOF'
mount /dev/sda3 /mnt
mount /dev/sda1 /mnt/boot
swapon /dev/sda2
mkdir -p /mnt/{proc,dev,sys}
mkdir -p /mnt/var/tmp
mkdir -p /mnt/fedora/var/tmp

cat > /mnt/run-dracut.sh <<'LOL'
export PATH="${PATH}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/dracut/"
export KERNEL_VERSION="$(ls /lib/modules)"
bash -xp /usr/bin/dracut --uefi --kver ${KERNEL_VERSION} --kernel-cmdline "console=ttyS0 root=/dev/sda3"
LOL

arch-chroot /mnt/fedora /bin/bash run-dracut.sh
EOF
$ bash fedora.sh
...
+ dinfo 'Executing: /usr/bin/dracut --uefi --kver 5.19.10-200.fc36.x86_64 --kernel-cmdline console=ttyS0'
+ set +x
bash-5.1# echo $?
0
bash-5.1# lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
fd0      2:0    1     4K  0 disk
loop0    7:0    0 683.2M  1 loop
sda      8:0    0    20G  0 disk
├─sda1   8:1    0   260M  0 part
├─sda2   8:2    0    10G  0 part [SWAP]
└─sda3   8:3    0   9.8G  0 part
sr0     11:0    1  1024M  0 rom
bash-5.1# find /boot/
/boot/
/boot/System.map-5.19.10-200.fc36.x86_64
/boot/.vmlinuz-5.19.10-200.fc36.x86_64.hmac
/boot/vmlinuz-5.19.10-200.fc36.x86_64
/boot/symvers-5.19.10-200.fc36.x86_64.gz
/boot/efi
/boot/efi/EFI
/boot/efi/EFI/fedora
/boot/efi/EFI/Linux
/boot/efi/EFI/Linux/linux-5.19.10-200.fc36.x86_64-d1a1c3d381b9405ab46417e3535ef1be.efi
/boot/grub2
/boot/initramfs-5.19.10-200.fc36.x86_64.img
/boot/loader
/boot/loader/entries
/boot/loader/entries/d1a1c3d381b9405ab46417e3535ef1be-5.19.10-200.fc36.x86_64.conf
/boot/config-5.19.10-200.fc36.x86_64
bash-5.1#
exit
[root@archiso ~]# bash fedora.shc
[root@archiso ~]# ll /mnt/boot/
bash: ll: command not found
[root@archiso ~]# find !$
find /mnt/boot/
/mnt/boot/
/mnt/boot/NvVars
[root@archiso ~]# bootctl --esp-path=/mnt/boot install
Created "/mnt/boot/EFI".
Created "/mnt/boot/EFI/systemd".
Created "/mnt/boot/EFI/BOOT".
Created "/mnt/boot/loader".
Created "/mnt/boot/loader/entries".
Created "/mnt/boot/EFI/Linux".
Copied "/usr/lib/systemd/boot/efi/systemd-bootx64.efi" to "/mnt/boot/EFI/systemd/systemd-bootx64.efi".
Copied "/usr/lib/systemd/boot/efi/systemd-bootx64.efi" to "/mnt/boot/EFI/BOOT/BOOTX64.EFI".
Random seed file /mnt/boot/loader/random-seed successfully written (32 bytes).
Not installing system token, since we are running in a virtualized environment.
Created EFI boot entry "Linux Boot Manager".
[root@archiso ~]# find /mnt/boot/
/mnt/boot/
/mnt/boot/NvVars
/mnt/boot/EFI
/mnt/boot/EFI/systemd
/mnt/boot/EFI/systemd/systemd-bootx64.efi
/mnt/boot/EFI/BOOT
/mnt/boot/EFI/BOOT/BOOTX64.EFI
/mnt/boot/EFI/Linux
/mnt/boot/loader
/mnt/boot/loader/entries
/mnt/boot/loader/loader.conf
/mnt/boot/loader/random-seed
/mnt/boot/loader/entries.srel
[root@archiso ~]# for file in $(find /mnt/fedora/boot/); do cp -v $file $(echo $file | sed -e 's/fedora//' -e 's/efi\/EFI/EFI/'); done
[root@archiso ~]# diff -y <(find /mnt/boot | sort) <(find /mnt/fedora/boot | sed -e 's/fedora\///' -e 's/efi\/EFI/EFI/' | sort)
/mnt/boot                                                       /mnt/boot
/mnt/boot/.vmlinuz-5.19.10-200.fc36.x86_64.hmac                 /mnt/boot/.vmlinuz-5.19.10-200.fc36.x86_64.hmac
/mnt/boot/EFI                                                   /mnt/boot/EFI
/mnt/boot/EFI/BOOT                                            <
/mnt/boot/EFI/BOOT/BOOTX64.EFI                                <
/mnt/boot/EFI/Linux                                             /mnt/boot/EFI/Linux
/mnt/boot/EFI/Linux/linux-5.19.10-200.fc36.x86_64-d1a1c3d381b   /mnt/boot/EFI/Linux/linux-5.19.10-200.fc36.x86_64-d1a1c3d381b
/mnt/boot/EFI/systemd                                         | /mnt/boot/EFI/fedora
/mnt/boot/EFI/systemd/systemd-bootx64.efi                     <
/mnt/boot/NvVars                                              <
/mnt/boot/System.map-5.19.10-200.fc36.x86_64                    /mnt/boot/System.map-5.19.10-200.fc36.x86_64
/mnt/boot/config-5.19.10-200.fc36.x86_64                        /mnt/boot/config-5.19.10-200.fc36.x86_64
                                                              > /mnt/boot/efi
                                                              > /mnt/boot/grub2
/mnt/boot/initramfs-5.19.10-200.fc36.x86_64.img                 /mnt/boot/initramfs-5.19.10-200.fc36.x86_64.img
/mnt/boot/loader                                                /mnt/boot/loader
/mnt/boot/loader/entries                                        /mnt/boot/loader/entries
/mnt/boot/loader/entries.srel                                 <
/mnt/boot/loader/entries/d1a1c3d381b9405ab46417e3535ef1be-5.1   /mnt/boot/loader/entries/d1a1c3d381b9405ab46417e3535ef1be-5.1
/mnt/boot/loader/loader.conf                                  | /mnt/boot/symvers-5.19.10-200.fc36.x86_64.gz
/mnt/boot/loader/random-seed                                  <
/mnt/boot/vmlinuz-5.19.10-200.fc36.x86_64                       /mnt/boot/vmlinuz-5.19.10-200.fc36.x86_64
```