## 2022-11-11 @pdxjohnny Engineering Logs

- https://fluxcd.io/flux/guides/image-update/
  - Possible `FROM` rebuild chain helper
- https://github.com/Xubuntu/lightdm-gtk-greeter-settings
  - https://github.com/Xubuntu/lightdm-gtk-greeter-settings/issues/4#issuecomment-1312059288
    - Same on Fedora 37
      - Root cause was permissions issue, needs to be world readable and
        all directories which are parents need to be world readable as
        well. Moved file from `/root` to `/opt/wallpapers/` and ensured
        permissions were correct.
    - ![reproduced-on-fedora-37-launchpad-lightdm-gtk-greeter-settings-bug-1593986](https://user-images.githubusercontent.com/5950433/201404906-c7f5d800-a803-4005-bfbf-129c2f45a096.png)

```console
$ sudo mkdir /opt/wallpapers/
$ sudo stat /opt/wallpapers/
  File: /opt/wallpapers/
  Size: 27              Blocks: 0          IO Block: 4096   directory
Device: 253,1   Inode: 9450093     Links: 2
Access: (0755/drwxr-xr-x)  Uid: (    0/    root)   Gid: (    0/    root)
Context: unconfined_u:object_r:usr_t:s0
Access: 2022-11-11 10:30:55.826849997 -0800
Modify: 2022-11-11 10:30:52.989865945 -0800
Change: 2022-11-11 10:30:52.989865945 -0800
 Birth: 2022-11-11 10:30:32.291982299 -0800
$ sudo cp /root/wallpaper.jpg /opt/wallpapers/
$ file /opt/wallpapers/wallpaper.jpg
/opt/wallpapers/wallpaper.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 218x218, segment length 16, Exif Standard: [TIFF image data, big-endian, direntries=7, orientation=upper-left, xresolution=98, yresolution=106, resolutionunit=2, software=Pixelmator Pro 2.1.3, datetime=2013:07:16 13:17:42], baseline, precision 8, 6016x3384, components 3
$ stat /opt/wallpapers/wallpaper.jpg
  File: /opt/wallpapers/wallpaper.jpg
  Size: 2187975         Blocks: 4280       IO Block: 4096   regular file
Device: 253,1   Inode: 9752102     Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Context: unconfined_u:object_r:usr_t:s0
Access: 2022-11-11 10:31:06.320791009 -0800
Modify: 2022-11-11 10:30:52.989865945 -0800
Change: 2022-11-11 10:30:52.989865945 -0800
 Birth: 2022-11-11 10:30:52.989865945 -0800
```

- Resize root LUKS partition on new fedora install.
  - https://www.golinuxcloud.com/resize-luks-partition-shrink-extend-decrypt/#Resize_LUKS_Partition

```console
$ df -h
Filesystem                      Size  Used Avail Use% Mounted on
devtmpfs                        4.0M     0  4.0M   0% /dev
tmpfs                           7.8G  101M  7.7G   2% /dev/shm
tmpfs                           3.1G  1.9M  3.1G   1% /run
/dev/mapper/fedora_fedora-root   15G   15G  754M  96% /
tmpfs                           7.8G  3.6M  7.8G   1% /tmp
/dev/sdc3                       1.1G  296M  751M  29% /boot
/dev/sdc2                       575M  6.2M  569M   2% /boot/efi
tmpfs                           1.6G  168K  1.6G   1% /run/user/1000
$ sudo blkid -t TYPE=crypto_LUKS -o device
/dev/sdc4
$ lsblk
NAME                                          MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
sdc                                             8:32   0 232.9G  0 disk  
├─sdc1                                          8:33   0    16M  0 part  
├─sdc2                                          8:34   0   576M  0 part  /boot/efi
├─sdc3                                          8:35   0     1G  0 part  /boot
└─sdc4                                          8:36   0 231.2G  0 part  
  └─luks-18013279-e995-45bc-bcb8-83dda718da78 253:0    0 231.2G  0 crypt 
    └─fedora_fedora-root                      253:1    0    15G  0 lvm   /
zram0                                         252:0    0     8G  0 disk  [SWAP]
$ sudo cryptsetup status fedora_fedora-root
/dev/mapper/fedora_fedora-root is active and is in use.
  type:    n/a
$ sudo cryptsetup status luks-18013279-e995-45bc-bcb8-83dda718da78
/dev/mapper/luks-18013279-e995-45bc-bcb8-83dda718da78 is active and is in use.
  type:    LUKS2
  cipher:  aes-xts-plain64
  keysize: 512 bits
  key location: keyring
  device:  /dev/sdc4
  sector size:  512
  offset:  32768 sectors
  size:    484860697 sectors
  mode:    read/write
  flags:   discards
```

- Reboot to live image of fedora server 36
  - Run `lvextend` and `xfs_growfs` on `/dev/mapper/fedora_fedora-root`, grow
    by unused space size, around +216.1G.

```console
$ lsblk
$ cryptsetup luksOpen /dev/sdc4 luks
$ cryptsetup status luks
$ lvextend -L +216.1G /dev/mapper/fedora_fedora-root
$ mount /dev/mapper/fedora_fedora-root /mnt
$ xfs_growfs /dev/mapper/fedora_fedora-root
```

- Boot and check new disk space, 216G available.

```console
$ df -h
Filesystem                      Size  Used Avail Use% Mounted on
devtmpfs                        4.0M     0  4.0M   0% /dev
tmpfs                           7.8G   93M  7.7G   2% /dev/shm
tmpfs                           3.1G  1.9M  3.1G   1% /run
/dev/mapper/fedora_fedora-root  232G   16G  216G   7% /
tmpfs                           7.8G  3.5M  7.8G   1% /tmp
/dev/sdc3                       1.1G  296M  751M  29% /boot
/dev/sdc2                       575M  6.2M  569M   2% /boot/efi
tmpfs                           1.6G  168K  1.6G   1% /run/user/1000
```

- https://github.com/decentralized-identity/credential-manifest/blob/main/spec/spec.md
  - https://github.com/decentralized-identity/credential-manifest/pull/131/files#diff-c4795c497b83a8c03e33535caf0fb0e1512cecd8cb448f62467326277c152afeR379
  - https://github.com/decentralized-identity/credential-manifest/blob/main/spec/spec.md#credential-response
    - > // NOTE: VP, OIDC, DIDComm, or CHAPI outer wrapper properties would be at outer layer
- https://github.com/decentralized-identity/credential-manifest/blob/main/test/credential-manifest/test.js
- TODO
  - [x] Resize LUKS fedora root to use full SSD attached via USB 3.1 :P it's fast!
  - [ ] "We need to consider automation too to make this work in the CI/CD pipeline. We use the open-source Data Flow Facilitator for Machine Learning (DFFML) framework to establish a bidirectional data bridge between the LTM and source code. When a new pull request is created, an audit-like scan is initiated to check to see if the LTM needs to be updated. For example, if a scan detects that new cryptography has been added to the code, but the existing LTM doesn’t know about it, then a warning is triggered. Project teams can triage the issue to determine whether it is a false positive or not, just like source code scans." [John L Whiteman]
    - [Rolling Alice: Progress Report 6: Living Threat Models Are Better Than Dead Threat Models](https://gist.github.com/pdxjohnny/07b8c7b4a9e05579921aa3cc8aed4866#file-rolling_alice_progress_report_0006_living_threat_models_are_better_than_dead_threat_models-md)
  - [ ] Investigate https://github.com/BishopFox/sliver for comms