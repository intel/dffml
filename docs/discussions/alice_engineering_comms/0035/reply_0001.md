# Architecting Alice: OS DecentrAlice

> Moved to: https://github.com/intel/dffml/blob/alice/docs/tutorials/rolling_alice/0000_architecting_alice/0006_os_decentralice.md

Let's build an Operating System!

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
  - The resulting commit from completion of this tutorial was: **TODO** Update with link to operations added.
- Feedback
  - Please provide feedback / thoughts for extension / improvement about this tutorial in the following discussion thread: https://github.com/intel/dffml/discussions/1414

We will verify that the OS boots under a virtualized environment.

We will then boot to an arch linux live USB, format a disk, write
the contents of our new operating system to the root partition,
and install a bootloader (can we use systemd?).

We'll leverage QEMU for our virtualized environment and
Dockerfiles to define the OS image contents.

- Arch Linux Live @ `/`
  - Wofli @ `/mnt`
    - Fedora @ `/mnt/fedora`

## Base Image Dockerfile

```Dockerfile
# OS DecentrAlice Base Image Dockerfile
# Docs: https://github.com/intel/dffml/discussions/1406#discussioncomment-3720703

# Download and build the Self Soverign Identity Service
FROM cgr.dev/chainguard/wolfi-base AS build-ssi-service
RUN apk update && apk add --no-cache --update-cache curl go

RUN curl -sfL https://github.com/TBD54566975/ssi-service/archive/refs/heads/main.tar.gz \
  | tar xvz \
  && cd /ssi-service-main \
  && go build -tags jwx_es256k -o /ssi-service ./cmd

# Download the Linux kernel and needed utils to create bootable system
FROM registry.fedoraproject.org/fedora AS build-linux-kernel

RUN mkdir -p /build/kernel-core-rpms \
  && source /usr/lib/os-release \
  && dnf -y install \
    --installroot=/build/kernel-core-rpms \
    --releasever="${VERSION_ID}" \
    kernel-core \
    kernel-modules \
    systemd \
    systemd-networkd \
    systemd-udev \
    dracut \
    binutils \
    strace \
    kmod-libs

# First PATH addition
# Add Fedora install PATHs to image environment
RUN mkdir -p /build/kernel-core-rpms/etc \
        && echo "PATH=\"\${PATH}:${PATH}:/usr/lib/dracut/\"" | tee /build/kernel-core-rpms/etc/environment

# Configure the OS
FROM cgr.dev/chainguard/wolfi-base

# Install SSI Service
COPY --from=build-ssi-service /ssi-service /usr/bin/ssi-service

# Install Linux Kernel
# TODO Hardlink kernel paths
COPY --from=build-linux-kernel /build/kernel-core-rpms /fedora

# Second PATH addition
# Add Wofli install PATHs to image environment
RUN source /fedora/etc/environment \
        && echo "PATH=\"${PATH}\"" | tee /etc/environment /etc/environment-wofli

# Patch dracut because we could not find what package on Wolfi provides readlink
# RUN sed -i 's/readonly TMPDIR.*/readonly TMPDIR="$tmpdir"/' /freusr/bin/dracut

# Run depmod to build /lib/modules/${KERNEL_VERSION}/modules.dep which is
# required by dracut for efi creation.
RUN chroot /fedora /usr/bin/bash -c "depmod $(ls /fedora/lib/modules) -a"

# TODO(security) Pinning and hash validation on get-pip
RUN apk update && apk add --no-cache --update-cache \
    curl \
    bash \
    python3 \
    sed \
  && curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python get-pip.py

RUN echo 'mount /dev/sda1 /mnt/boot' | tee /fedora-dracut.sh \
  && echo 'swapon /dev/sda2' | tee -a /fedora-dracut.sh \
  && echo 'mkdir -p /mnt/{proc,dev,sys}' | tee -a /fedora-dracut.sh \
  && echo 'mkdir -p /mnt/var/tmp' | tee -a /fedora-dracut.sh \
  && echo 'mkdir -p /mnt/fedora/var/tmp' | tee -a /fedora-dracut.sh \
  && echo "cat > /mnt/fedora/run-dracut.sh <<'LOL'" | tee -a /fedora-dracut.sh \
  && echo 'export PATH="${PATH}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/dracut/"' | tee -a /fedora-dracut.sh \
  && echo 'export KERNEL_VERSION="$(ls /lib/modules)"' | tee -a /fedora-dracut.sh \
  && echo 'bash -xp /usr/bin/dracut --uefi --kver ${KERNEL_VERSION} --kernel-cmdline "console=ttyS0 root=/dev/sda3"' | tee -a /fedora-dracut.sh \
  && echo 'LOL' | tee -a /fedora-dracut.sh \
  && echo 'arch-chroot /mnt/fedora /bin/bash run-dracut.sh' | tee -a /fedora-dracut.sh \
  && echo 'bootctl --esp-path=/mnt/boot install' | tee -a /fedora-dracut.sh \
  && echo 'for file in $(find /mnt/fedora/boot/); do cp -v $file $(echo $file | sed -e "s/fedora//" -e "s/efi\/EFI/EFI/"); done' | tee -a /fedora-dracut.sh

RUN rm /sbin/init \
  && ln -s /fedora/lib/systemd/systemd /sbin/init

# Install Alice
# ARG ALICE_STATE_OF_ART=0c4b8191b13465980ced3fd1ddfbea30af3d1104
# RUN python3 -m pip install -U setuptools pip wheel
# RUN python3 -m pip install \
#     "https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml" \
#     "https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml-feature-git&subdirectory=feature/git" \
#     "https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=shouldi&subdirectory=examples/shouldi" \
#     "https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml-config-yaml&subdirectory=configloader/yaml" \
#     "https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=dffml-operations-innersource&subdirectory=operations/innersource" \
#     "https://github.com/intel/dffml/archive/${ALICE_STATE_OF_ART}.zip#egg=alice&subdirectory=entities/alice"

ENTRYPOINT bash
```

