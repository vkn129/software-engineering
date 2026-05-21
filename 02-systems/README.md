# 02 — Systems

A first-principles tour of how a computer actually runs your code, talks to other computers, and coordinates with them at scale. Each day is one focused topic with a runnable implementation.

## Path Structure

### Phase 1 — Operating Systems (Days 1–10)
What the kernel does for you, and what it forces you to do yourself.

| Day | Topic |
|-----|-------|
| 01  | What an OS Actually Does — Kernel vs User Space |
| 02  | Processes — `fork()`, `exec()`, PCBs |
| 03  | Threads — Concurrency vs Parallelism |
| 04  | Context Switching & CPU Scheduling |
| 05  | Virtual Memory & Paging |
| 06  | Memory Allocators — `malloc` from scratch |
| 07  | File Systems — inodes, Blocks, Journaling |
| 08  | System Calls — The User/Kernel Boundary |
| 09  | Signals & IPC (pipes, shared memory) |
| 10  | Mini-Project — Build a Shell |

### Phase 2 — Networking (Days 11–20)
Bits on a wire to bytes in a socket — every layer that's lying to you.

| Day | Topic |
|-----|-------|
| 11  | TCP/IP — The Stack from Wire to Socket |
| 12  | Ethernet & ARP — Layer 2 Reality |
| 13  | IP Routing — How Packets Find Their Way |
| 14  | TCP Deep Dive — Handshakes, Congestion Control |
| 15  | UDP — When Reliability Isn't Worth It |
| 16  | DNS — The World's Distributed Database |
| 17  | HTTP/1.1 → HTTP/2 → HTTP/3 |
| 18  | TLS — Encryption & Trust |
| 19  | Sockets — Berkeley API from Scratch |
| 20  | Mini-Project — HTTP Server from Scratch |

### Phase 3 — Distributed Systems (Days 21–30)
Coordination under partial failure — the only honest model of scale.

| Day | Topic |
|-----|-------|
| 21  | CAP Theorem & PACELC |
| 22  | Consensus — Paxos & Raft |
| 23  | Replication — Leader-Follower, Multi-Leader, Leaderless |
| 24  | Sharding & Partitioning |
| 25  | Distributed Locks & Leases |
| 26  | Vector Clocks & Logical Time |
| 27  | Gossip Protocols |
| 28  | Service Discovery & Load Balancing |
| 29  | Idempotency, Retries, Backoff |
| 30  | Mini-Project — Distributed KV Store |

## Conventions

- Each day has: `README.md` (theory + checkpoint questions), one implementation file, one `practice.py`/`practice.c` with exercises.
- Implementations prefer the standard library; C for OS-level work, Python/Go for distributed-systems sketches.
- Code comments explain *why*, not *what*.
- Every README ends with checkpoint questions you should be able to answer cold.
