- can use web3 as cve bin tool mirrors / torrent / webtorrent / ipfs
- Bridging the web2/web3 Identity Gap
- `did:key` is a method 0 `did:peer` (inception key without doc)
  - Add top level context overlay switch to command line and high level run. Use this to pass dataflow which might load from `~/.local/` or somewhere else. Always require argument, never load from disk a default, people can make aliases or use environment variables to set. Always load via env vars or CLI or python API. Never assume disk.

https://identity.foundation/peer-did-method-spec/#generation-method

> The DID doc offers no endpoint. This makes the DID functionally equivalent to a `did:key` value, and visually similar, except that a peer DID will have the numeric algorithm as a prefix, before the multibase encoded, multicodec-encoded public key. For example, `did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH` is equivalent to `did:peer:0z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH`. The `did:peer` version differs in that it is upgradeable to a dynamically updatable DID with full DID doc and endpoints, simply using deltas, as long as the first delta is authenticated by the inception key.

https://github.com/intel/dffml/issues/1381