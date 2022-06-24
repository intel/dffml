### Nice to have

- [ ] DID as CBOR

### Security Considerations

- [ ] Peer DID size inspection on pre-receive / receive from Distributed Web Node (DWN)
  - [ ] Default strategic plan overlay enabled to not write to disk or receive to memory DIDs beyond certain size threshold. Can traverse input network to determine system local resource constraints - can go through operations to trigger refresh of local resources, see recording for telemetry example.
- [ ] DID post quantum alg support

### Everything as a Blockchain

- [ ] Operations to put data in / get data out / dataflows as class to implement interfaces which call operations. Thereby creating ability to transparently proxy information into / output web3 space via input networks acting as bridges. Input network made from dataflow as class. For example, on add input method, encode to DID, store in source by calling add method of input network defined via dataflow as class within dataflow which uses operations to encode manifest to DID doc which when read by shim results in a system context which is executed to retrieve the next stage (in this case this is the `Input.value`).
  - [ ] Operation which is a proxy for calling a class's method. `config.cls_instance.method_name()` can be implemented via decorator. Extend `@op` to create an imp enter which enters the cls_instance context, if not already entered by another operations also using class via shared config.