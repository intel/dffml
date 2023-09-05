## 2022-10-09 @pdxjohnny Engineering Logs: OS DecentrAlice

- References
  - https://gist.github.com/pdxjohnny/1cd906b3667d8e9c956dd624f295aa2f
  - https://github.com/dracutdevs/dracut/blob/master/man/dracut.usage.asc#injecting-custom-files
    - `/etc/fstab` ?
  - https://kernel.org/doc/html/v4.14/admin-guide/kernel-parameters.html
    - https://elixir.bootlin.com/linux/v6.0/source/init/do_mounts.c#L277

**do.wolfi-fedora.sh**

```bash
set -u

fedora_setup() {
  useradd -m "${CREATE_USER}"
  echo "${CREATE_USER}   ALL=(ALL:ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
  cp -r ~/.ssh "/home/${CREATE_USER}/.ssh"
  chown -R "${CREATE_USER}:" "/home/${CREATE_USER}"

  dnf upgrade -y
  dnf install -y podman qemu tmux curl tar sudo

tee -a /etc/environment <<'EOF'
EDITOR=vim
CHROOT=/tmp/decentralice-chroot
BZ_IMAGE="$(find ${CHROOT} -name vmlinuz)"
EOF
}

fedora_setup
```

Run install

```console
$ python -c 'import pathlib, sys; p = pathlib.Path(sys.argv[-1]); p.write_bytes(p.read_bytes().replace(b"\r", b""))' do.wolfi-fedora.sh
$ export REC_TITLE="Rolling Alice: Engineering Logs: OS DecentrAlice"; export REC_HOSTNAME="build.container.image.nahdig.com"; python3.9 -m asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@143.110.152.152 CREATE_USER=$USER bash -xe < do.wolfi-fedora.sh" >(xz --stdout - > "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).json.xz")
```

Run build

**Dockerfile**

```dockerfile
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
FROM registry.fedoraproject.org/fedora AS osdecentralice-fedora-builder

RUN mkdir -p /build/fedora \
  && source /usr/lib/os-release \
  && dnf -y install \
    --installroot=/build/fedora \
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
RUN mkdir -p /build/fedora/etc \
        && echo "PATH=\"\${PATH}:${PATH}:/usr/lib/dracut/\"" | tee /build/fedora/etc/environment

RUN echo 'mount /dev/sda1 /mnt/boot' | tee /install-bootloader.sh \
  && echo 'swapon /dev/sda2' | tee -a /install-bootloader.sh \
  && echo 'mkdir -p /mnt/{proc,dev,sys}' | tee -a /install-bootloader.sh \
  && echo 'mkdir -p /mnt/var/tmp' | tee -a /install-bootloader.sh \
  && echo "cat > /mnt/run-dracut.sh <<'EOF'" | tee -a /install-bootloader.sh \
  && echo 'export PATH="${PATH}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/dracut/"' | tee -a /install-bootloader.sh \
  && echo 'export KERNEL_VERSION="$(ls /lib/modules)"' | tee -a /install-bootloader.sh \
  && echo 'bash -xp /usr/bin/dracut --uefi --kver ${KERNEL_VERSION} --kernel-cmdline "console=ttyS0 root=/dev/sda3"' | tee -a /install-bootloader.sh \
  && echo 'EOF' | tee -a /install-bootloader.sh \
  && echo 'arch-chroot /mnt /bin/bash run-dracut.sh' | tee -a /install-bootloader.sh \
  && echo 'bootctl --esp-path=/mnt/boot install' | tee -a /install-bootloader.sh \
  && mv /install-bootloader.sh /build/fedora/usr/bin/install-bootloader.sh \
  && chmod 755 /build/fedora/usr/bin/install-bootloader.sh

RUN rm -f /sbin/init \
  && ln -s /lib/systemd/systemd /sbin/init

# The root of the root fs
FROM scratch AS osdecentralice

COPY --from=osdecentralice-fedora-builder /build/fedora /

# Run depmod to build /lib/modules/${KERNEL_VERSION}/modules.dep which is
# required by dracut for efi creation.
# RUN chroot /build/fedora /usr/bin/bash -c "depmod $(ls /build/fedora/lib/modules) -a"
ARG LINUX_CMDLINE_ROOT="PARTLABEL=Fedora"
RUN depmod $(ls /lib/modules) -a \
  && export PATH="${PATH}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/dracut/" \
  && export KERNEL_VERSION="$(ls /lib/modules)" \
  && echo 'PARTLABEL=EFI          /boot           vfat            rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro        0 2' | tee -a /etc/fstab \
  && echo 'PARTLABEL=Swap              none            swap            defaults,pri=100        0 0' | tee -a /etc/fstab \
  && echo 'PARTLABEL=Fedora       /               ext4            rw,relatime     0 1' | tee -a /etc/fstab \
  && echo 'PARTLABEL=Wolfi       /wolfi          ext4            rw,relatime     0 2' | tee -a /etc/fstab \
  && bash -xp /usr/bin/dracut \
    --include /etc/fstab /etc/fstab \
    --uefi \
    --kver ${KERNEL_VERSION} \
    --kernel-cmdline "rd.luks=0 rd.lvm=0 rd.md=0 rd.dm=0 rd.shell=ttyS0 console=ttyS0 root=${LINUX_CMDLINE_ROOT}"

# Configure getty on ttyS0 for QEMU serial
# References:
# - https://www.freedesktop.org/software/systemd/man/systemd-getty-generator.html
# - https://www.thegeekdiary.com/centos-rhel-7-how-to-configure-serial-getty-with-systemd/
RUN cp /usr/lib/systemd/system/serial-getty@.service /etc/systemd/system/serial-getty@ttyS0.service \
  && ln -s /etc/systemd/system/serial-getty@ttyS0.service /etc/systemd/system/getty.target.wants/

# The Wolfi based chroot (the primary, Fedora just for boot)
FROM cgr.dev/chainguard/wolfi-base AS osdecentralice-wolfi-base

# Install SSI Service
COPY --from=build-ssi-service /ssi-service /usr/bin/ssi-service

# TODO(security) Pinning and hash validation on get-pip
RUN apk update && apk add --no-cache --update-cache \
    curl \
    bash \
    python3 \
    sed \
  && curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
  && python get-pip.py

# Second PATH addition
# Add Wofli install PATHs to image environment
RUN echo "PATH=\"${PATH}\"" | tee /etc/environment

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

FROM osdecentralice

# Install SSI Service
COPY --from=osdecentralice-wolfi-base / /wolfi

ENTRYPOINT bash
```

