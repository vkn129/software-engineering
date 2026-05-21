# 02-systems — 180-Day Curriculum

Six phases × 30 days. Same first-principles cadence as `01-dsa`: each day has a focused topic, ~1 hour of reading, and a runnable implementation.

## Phase 1 — OS Foundations (Days 1–30)

Process model, memory, concurrency primitives. The kernel as a resource arbiter.

| Day | Topic |
|-----|-------|
| 1   | What an OS Actually Does — Kernel vs User Space |
| 2   | Processes — fork(), exec(), the PCB |
| 3   | Threads — Concurrency vs Parallelism, the GIL |
| 4   | Context Switching & CPU Scheduling (FCFS, RR, MLFQ, CFS) |
| 5   | Virtual Memory & Paging |
| 6   | Memory Allocators — `malloc` from scratch |
| 7   | Heap, Stack, and Buffer Overflow Mechanics |
| 8   | File Systems — inodes, Blocks, Directories |
| 9   | Block Devices & Disk Scheduling |
| 10  | System Calls — Crossing the User/Kernel Boundary |
| 11  | Signals — Async Interrupts in User Space |
| 12  | IPC — Pipes, FIFOs, Message Queues |
| 13  | Shared Memory & mmap |
| 14  | Locks — Spinlocks, Mutexes, RW Locks |
| 15  | Semaphores & Condition Variables |
| 16  | Deadlock — Coffman Conditions, Detection, Avoidance |
| 17  | Classic Synchronization Problems |
| 18  | Lock-Free Programming — Atomics & CAS |
| 19  | Memory Models & Memory Ordering |
| 20  | Mini-Project — Build a Shell |
| 21  | ELF & Loaders — How a Binary Starts Running |
| 22  | Dynamic Linking — Symbols, PLT, GOT |
| 23  | ASLR & Position-Independent Code |
| 24  | Process Containers — cgroups & namespaces |
| 25  | Lightweight VMs — KVM, Firecracker |
| 26  | eBPF — Programmable Kernel Extension Points |
| 27  | Profiling — `perf`, Flamegraphs |
| 28  | Tracing — `strace`, `ftrace` |
| 29  | `/proc` and `/sys` — Kernel as Filesystem |
| 30  | Mini-Project — Toy Container Runtime |

## Phase 2 — OS Advanced (Days 31–60)

I/O, hardware-software interface, performance, security.

| Day | Topic |
|-----|-------|
| 31  | The Page Cache & Block Cache |
| 32  | Write-Back vs Write-Through |
| 33  | `fsync`, `fdatasync` & Crash Consistency |
| 34  | Journaling File Systems — ext4 |
| 35  | Log-Structured File Systems |
| 36  | Copy-on-Write Filesystems — btrfs, ZFS |
| 37  | Network File Systems — NFS Protocol |
| 38  | RAID — Mirroring, Striping, Parity |
| 39  | NVMe & SSD Internals — FTL, GC, Write Amplification |
| 40  | I/O Schedulers — CFQ, mq-deadline, BFQ |
| 41  | Async I/O — epoll, kqueue, io_uring |
| 42  | Zero-Copy I/O — sendfile, splice, MSG_ZEROCOPY |
| 43  | DMA & Interrupts |
| 44  | Interrupt Handlers — Top vs Bottom Halves |
| 45  | NUMA — Memory Locality on Multi-Socket Boxes |
| 46  | CPU Caches — L1/L2/L3, MESI Coherence |
| 47  | False Sharing — Cache-Line Contention |
| 48  | Branch Prediction & Speculative Execution |
| 49  | Spectre & Meltdown — Architectural Side Channels |
| 50  | SIMD — Vectorizing Hot Loops |
| 51  | GPUs vs CPUs — Throughput vs Latency |
| 52  | Real-Time Systems — Hard vs Soft Deadlines |
| 53  | Embedded OS Concepts — FreeRTOS Internals |
| 54  | Power Management — DVFS, Suspend, C-States |
| 55  | Booting — BIOS, UEFI, Bootloaders |
| 56  | Kernel Compilation & Modules |
| 57  | Capabilities & seccomp — Privilege Reduction |
| 58  | Security — SELinux, AppArmor, MAC vs DAC |
| 59  | OS Performance Tuning Lab |
| 60  | Mini-Project — Loadable Kernel Module |

