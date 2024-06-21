Using UNIX domain sockets instead of TCP/IP loopback for local inter-process communication (IPC) provides several security and performance advantages. Here's a detailed look at why binding to UNIX sockets can be beneficial, particularly in terms of security and efficiency:

### Security Advantages of UNIX Domain Sockets

1. **File System Permissions**:
   - UNIX domain sockets use the file system for addressing, which allows the use of traditional UNIX file permissions to control access. This means you can restrict which users or processes can communicate through the socket using standard file permissions (e.g., setting ownership and mode)【33†source】.
   - This fine-grained access control is not available with TCP/IP sockets, where any process running on the local machine that knows the port number can attempt to connect.

2. **Credential Passing**:
   - UNIX domain sockets support passing credentials between processes. This means a server can validate the identity of the connecting client process, ensuring that only authorized processes can communicate with it【33†source】.

3. **Reduced Exposure**:
   - Since UNIX domain sockets do not use the network stack, they are inherently local. This reduces the risk of exposure to network-based attacks that might exploit vulnerabilities in the TCP/IP stack or the configuration of the network interfaces.

### Performance Benefits

1. **Lower Overhead**:
   - UNIX domain sockets avoid the overhead associated with the TCP/IP stack, such as checksums, three-way handshakes, and packet routing. This results in lower latency and higher throughput for local IPC【32†source】【33†source】.

2. **Fewer Context Switches**:
   - Communication via UNIX domain sockets typically involves fewer context switches compared to TCP loopback, since the data does not need to traverse the network stack. This can lead to more efficient CPU usage and faster communication【32†source】.

### Comparison to Zero Trust Architecture

Using TCP/IP loopback still necessitates a robust security architecture like Zero Trust because the network stack is still involved, and potential vulnerabilities within it could be exploited. With Zero Trust, every connection is treated as potentially insecure, and continuous verification and strict access controls are applied. However, by using UNIX domain sockets, you leverage the operating system's built-in security mechanisms (like file permissions and credential passing) to add another layer of security, reducing the attack surface.

In summary, while TCP/IP loopback requires comprehensive security measures to mitigate network-based risks, UNIX domain sockets offer a more secure and efficient alternative for local IPC by leveraging the file system and reducing the involvement of the network stack.

For further reading, you might find the following resources useful:
- [PostgreSQL: Unix domain socket vs TCP/IP loopback](https://zaiste.net/posts/postgresql-unix-socket-tcpip-loopback/)
- [GitHub - Unix Domains Sockets vs Loopback TCP Sockets](https://github.com/nicmcd/uds_vs_tcp)
- [FreeBSD Mailing List Discussion on Unix Domain Sockets vs Internet Sockets](https://lists.freebsd.org)