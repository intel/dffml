## Notes

Wnode: WorkerNode
Onode: OrchestratorNode
Wctx: WorkerNodeContext

- Worker nodes are initialised with a set of operations which they can run.
- Worker nodes wait for a connection request ``ConnectToOrchestratorNode``
- An Onode is initialized with dataflow and configarations for operations if any
- Onode sends ``ConnectToOrchestratorNode``
- Wnodes receives connection request and spins up a new context which only processes
    messages from the Onode which it is paired with. This is ensured by prefixing
    subjects from Onode with its Id and checking for this when receiving messages
    in Wnode
- Wnode context sends back a list of operations supported by it.
- Wnode ctx waits for instantiation request from Onode. Wctx has to wait because all
    Wnodes has to reply to Onode for Onode to allocate instances of same operations
    to multiple nodes. This is ensured by the circular queue maintained in the Onode
- Onode receives operation sets from all Wctxes connected to it.
- Onode waits until all required operations to run the dataflow is found.
- Onode replies to each wctx with instance info if any.
- Wnode receives instance information, instantiates operation and Acknowledges
- Onode waits for all instances to be acknowledged
- Once all instances are acknowledged onode is ready to process inputs