### SSI Service

- TODO
  - [ ] User systemd socket and service for `/etc/skel` (the place copied from when using `useradd -m`)


### Systemd

**TODO** Currently systemd is within the fedora chroot which causes issues
with it's default library search path on load.

We could try going any of the following routes next or combination thereof.

- Wrapper exec on systemd to set `LD_LIBRARY_PATH` before exec
  - Possibly with all libs explicitly set (`.so` files) to their location within
    the Fedora chroot (`/mnt/fedora` currently).
- Separate Partitions
  - Chroot on getty / docker / k3s start (once we get there)
    - We haven't messed with docker / k3s yet (something to run containers from Wofli)
- Overlayfs?
  - Not sure if this might be helpful here
  - Something something systemd target / service to mount Wolfi over Fedora and then chroot?

STATE_OF_THE_ART: Error bellow for systemd failure to load `.so`'s

```
         Starting initrd-switch-root.service - Switch Root...
[    7.926443] systemd-journald[229]: Received SIGTERM from PID 1 (systemd).
[    8.036984] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00007f00
[    8.037936] CPU: 0 PID: 1 Comm: init Not tainted 5.19.10-200.fc36.x86_64 #1
[/ s  b 8in./0i37n93i6t]:  Hearrdrwaore name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 0.0.0 02/06/2015
[    8.037936] Call Trace:
...
[    8.131416]  </TASK>
r while loading shared libraries: libsystemd-shared-250.so: cannot open shared object file: No such file or directory
```

## Installation in VM

- Using DigitalOcean Fedora host with QEMU installed (`dnf -y install qemu`)
  - First boot and install via arch PXE
    - Mount root partition
      - `# mount /dev/sda3 /mnt`
    - Install bootloader
      - `# bash -x /mnt/fedora/run-dracut.sh`
  - Then reboot without PXE to boot into system
