Subnode                          |       Primary Node
------------------------------------------------------------------------------
- Starts and waits               | - Accept connection request from sn and
for connection from primary node |   replies with its id

- Records id of pn, sends back   | - Iterates through operations and assigns
names of operation supported     | token number for operations which are in the dataflow
                                 |
- Accepts operation token        | - Waits till all operations required by the dataflow
                                 | is registered
- TODO Instantiates operations   |
which were assigned a token      |
                                 |
                                 |
                                 |
                                 |
                                 |
                                 |
                                 |
                                 |
                                 |
