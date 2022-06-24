When your top level system context is looking at a DID to run dataflow within it. It should:

- Have an overylayed dataflow which understands the DID format, and is looking to parse it.
  - Means we should have a strategic plan in place which calls to the shim operation (make it an operation) and can be directed via flow to take any input matching specific definitions or origins and attempt to convert it to a plugin instance. 