- TODO Piggy Back off arch linux install guide
  - https://wiki.archlinux.org/title/Installation_guide

```bash
#!/usr/bin/env bash
set -xeuo pipefail

# Virtual machine disk image where virtual machine filesystem is stored
VM_DISK=${VM_DISK:-"${HOME}/vm/image.qcow2"}

# Block device we use as an intermediary to mount the guest filesystem from host
VM_DEV=${VM_DEV:-"/dev/nbd0"}

# The directory where we mount the guest filesystem on the host for access and
# modification when not in use by the guest
CHROOT=${CHROOT:-"${HOME}/vm/decentralice-chroot"}

# Extract container image to chroot
IMAGE=${IMAGE:-"localhost/c-distroliess:latest"};

container=$(podman run --rm -d --entrypoint tail "${IMAGE}" -F /dev/null);
trap "podman kill ${container}" EXIT

# Linux kernel command line
CMDLINE=${CMDLINE:-"console=ttyS0 root=/dev/sda3 rw resume=/dev/sda2 init=/usr/bin/init.sh"}

# Location of qemu binary to use
QEMU=${QEMU:-"qemu-system-x86_64"}

# Load the network block device kernel module
sudo modprobe nbd max_part=8

# Unmount the virtual disk image if it is currently mounted
sudo umount -R "${CHROOT}" || echo "Image was not mounted at ${CHROOT}"
# Disconnect the network block device
sudo qemu-nbd --disconnect "${VM_DEV}" || echo "Image was not connected as nbd"

mount_image() {
  sudo qemu-nbd --connect="${VM_DEV}" "${VM_DISK}"
  sudo mount "${VM_DEV}p3" "${CHROOT}"
  sudo mount "${VM_DEV}p1" "${CHROOT}/boot"
}

unmount_image() {
  sudo sync
  sudo umount -R "${CHROOT}"
  sudo qemu-nbd --disconnect "${VM_DEV}"
}

# Check if the block device we are going to use to mount the virtual disk image
# already exists
if [ -b "${VM_DEV}" ]; then
  echo "VM_DEV already exists: ${VM_DEV}" >&2
  # exit 1
fi

# Create the virtual disk image and populate it if it does not exist
if [ ! -f "${VM_DISK}" ]; then
  mkdir -p "${CHROOT}"
  mkdir -p "$(dirname ${VM_DISK})"

  # Create the virtual disk image
  qemu-img create -f qcow2 "${VM_DISK}" 20G

  # Use the QEMU guest utils network block device utility to mount the virtual
  # disk image as the $VM_DEV device
  sudo qemu-nbd --connect="${VM_DEV}" "${VM_DISK}"
  # Partition the block device
  sudo parted "${VM_DEV}" << 'EOF'
mklabel gpt
mkpart primary fat32 1MiB 261MiB
set 1 esp on
mkpart primary linux-swap 261MiB 10491MiB
mkpart primary ext4 10491MiB 100%
EOF
  # EFI partition
  sudo mkfs.fat -F32 "${VM_DEV}p1"
  # swap space
  sudo mkswap "${VM_DEV}p2"
  # Linux root partition
  sudo mkfs.ext4 "${VM_DEV}p3"
  sudo mount "${VM_DEV}p3" "${CHROOT}"
  # Boot partiion
  sudo mkdir "${CHROOT}/boot"
  sudo mount "${VM_DEV}p1" "${CHROOT}/boot"

  # Image to download
  podman cp "${container}:/" "${CHROOT}"

  # Unmount the virtual disk image so the virtual machine can use it
  unmount_image
fi

# Mount the guest file system on the host when we exit the guest
trap mount_image EXIT

if [[ ! -f "$( echo ipxe*.efi)" ]]; then
  curl -sfLO https://archlinux.org/static/netboot/ipxe-arch.16e24bec1a7c.efi
fi

# Only add -kernel for first install
# -kernel ipxe*.efi \

"${QEMU}" \
  -smp cpus=2 \
  -m 4096M \
  -enable-kvm \
  -nographic \
  -cpu host \
  -drive file="${VM_DISK}",index=0,media=disk,format=qcow2 \
  -bios /usr/share/edk2/ovmf/OVMF_CODE.fd $@
```

