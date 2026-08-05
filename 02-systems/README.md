# 02-systems: Systems Engineering from First Principles

A parallel curriculum to `01-dsa/`. Where DSA teaches **how to compute**, this
track teaches **what the machine is actually doing while it computes** —
processes, threads, memory, I/O, networks, distributed coordination.

## Why This Exists

Most engineers learn systems through framework abstractions: "spin up a
container," "scale horizontally," "use a queue." That works until production
breaks at 3 AM and the abstraction leaks. Then you need to know:

- Why did the process get OOM-killed instead of paging?
- Why is the load average 200 with 4% CPU usage?
- Why does TCP behave fine in dev and collapse under bursty traffic?
- Why does Raft tolerate `f` failures with `2f+1` nodes — and what happens at `f+1`?

This curriculum builds those answers from first principles — kernel
data structures, syscall boundaries, network packets, consensus invariants —
by implementing the relevant pieces from scratch in Python or C.

## Curriculum (8 Weeks)

| Week | Theme | Topics | Capstone |
|------|-------|--------|----------|
| 1 | **Process Fundamentals** | PCB, fork/exec, threads vs procs, scheduling, context switches, IPC | Tiny process supervisor |
| 2 | **Threading & Synchronization** | Race conditions, mutexes, semaphores, condition vars, deadlock, lock-free | Bounded-buffer producer/consumer |
| 3 | **Memory** | Virtual memory, paging, TLB, allocators (bump, free-list, slab), mmap | Toy malloc + leak detector |
| 4 | **I/O & Syscalls** | Blocking vs non-blocking, select/poll/epoll, kqueue, io_uring, zero-copy | Async TCP echo server |
| 5 | **Networking Foundations** | OSI layers, Ethernet/IP, ARP, routing, NAT, DNS, sockets | DNS resolver from scratch |
| 6 | **TCP & HTTP** | 3-way handshake, congestion control, head-of-line blocking, HTTP/1.1 → HTTP/2 → HTTP/3 | HTTP/1.1 server with keep-alive |
| 7 | **Distributed Systems Intro** | Clocks (Lamport, vector), failure detectors, gossip, CAP, sharding | Gossip-based membership |
| 8 | **Consensus & Replication** | Quorums, two-phase commit, Paxos, Raft, log replication, linearizability | Toy Raft (leader election + log) |

Each week has 5 daily lessons + 1 capstone day. Each day folder contains:

- `README.md` — first-principles explanation, failure modes, real-world hooks, checkpoint questions
- `<topic>.py` or `<topic>.c` — from-scratch implementation
- `practice.py` — 5-6 exercises with `_sol_*` references and a `run_tests()` runner

## Tech Stack

- **Python (stdlib only)** — high-level demonstrations, schedulers, simulators, network protocols. `os`, `threading`, `multiprocessing`, `socket`, `select`, `signal`, `ctypes`.
- **C (when kernel-adjacent)** — context-switch microbenchmarks, raw syscall wrappers, allocator internals. `gcc -Wall -Wextra`.
- **No frameworks.** No `asyncio` until we've built `select` loops by hand. No `requests` until we've parsed HTTP off a raw socket.

## Prerequisites

- DSA Phase 1-3 (arrays, hashing, linked structures, trees, recursion). Phase 4-5 helpful (graphs, DP) for distributed systems weeks.
- Comfort on a Unix shell (`ps`, `top`, `strace`/`dtruss`, `lsof`, `netstat`/`ss`).
- A C toolchain (`gcc` or `clang`) for weeks 1, 3, 4.

## Failure-First Pedagogy

Every topic answers three questions:

1. **What problem does this solve?** (Why was it invented?)
2. **How does it fail?** (Zombies, deadlock, thrashing, head-of-line blocking, split-brain.)
3. **What does it cost?** (Time, memory, syscalls, network round-trips.)

Real systems cited throughout: Linux kernel (`task_struct`, CFS, epoll, slab),
macOS XNU (Mach ports, kqueue), BSD (sockets, ufs), etcd/Consul (Raft), Redis
(single-threaded event loop), nginx (worker pool + epoll).

## How To Work Through It

```bash
cd 02-systems/week-01/day-01
cat README.md           # read the why
python process_basics.py   # run the demo
python practice.py      # implement the TODOs, hit PASS
```

When `practice.py` prints `All tests passed!`, move on. If a checkpoint
question stumps you, that's where to dig — not where to skip.