```console
export REC_TITLE="Rolling Alice: Engineering Logs: OS DecentrAlice"; export REC_HOSTNAME="build.container.image.nahdig.com"; python3.9 -m asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@143.110.152.152 sudo podman build -t osdecentralice:latest - < Dockerfile" >(xz --stdout - > "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).json.xz")
```

Run VM

```bash
#!/usr/bin/env bash
set -xeuo pipefail

# URL to the iPXE EFI firmawre to use boot for live install
IPXE_EFI_ARCHLINUX_VERSION=${IPXE_EFI_ARCHLINUX_VERSION:-"16e24bec1a7c"}
IPXE_EFI_URL=${IPXE_EFI_URL:-"https://archlinux.org/static/netboot/ipxe-arch.${IPXE_EFI_ARCHLINUX_VERSION}.efi"}

# Path on disk to iPXE EFI firmawre to use boot for live install
IPXE_EFI_PATH=${IPXE_EFI_PATH:-"${HOME}/vm/ipxe-arch.${IPXE_EFI_ARCHLINUX_VERSION}.efi"}

# Virtual machine disk image where virtual machine filesystem is stored
VM_DISK=${VM_DISK:-"${HOME}/vm/image.qcow2"}
VM_KERNEL=${VM_KERNEL:-"${HOME}/vm/kernel"}

# Block device we use as an intermediary to mount the guest filesystem from host
VM_DEV=${VM_DEV:-"/dev/nbd0"}

# The directory where we mount the guest filesystem on the host for access and
# modification when not in use by the guest
STAGING=${STAGING:-"${HOME}/vm/decentralice-staging-chroot"}
CHROOT=${CHROOT:-"${HOME}/vm/decentralice-chroot"}

# Extract container image to chroot
IMAGE=${IMAGE:-"localhost/osdecentralice:latest"};

container=$(podman run --rm -d --entrypoint tail "${IMAGE}" -F /dev/null);
trap "podman kill ${container}" EXIT
sleep 1

# Linux kernel command line
CMDLINE=${CMDLINE:-"console=ttyS0 root=/dev/sda3 rw resume=/dev/sda2 init=/usr/bin/init.sh"}

# Location of qemu binary to use
QEMU=${QEMU:-"qemu-system-x86_64"}

# Load the network block device kernel module
modprobe nbd max_part=8

# Unmount the virtual disk image if it is currently mounted
umount -R "${CHROOT}" || echo "Image was not mounted at ${CHROOT}"
# Disconnect the network block device
qemu-nbd --disconnect "${VM_DEV}" || echo "Image was not connected as nbd"

mount_image() {
  qemu-nbd --connect="${VM_DEV}" "${VM_DISK}"
  mount "${VM_DEV}p3" "${CHROOT}"
  mount "${VM_DEV}p4" "${CHROOT}/wolfi"
  mount "${VM_DEV}p1" "${CHROOT}/boot"
}

unmount_image() {
  sync
  umount -R "${CHROOT}"
  qemu-nbd --disconnect "${VM_DEV}"
}

run_vm() {
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
    qemu-img create -f qcow2 "${VM_DISK}" 30G

    # Use the QEMU guest utils network block device utility to mount the virtual
    # disk image as the $VM_DEV device
    qemu-nbd --connect="${VM_DEV}" "${VM_DISK}"
    # Partition the block device
    parted -s "${VM_DEV}" -- \
      mklabel gpt \
      mkpart primary fat32 1MiB 261MiB \
      "set" 1 esp on \
      mkpart primary linux-swap 261MiB 10491MiB \
      mkpart primary ext4 10491MiB 15491MiB \
      name 3 fedora \
      mkpart primary ext4 15491MiB "100%" \
      name 4 wolfi
    # EFI partition
    mkfs.fat -F32 -n EFI "${VM_DEV}p1"
    # swap space
    mkswap "${VM_DEV}p2" -L Swap
    # Linux root partition (fedora)
    mkfs.ext4 "${VM_DEV}p3" -L Fedora
    mount "${VM_DEV}p3" "${CHROOT}"
    # Linux root partition (wolfi)
    mkfs.ext4 "${VM_DEV}p4" -L Wolfi
    mkdir "${CHROOT}/wolfi"
    mount "${VM_DEV}p4" "${CHROOT}/wolfi"
    # Boot partiion
    mkdir "${CHROOT}/boot"
    mount "${VM_DEV}p1" "${CHROOT}/boot"

    # Image to download
    podman cp "${container}:/" "${STAGING}"
    set +e
    for mount in $(echo boot wolfi .); do for file in $(ls -a "${STAGING}/${mount}" | grep -v '^\.\.$' | grep -v '^\.$'); do mv "${STAGING}/${mount}/${file}" "${CHROOT}/${mount}/" || true; done; rm -rf "${STAGING}/${mount}" || true; done
    set -e
    GUEST_KERNEL_EFI=$(find "${CHROOT}/boot" -name 'linux*.efi')
    cp "${GUEST_KERNEL_EFI}" "${VM_KERNEL}"
    # TODO Copy out kernel for use for first time bootloader install call with
    # -kernel $KERNEL.efi -no-reboot TODO Ideally check for successful boot
    # before publish.

    #   $ sudo dnf -y install arch-install-scripts
    # genfstab -t UUID "${CHROOT}" | tee "${CHROOT}/etc/fstab"
    # export KERNEL_VERSION="$(ls ${CHROOT}/lib/modules)"
    # chroot "${CHROOT}" /usr/bin/bash -xp /usr/bin/dracut \
      # --fstab /etc/fstab \
      # --add-drivers ext4 \
      # --uefi \
      # --kver ${KERNEL_VERSION} \
      # --kernel-cmdline "rd.luks=0 rd.lvm=0 rd.md=0 rd.dm=0 console=ttyS0"
    # --kernel-cmdline "rd.luks=0 rd.lvm=0 rd.md=0 rd.dm=0 console=ttyS0 root=${LINUX_CMDLINE_ROOT}"

    # Unmount the virtual disk image so the virtual machine can use it
    unmount_image
  fi

  # TODO Move into disk creation
  # Copy out kernel for use for first time bootloader install call with
  #   -kernel $KERNEL.efi -no-reboot
  "${QEMU}" \
    -no-reboot \
    -kernel "${VM_KERNEL}" \
    -append "console=ttyS0 systemd.log_level=9 rd.shell rd.debug log_buf_len=1M root=PARTLABEL=fedora" \
    -smp cpus=2 \
    -m 4096M \
    -enable-kvm \
    -nographic \
    -cpu host \
    -drive file="${VM_DISK}",if=virtio,aio=threads,format=qcow2 \
    -bios /usr/share/edk2/ovmf/OVMF_CODE.fd
  # -drive file="${VM_DISK}",index=0,media=disk,format=qcow2 \

  exit 0

  if [[ ! -f "${IPXE_EFI_PATH}" ]]; then
    curl -sfLC - -o "${IPXE_EFI_PATH}" "${IPXE_EFI_URL}"
  fi

  # Only add -kernel for first install
  # -kernel /vm/ipxe*.efi \

  "${QEMU}" \
    -smp cpus=2 \
    -m 4096M \
    -enable-kvm \
    -nographic \
    -cpu host \
    -drive file="${VM_DISK}",index=0,media=disk,format=qcow2 \
    -bios /usr/share/edk2/ovmf/OVMF_CODE.fd $@
}

run_vm $@
```

