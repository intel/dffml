## 2022-10-09 @pdxjohnny Engineering Logs

- Supply Chain
  - https://medium.com/@nis.jespersen/the-united-nations-trust-graph-d65af7b0b678
- Collective Intelligence
  - Cattle not pets with state
    - Bringing agents into equilibrium (critical velocity) state
    - https://twitter.com/hardmaru/status/1577159167415984128
  - grep discussion the cells are working tigether
  - https://journals.sagepub.com/doi/10.1177/26339137221114874
    - > The better results from CI are attributed to three factors: diversity, independence, and decentralization
- Linux
  - https://github.com/kees/kernel-tools/tree/trunk/coccinelle
- Time
  - cycle of time repeats
    - tick
    - Tock
  - Relative cycles
  - threads of time / Number / critical velocity in cycle relation to relativity (aligned system contexts) vol 6? Or before for thought arbitrage
- KERI
  - https://github.com/WebOfTrust/ietf-did-keri/blob/main/draft-pfeairheller-did-keri.md
  - https://github.com/SmithSamuelM/Papers/blob/master/presentations/KERI_for_Muggles.pdf

Source: KERI Q&A

> BDKrJxkcR9m5u1xs33F5pxRJP6T7hJEbhpHrUtlDdhh0   
<- this the bare bones _identifier_
> did:aid:BDKrJxkcR9m5u1xs33F5pxRJP6T7hJEbhpHrUtlDdhh0/path/to/resource?name=secure#really 
<- this is _a call to resolve_ the identifier on the web
> Currently `KERI` is just code, that can be tested and executed in a terminal on the command line. Private key management of KERI will look like `wallets`.
> Key Event Logs (`KEL`) and Key Event Receipt Log (`KERL`) are files with lots of encrypted stuff in there.
- TODO
  - [ ] download_nvd fork to save restore pip cache via wheel (could later even package static_bin_operation_download)
  - [ ] OS DecentrAlice
    - [ ] Add KERI PY/watcher code to image
      - [ ] Enable as comms channel on boot
      - [ ] Connect to DERP network
    - [ ] Secret provisioning
      - [ ] DERP servers
      - [ ] Roots to trust
        - [ ] eventually data flows
    - [ ] fedora cloud-init etc.
    - [ ] Deploy on DO
    - [ ] Deploy with QEMU
    - [ ] CVE Bin Tool
      - [ ] Periodic (cron/systemd timer) scan and report both partitions to some DFFML source via dataflow run
- Future
  - grep -i ‘Down Distrowatch line”
  - Deploy with firecracker