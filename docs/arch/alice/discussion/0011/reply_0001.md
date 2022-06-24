For VM image feature extraction:

- https://www.kitploit.com/2022/05/leaf-linux-evidence-acquisition.html
- https://www.cgsecurity.org/wiki/PhotoRec
- Mount via loopback for raw disks (locality is OS, loopback mount can only be run if it has access to a linux kernel, we cannot live migrate it unless we have something which understands how to live migrate all OS decendent resources. Ir we can migrate by just blowing away the loopback point from the cache? Letting it regenerate it bybrunning the operation again and then loading the file to it).
- The QEMU userspace mount of qcow2 images, handled similary
- Should also fijish out the flow where we make the full VM image with bootloader and all that supports hibernate