**TODO** Do we have to boot to PXE? Can we boot directly to the EFI stub we just created with dracut?
Run install via arch live environment iPXE booted to

```console
$ scp -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no decentralice.sh $USER@143.110.152.152:./
$ ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@143.110.152.152 sudo rm -f /root/vm/image.qcow2
$ export REC_TITLE="Rolling Alice: Engineering Logs: OS DecentrAlice"; export REC_HOSTNAME="build.container.image.nahdig.com"; python3.9 -m asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@143.110.152.152 sudo bash decentralice.sh -kernel /root/vm/kernel -no-reboot" >(xz --stdout - > "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).json.xz")
```

Run normal startup

```console
$ scp -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no decentralice.sh $USER@143.110.152.152:./
$ export REC_TITLE="Rolling Alice: Engineering Logs: OS DecentrAlice"; export REC_HOSTNAME="build.container.image.nahdig.com"; python3.9 -m asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no $USER@143.110.152.152 bash decentralice.sh" >(xz --stdout - > "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).json.xz")
```

Run regular ssh session for debug

```console
$ export REC_TITLE="Rolling Alice: Engineering Logs: OS DecentrAlice"; export REC_HOSTNAME="build.container.image.nahdig.com"; python3.9 -m asciinema rec --idle-time-limit 0.5 --title "$(date -Iseconds): ${REC_HOSTNAME} ${REC_TITLE}" --command "ssh -t -i ~/.ssh/nahdig -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o PasswordAuthentication=no root@143.110.152.152" >(xz --stdout - > "$HOME/asciinema/${REC_HOSTNAME}-rec-$(date -Iseconds).json.xz")
```