#### Disk Partitioning

`decentralice.sh` creates a 20 GB virtual disk in QCOW2 format
and formats partitions according to the following example UEFI
recommendations.

- References
  - https://wiki.archlinux.org/title/Installation_guide#Boot_loader
   - https://wiki.archlinux.org/title/Installation_guide#Example_layouts

#### Netboot to Live Install Media

We download the pxe netboot image and use it to boot to an
Arch Linux live image which is usually used for installing
Arch Linux, but there is no reason we can't use it to install
AliceOS.

Choose a contry and mirror then modify 

- References
  - https://archlinux.org/releng/netboot/

```console
$ ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@147.182.254.77 sudo rm -f /root/vm/image.qcow2
Warning: Permanently added '147.182.254.77' (ECDSA) to the list of known hosts.
Connection to 147.182.254.77 closed.
$ python -m asciinema rec --idle-time-limit 0.5 --title "$(date +%4Y-%m-%d-%H-%M-%ss)" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@147.182.254.77 sudo bash decentralice.sh -kernel ipxe*.efi" >(xz --stdout - > "$HOME/asciinema/rec-$(hostname)-$(date +%4Y-%m-%d-%H-%M-%ss).json.xz")
```

#### Mount Partitions from Live Install Media `root` Shell

```console
Boot options: ip=dhcp net.ifnames=0 BOOTIF=01-52:54:00:12:34:56 console=ttyS0

                               Arch Linux Netboot

   Settings
   Architecture: x86_64
   Release: 2022.09.03
   Mirror: http://mirrors.cat.pdx.edu/archlinux/
   Boot options: ip=dhcp net.ifnames=0 BOOTIF=01-52:54:00:12:34:56 console=tt

   Boot Arch Linux
   Drop to iPXE shell
   Reboot
   Exit iPXE











Booting Arch Linux x86_64 2022.09.03 from http://mirrors.cat.pdx.edu/archlinux/

http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/x86_64/vmlinuz-linux... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/x86_64/vmlinuz-linux.ipxe.sig... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/amd-ucode.img... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/amd-ucode.img.ipxe.sig... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/intel-ucode.img... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/intel-ucode.img.ipxe.sig... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/x86_64/initramfs-linux.img... ok
http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/boot/x86_64/initramfs-linux.img.ipxe.sig... ok
:: running early hook [udev]
Starting version 251.4-1-arch
:: running early hook [archiso_pxe_nbd]
:: running hook [udev]
:: Triggering uevents...
:: running hook [memdisk]
:: running hook [archiso]
:: running hook [archiso_loop_mnt]
:: running hook [archiso_pxe_common]
IP-Config: eth0 hardware address 52:54:00:12:34:56 mtu 1500 DHCP
IP-Config: eth0 guessed broadcast address 10.0.2.255
IP-Config: eth0 complete (from 10.0.2.2):
 address: 10.0.2.15        broadcast: 10.0.2.255       netmask: 255.255.255.0
 gateway: 10.0.2.2         dns0     : 10.0.2.3         dns1   : 0.0.0.0
 rootserver: 10.0.2.2 rootpath:
 filename  :
:: running hook [archiso_pxe_nbd]
:: running hook [archiso_pxe_http]
:: running hook [archiso_pxe_nfs]
:: Mounting /run/archiso/httpspace (tmpfs) filesystem, size='75%'
:: Downloading 'http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/x86_64/airootfs.sfs'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  683M  100  683M    0     0  52.3M      0  0:00:13  0:00:13 --:--:-- 65.9M
:: Downloading 'http://mirrors.cat.pdx.edu/archlinux/iso/2022.09.03/arch/x86_64/airootfs.sfs.sig'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   471  100   471    0     0   7009      0 --:--:-- --:--:-- --:--:--  7136
:: Signature verification requested, please wait...
[GNUPG:] GOODSIG 044ABFB932C36814 Arch Linux Release Engineering (Ephemeral Signing Key) <arch-releng@lists.archlinux.org>
Signature is OK, continue booting.
:: Mounting /run/archiso/copytoram (tmpfs) filesystem, size=75%
:: Mounting /run/archiso/cowspace (tmpfs) filesystem, size=256M...
:: Copying rootfs image to RAM...
done.
:: Mounting '/dev/loop0' to '/run/archiso/airootfs'
:: Device '/dev/loop0' mounted successfully.
:: running late hook [archiso_pxe_common]
:: running cleanup hook [udev]

Welcome to Arch Linux!

[   41.600639] I/O error, dev fd0, sector 0 op 0x0:(READ) flags 0x0 phys_seg 1 prio class 0
[  OK  ] Created slice Slice /system/getty.
[  OK  ] Created slice Slice /system/modprobe.
[  OK  ] Created slice Slice /system/serial-getty.
[  OK  ] Created slice User and Session Slice.
[  OK  ] Started Dispatch Password …ts to Console Directory Watch.
[  OK  ] Started Forward Password R…uests to Wall Directory Watch.
[  OK  ] Set up automount Arbitrary…s File System Automount Point.
[  OK  ] Reached target Local Encrypted Volumes.
[  OK  ] Reached target Local Integrity Protected Volumes.
[  OK  ] Reached target Path Units.
...
[  OK  ] Started Getty on tty1.
[  OK  ] Started Serial Getty on ttyS0.
[  OK  ] Reached target Login Prompts.

Arch Linux 5.19.6-arch1-1 (ttyS0)

archiso login: root
To install Arch Linux follow the installation guide:
https://wiki.archlinux.org/title/Installation_guide

For Wi-Fi, authenticate to the wireless network using the iwctl utility.
For mobile broadband (WWAN) modems, connect with the mmcli utility.
Ethernet, WLAN and WWAN interfaces using DHCP should work automatically.

After connecting to the internet, the installation guide can be accessed
via the convenience script Installation_guide.


Last login: Sun Sep 25 23:55:20 on tty1
root@archiso ~ # mount /dev/sda3 /mnt
root@archiso ~ # bash -x /mnt/fedora-dracut.sh
```