## Phase 3 — Networking Foundations (Days 61–90)

Bits to bytes to sockets. Every layer that lies to you.

| Day | Topic |
|-----|-------|
| 61  | The Network Stack — From Wire to Socket |
| 62  | Ethernet — Frames, MAC, CSMA/CD |
| 63  | ARP — IP to MAC Resolution |
| 64  | IPv4 — Addressing, Subnetting, CIDR |
| 65  | IPv6 — Why It Exists, How It Differs |
| 66  | Fragmentation & Path MTU |
| 67  | ICMP — Ping, Traceroute, MTU Discovery |
| 68  | Routing Basics — Static, Default Gateway |
| 69  | Dynamic Routing — RIP, OSPF, BGP |
| 70  | NAT & Connection Tracking |
| 71  | UDP — Connectionless Best-Effort |
| 72  | TCP — Three-Way Handshake, State Machine |
| 73  | TCP Reliability — Sequence, ACK, Retransmit |
| 74  | TCP Flow Control — Receive Window |
| 75  | TCP Congestion Control — Slow Start, AIMD |
| 76  | TCP Variants — Reno, Cubic, BBR |
| 77  | TCP Tuning — Buffers, Nagle, Delayed ACK |
| 78  | Sockets — Berkeley API |
| 79  | select / poll / epoll — Multiplexing Models |
| 80  | Server Architectures — Thread-per-Conn, Reactor, Proactor |
| 81  | DNS — Hierarchy, Recursive Resolution |
| 82  | DNS Caching, TTL, Glue Records |
| 83  | HTTP/1.1 — Methods, Headers, Pipelining |
| 84  | HTTP/2 — Multiplexing, HPACK |
| 85  | HTTP/3 — QUIC, 0-RTT |
| 86  | TLS Handshake — Symmetric + Asymmetric Crypto |
| 87  | Certificate Authorities & Trust Chains |
| 88  | WebSockets — Full Duplex Over HTTP |
| 89  | gRPC & Protocol Buffers |
| 90  | Mini-Project — HTTP/1.1 Server from Scratch |

## Phase 4 — Networking Advanced (Days 91–120)

Edge, proxies, container networking, reliability patterns.

| Day | Topic |
|-----|-------|
| 91  | CDN — Edge Caching, Anycast |
| 92  | Load Balancers — L4 vs L7 |
| 93  | Reverse Proxies — Nginx, Envoy Internals |
| 94  | API Gateways |
| 95  | Service Meshes — Istio, Linkerd |
| 96  | mTLS & Zero Trust |
| 97  | VPNs — IPSec, WireGuard |
| 98  | Firewalls — netfilter, iptables, nftables |
| 99  | eBPF for Networking — XDP |
| 100 | DPDK & Kernel Bypass |
| 101 | RDMA & High-Performance Networking |
| 102 | Network Namespaces & veth Pairs |
| 103 | Container Networking — CNI, Calico, Flannel |
| 104 | SDN — Software Defined Networking |
| 105 | BGP & the Internet's Routing Plane |
| 106 | DDoS Mitigation |
| 107 | Rate Limiting — Token Bucket, Leaky Bucket |
| 108 | Circuit Breakers & Bulkheads |
| 109 | Connection Pooling |
| 110 | HTTP Caching — ETag, Last-Modified, Cache-Control |
| 111 | WebRTC — Peer-to-Peer Real-Time |
| 112 | MQTT, AMQP, Kafka Wire Protocol |
| 113 | Publish-Subscribe Patterns |
| 114 | Network Profiling — tcpdump, Wireshark |
| 115 | Latency vs Throughput Trade-offs |
| 116 | Bandwidth-Delay Product & BBR Deep Dive |
| 117 | Retry Patterns — Jitter, Exponential Backoff |
| 118 | Deadline Propagation |
| 119 | Bufferbloat — Why Your WiFi Is Slow |
| 120 | Mini-Project — Reverse Proxy with Health Checks |