```console
[pdxjohnny@fedora-s-4vcpu-8gb-sfo3-01 ~]$ sudo fdisk -l /dev/nbd0 -x
Disk /dev/nbd0: 30 GiB, 32212254720 bytes, 62914560 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: DEC7B131-9DBB-4FD5-8789-AE383F16C1C5
First usable LBA: 34
Last usable LBA: 62914526
Alternative LBA: 62914559
Partition entries starting LBA: 2
Allocated partition entries: 128
Partition entries ending LBA: 33

Device         Start      End  Sectors Type-UUID                            UUID                                 Name    Attrs
/dev/nbd0p1     2048   534527   532480 C12A7328-F81F-11D2-BA4B-00A0C93EC93B 6767EC6D-A612-4B1F-B390-8F15284F134E primary
/dev/nbd0p2   534528 21485567 20951040 0657FD6D-A4AB-43C4-84E5-0933C84B4F4F 58D5880D-D3EA-4B57-85AB-E08A3AB8D6F3 primary
/dev/nbd0p3 21485568 31725567 10240000 0FC63DAF-8483-4772-8E79-3D69D8477DE4 38CC9A55-724F-47D6-A17E-EF6F2DAB2F1F fedora
/dev/nbd0p4 31725568 62912511 31186944 0FC63DAF-8483-4772-8E79-3D69D8477DE4 B8D4F18B-40CF-4A69-A6F4-BB3C1DDB9ABC wolfi
```

Got dropped to dracut shell

```console
:/root# blkid
/dev/vda4: LABEL="Wolfi" UUID="1b01665f-1a3d-4bde-a9b4-cc484529e999" BLOCK_SIZE="4096" TYPE="ext4" PARTLABEL="wolfi" PARTUUID="dfc228b1-76d4-42ef-8132-f1a0707ea3e1"
/dev/vda2: LABEL="Swap" UUID="d212c4f0-c61a-4762-9b5f-af2c2595b0d1" TYPE="swap" PARTLABEL="primary" PARTUUID="88a54dc7-ed14-431c-a9e9-39913d5cea7e"
/dev/vda3: LABEL="Fedora" UUID="559359d9-d88b-40d2-a0ae-ca0ce68b7fc7" BLOCK_SIZE="4096" TYPE="ext4" PARTLABEL="fedora" PARTUUID="2fd26f17-508e-4fab-a8e7-e9f434fc2e94"
/dev/vda1: UUID="BEB1-9DC4" BLOCK_SIZE="512" TYPE="vfat" PARTLABEL="primary" PARTUUID="0699ba50-02d6-4ef6-a0b2-d1f1ab03f6f6"
```

- TODO
- Future
  - [ ] `alice shell` overlay to CSP of choice to start VM and then ssh in with recorded session (optionally via overlays)
    - https://github.com/intel/dffml/commit/54a272822eeef759668b7396cf8c70beca352687
  - [ ] kernel cmdline (bpf?) DERP -> wireguard -> nfs (overlays applied as systemd files added)