- Now without PXE boot
  - Currently systemd takes the 

```console
$ python -m asciinema rec --idle-time-limit 0.5 --title "$(date +%4Y-%m-%d-%H-%M-%ss)" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@147.182.254.77 sudo bash decentralice.sh" >(xz --stdout - > "$HOME/asciinema/rec-$(hostname)-$(date +%4Y-%m-%d-%H-%M-%ss).json.xz")
+ VM_DISK=/root/vm/image.qcow2
+ VM_DEV=/dev/nbd0
+ CHROOT=/root/vm/decentralice-chroot
+ IMAGE=localhost/c-distroliess:latest
++ podman run --rm -d --entrypoint tail localhost/c-distroliess:latest -F /dev/null
+ container=1b79597e28cbc714043992a46d0498bd31a449c773784e0fab4629ee11244ce1
+ trap 'podman kill 1b79597e28cbc714043992a46d0498bd31a449c773784e0fab4629ee11244ce1' EXIT
+ CMDLINE='console=ttyS0 root=/dev/sda3 rw resume=/dev/sda2 init=/usr/bin/init.sh'
+ QEMU=qemu-system-x86_64
+ sudo modprobe nbd max_part=8
+ sudo umount -R /root/vm/decentralice-chroot
+ sudo qemu-nbd --disconnect /dev/nbd0
/dev/nbd0 disconnected
+ '[' -b /dev/nbd0 ']'
+ echo 'VM_DEV already exists: /dev/nbd0'
VM_DEV already exists: /dev/nbd0
+ '[' '!' -f /root/vm/image.qcow2 ']'
+ trap mount_image EXIT
++ echo ipxe-arch.16e24bec1a7c.efi
+ [[ ! -f ipxe-arch.16e24bec1a7c.efi ]]
+ qemu-system-x86_64 -smp cpus=2 -m 4096M -enable-kvm -nographic -cpu host -drive file=/root/vm/image.qcow2,index=0,media=disk,format=qcow2 -bios /usr/shar
e/edk2/ovmf/OVMF_CODE.fd
BdsDxe: loading Boot0001 "Linux Boot Manager" from HD(1,GPT,5ED5E31E-F9DF-4168-B087-18AB1EF33E24,0x800,0x82000)/\EFI\systemd\systemd-bootx64.efi
BdsDxe: starting Boot0001 "Linux Boot Manager" from HD(1,GPT,5ED5E31E-F9DF-4168-B087-18AB1EF33E24,0x800,0x82000)/\EFI\systemd\systemd-bootx64.efi
EFI stub: Loaded initrd from LINUX_EFI_INITRD_MEDIA_GUID device path
[    0.000000] Linux version 5.19.10-200.fc36.x86_64 (mockbuild@bkernel01.iad2.fedoraproject.org) (gcc (GCC) 12.2.1 20220819 (Red Hat 12.2.1-2), GNU ld ver
sion 2.37-36.fc36) #1 SMP PREEMPT_DYNAMIC Tue Sep 20 15:15:53 UTC 2022
[    0.000000] Command line:  console=ttyS0 root=/dev/sda3
[    0.000000] x86/fpu: Supporting XSAVE feature 0x001: 'x87 floating point registers'
[    0.000000] x86/fpu: Supporting XSAVE feature 0x002: 'SSE registers'
[    0.000000] x86/fpu: Supporting XSAVE feature 0x004: 'AVX registers'
[    0.000000] x86/fpu: xstate_offset[2]:  576, xstate_sizes[2]:  256
[    0.000000] x86/fpu: Enabled xstate features 0x7, context size is 832 bytes, using 'standard' format.
[    0.000000] signal: max sigframe size: 1776
[    0.000000] BIOS-provided physical RAM map:
...
[    4.505931] systemd[1]: dracut-pre-udev.service - dracut pre-udev hook was skipped because all trigger condition checks failed.
[    4.511214] audit: type=1130 audit(1664171381.024:4): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=systemd-vconsole-setup comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
[    4.521203] systemd[1]: Starting systemd-tmpfiles-setup-dev.service - Create Static Device Nodes in /dev...
         Starting systemd-tmpfiles-…ate Static Device Nodes in /dev...
[    4.530842] systemd[1]: Started systemd-journald.service - Journal Service.
[  OK  ] Started systemd-journald.service - Journal Service.
         Starting syste[    4.543614] audit: type=1130 audit(1664171381.072:5): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=systemd-journald comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
md-tmpfiles-… Volatile Files and Directories...
[  OK  ] Finished systemd-tmpfiles-…reate Static Device Nodes in /dev.
         Starting systemd-udevd.ser…ger for Device Events and Files..[    4.570653] audit: type=1130 audit(1664171381.095:6): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=systemd-tmpfiles-setup-dev comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
.[    4.580930] audit: type=1334 audit(1664171381.097:7): prog-id=6 op=LOAD

[    4.596257] audit: type=1334 audit(1664171381.097:8): prog-id=7 op=LOAD
[    4.596303] audit: type=1334 audit(1664171381.097:9): prog-id=8 op=LOAD
[  OK  ] Finished systemd-tmpfiles-…te Volatile Files and Directories.
[    4.614382] audit: type=1130 audit(1664171381.146:10): pid=1 uid=0 auid=4294967295 ses=4294967295 subj=kernel msg='unit=systemd-tmpfiles-setup comm="systemd" exe="/usr/lib/systemd/systemd" hostname=? addr=? terminal=? res=success'
[  OK  ] Started systemd-udevd.serv…nager for Device Events and Files.
         Starting systemd-udev-trig…[0m - Coldplug All udev Devices...
[  OK  ] Finished systemd-udev-trig…e - Coldplug All udev Devices.
[  OK  ] Reached target sysinit.target - System Initialization.
[  OK  ] Reached target basic.target - Basic System.
[  OK  ] Reached target remote-fs-p…eparation for Remote File Systems.
[  OK  ] Reached target remote-fs.target - Remote File Systems.
[  OK  ] Found device dev-sda3.device - QEMU_HARDDISK primary.
[  OK  ] Reached target initrd-root…e.target - Initrd Root Device.
         Starting systemd-fsck-root… File System Check on /dev/sda3...
[  OK  ] Finished systemd-fsck-root… - File System Check on /dev/sda3.
         Mounting sysroot.mount - /sysroot...
[    5.543281] EXT4-fs (sda3): mounted filesystem with ordered data mode. Quota mode: none.
[  OK  ] Mounted sysroot.mount - /sysroot.
[  OK  ] Reached target initrd-root…get - Initrd Root File System.
         Starting initrd-parse-etc.…onfiguration from the Real Root...
[  OK  ] Finished initrd-parse-etc.… Configuration from the Real Root.
[  OK  ] Reached target initrd-fs.target - Initrd File Systems.
[  OK  ] Reached target initrd.target - Initrd Default Target.
         Starting dracut-pre-pivot.…acut pre-pivot and cleanup hook...
[  OK  ] Finished dracut-pre-pivot.…dracut pre-pivot and cleanup hook.
         Starting initrd-cleanup.se…ng Up and Shutting Down Daemons...
[  OK  ] Stopped target timers.target - Timer Units.
[  OK  ] Stopped dracut-pre-pivot.s…dracut pre-pivot and cleanup hook.
[  OK  ] Stopped target initrd.target - Initrd Default Target.
[  OK  ] Stopped target basic.target - Basic System.
[  OK  ] Stopped target initrd-root…e.target - Initrd Root Device.
[  OK  ] Stopped target initrd-usr-…get - Initrd /usr File System.
[  OK  ] Stopped target paths.target - Path Units.
[  OK  ] Stopped systemd-ask-passwo…quests to Console Directory Watch.
[  OK  ] Stopped target remote-fs.target - Remote File Systems.
[  OK  ] Stopped target remote-fs-p…eparation for Remote File Systems.
[  OK  ] Stopped target slices.target - Slice Units.
[  OK  ] Stopped target sockets.target - Socket Units.
[  OK  ] Stopped target sysinit.target - System Initialization.
[  OK  ] Stopped target swap.target - Swaps.
[  OK  ] Stopped systemd-sysctl.service - Apply Kernel Variables.
[  OK  ] Stopped systemd-tmpfiles-s…te Volatile Files and Directories.
[  OK  ] Stopped target local-fs.target - Local File Systems.
[  OK  ] Stopped systemd-udev-trigg…e - Coldplug All udev Devices.
         Stopping systemd-udevd.ser…ger for Device Events and Files...
[  OK  ] Stopped systemd-vconsole-s…rvice - Setup Virtual Console.
[  OK  ] Finished initrd-cleanup.se…ning Up and Shutting Down Daemons.
[  OK  ] Stopped systemd-udevd.serv…nager for Device Events and Files.
[  OK  ] Closed systemd-udevd-contr….socket - udev Control Socket.
[  OK  ] Closed systemd-udevd-kernel.socket - udev Kernel Socket.
         Starting initrd-udevadm-cl…ice - Cleanup udev Database...
[  OK  ] Stopped systemd-tmpfiles-s…reate Static Device Nodes in /dev.
[  OK  ] Stopped kmod-static-nodes.…reate List of Static Device Nodes.
[  OK  ] Finished initrd-udevadm-cl…rvice - Cleanup udev Database.
[  OK  ] Reached target initrd-switch-root.target - Switch Root.
         Starting initrd-switch-root.service - Switch Root...
[    7.926443] systemd-journald[229]: Received SIGTERM from PID 1 (systemd).
[    8.036984] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00007f00
[    8.037936] CPU: 0 PID: 1 Comm: init Not tainted 5.19.10-200.fc36.x86_64 #1
[/ s  b 8in./0i37n93i6t]:  Hearrdrwaore name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 0.0.0 02/06/2015
[    8.037936] Call Trace:
[    8.037936]  <TASK>
[    8.037936]  dump_stack_lvl+0x44/0x5c
[    8.037936]  panic+0xfb/0x2b1
[    8.037936]  do_exit.cold+0x15/0x15
[    8.037936]  do_group_exit+0x2d/0x90
[    8.037936]  __x64_sys_exit_group+0x14/0x20
[    8.037936]  do_syscall_64+0x5b/0x80
[    8.037936]  ? do_syscall_64+0x67/0x80
[    8.037936]  entry_SYSCALL_64_after_hwframe+0x63/0xcd
[    8.037936] RIP: 0033:0x7f9b61282911
[    8.037936] Code: f7 d8 89 01 48 83 c8 ff c3 be e7 00 00 00 ba 3c 00 00 00 eb 11 0f 1f 40 00 89 d0 0f 05 48 3d 00 f0 ff ff 77 1c f4 89 f0 0f 05 <48> 3d 00 f0 ff ff 76 e7 f7 d8 89 05 7f 29 01 00 eb dd 0f 1f 44 00
[    8.037936] RSP: 002b:00007ffd45b6dc78 EFLAGS: 00000246 ORIG_RAX: 00000000000000e7
[    8.037936] RAX: ffffffffffffffda RBX: 00007f9b6128caf8 RCX: 00007f9b61282911
[    8.037936] RDX: 000000000000003c RSI: 00000000000000e7 RDI: 000000000000007f
[    8.037936] RBP: 00007f9b6126017f R08: 00007ffd45b6dc88 R09: 000000006128a000
[    8.037936] R10: 0000000000000020 R11: 0000000000000246 R12: 0000000000000002
[    8.129077] R13: 0000000000000001 R14: 00007f9b612601a0 R15: 0000000000000000
[    8.131416]  </TASK>
r while loading shared libraries: libsystemd-shared-250.so: cannot open shared object file: No such file or directory
[    8.131416] Kernel Offset: 0x5000000 from 0xffffffff81000000 (relocation range: 0xffffffff80000000-0xffffffffbfffffff)
[    8.131416] ---[ end Kernel panic - not syncing: Attempted to kill init! exitcode=0x00007f00 ]---


<Ctrl-a x>

QEMU: Terminated
```

- TODO
  - `--fstab /etc/fstab`?
    - Not sure if we need this yet but saving here until dracut we get `EXIT_SUCCESS`
  - Add custom bootloader image
    - slice image from alice unbirthday gif-2-cli gif and convert to bitmap
    - References
      - https://man7.org/linux/man-pages/man8/dracut.8.html
        - > `--uefi-splash-image <FILE>`
          >   - Specifies the UEFI stub loader’s splash image. Requires
          >     bitmap (.bmp) image format.

### Alice

Install Alice!

## Misc.

- TODO
  - [ ] Updates for fedora packages (aka kernel) will need to be handled.
    - We might just re-roll and pull only the layers with kernel stuff? TBD
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