## Phase 5 — Distributed Systems Foundations (Days 121–150)

Coordination under partial failure.

| Day | Topic |
|-----|-------|
| 121 | The 8 Fallacies of Distributed Computing |
| 122 | Failure Modes — Crash, Omission, Byzantine |
| 123 | The CAP Theorem |
| 124 | PACELC — Beyond CAP |
| 125 | Time — Wall, Monotonic, Logical |
| 126 | Lamport Timestamps |
| 127 | Vector Clocks |
| 128 | Hybrid Logical Clocks |
| 129 | TrueTime & Spanner |
| 130 | Consensus — The Problem Statement |
| 131 | Two-Phase Commit |
| 132 | Three-Phase Commit |
| 133 | Paxos — Single Decree |
| 134 | Multi-Paxos |
| 135 | Raft — Leader Election, Log Replication |
| 136 | ZAB — Zookeeper Atomic Broadcast |
| 137 | Byzantine Fault Tolerance — PBFT |
| 138 | Replication — Leader-Follower |
| 139 | Replication — Multi-Leader |
| 140 | Replication — Leaderless (Dynamo Style) |
| 141 | Quorums — N, R, W |
| 142 | Read Repair & Anti-Entropy |
| 143 | CRDTs — Conflict-Free Replicated Data Types |
| 144 | Eventual Consistency Models |
| 145 | Linearizability vs Sequential vs Causal |
| 146 | Sharding — Range vs Hash |
| 147 | Consistent Hashing |
| 148 | Rebalancing & Hot Shards |
| 149 | Distributed Transactions — Saga Pattern |
| 150 | Mini-Project — Raft Implementation |

## Phase 6 — Distributed Systems Advanced + Production (Days 151–180)

The systems you actually run in production.

| Day | Topic |
|-----|-------|
| 151 | Service Discovery — DNS, etcd, Consul |
| 152 | Health Checks & Failure Detection |
| 153 | SWIM Gossip Protocol |
| 154 | Hinted Handoff |
| 155 | Distributed Locks — Redlock, Chubby |
| 156 | Leases & Fencing Tokens |
| 157 | Distributed Pub-Sub — Kafka Architecture |
| 158 | Distributed Logs — Append-Only, Compaction |
| 159 | Stream Processing — Exactly-Once Semantics |
| 160 | Distributed File Systems — GFS, HDFS |
| 161 | Object Storage — S3 Internals |
| 162 | Distributed KV Stores — Dynamo, Cassandra |
| 163 | Distributed SQL — Spanner, CockroachDB |
| 164 | NewSQL vs NoSQL Trade-offs |
| 165 | Caching Strategies — Cache-Aside, Write-Through |
| 166 | Cache Invalidation |
| 167 | Hot Keys & Cache Stampedes |
| 168 | Distributed Rate Limiting |
| 169 | Distributed Tracing — OpenTelemetry |
| 170 | Logging at Scale — Structured, Centralized |
| 171 | Metrics — Counters, Gauges, Histograms |
| 172 | SLIs, SLOs, Error Budgets |
| 173 | Alerting & On-Call Discipline |
| 174 | Incident Response & Postmortems |
| 175 | Chaos Engineering |
| 176 | Feature Flags & Gradual Rollouts |
| 177 | Blue-Green vs Canary Deployments |
| 178 | Database Migrations Under Load |
| 179 | Capacity Planning & Forecasting |
| 180 | Capstone — Distributed KV Store with Raft + Sharding |
