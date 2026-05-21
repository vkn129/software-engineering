# Day 10: System Calls — Crossing the User/Kernel Boundary

## Why This Exists

Day 1 introduced syscalls as the gateway to the kernel. Today you go down to the metal: which CPU instruction fires, what happens to your registers, why crossing the boundary costs 200-1000 cycles, and how the kernel engineers partially escaped that cost with the vDSO. Understanding this shapes every decision about buffering, batching, and async I/O.

### What If This Didn't Exist?

Without a privileged boundary every process could overwrite kernel memory, steal another process's file descriptors, or reprogram the disk controller directly. The x86 ring model — ring 0 (kernel) vs ring 3 (user) — is the hardware guarantee that makes multi-tenant OSes possible. Syscalls are the only legal crossing point.

### The Physics Connection

The 200-1000 cycle cost is physics. Saving 15+ registers costs ~4 cycles each (L1 write). Switching the stack pointer touches a new cache line. After Spectre/Meltdown patches (KPTI), many CPUs flush the TLB on every kernel entry, forcing the MMU to re-walk page tables on the next user-space access — this alone adds 100-800 cycles on Intel. The vDSO exists because `clock_gettime` is called millions of times per second and that cost is indefensible.

### The Mathematics Connection

Batching amortizes fixed overhead. If each syscall costs F cycles fixed + P cycles per byte, writing N bytes one at a time costs N*(F+P). Writing in B-byte chunks costs (N/B)*F + N*P. Throughput improves by ~B when F >> P — the exact regime of real I/O. This explains why io_uring's ring buffer can saturate NVMe drives that per-call write() cannot.

### The Economics Connection

A busy web server making 10^6 syscalls/second burns 10^9 cycles/second purely on boundary crossing — roughly one full CPU core. The isolation guarantee is worth that price for most workloads. vDSO and io_uring are targeted escapes for the cases where economics tip back.

## Theory

### The Three Entry Mechanisms

**int 0x80 (legacy 32-bit):** Triggers a software interrupt; CPU walks the IDT, switches to ring 0. ~200 cycles. Still works in 64-bit mode but uses the 32-bit syscall table — a subtle trap for code mixing ABIs.

**SYSENTER/SYSEXIT (Intel 32-bit fast path):** Loads kernel CS/EIP/ESP from MSRs instead of walking the IDT. ~2x faster than int 0x80. AMD's early 64-bit chips skipped it, creating portability headaches. Still used by Linux's 32-bit vDSO stubs.

**SYSCALL/SYSRET (x86_64 native):** The modern standard. SYSCALL atomically saves RIP→RCX, RFLAGS→R11, loads the kernel entry point from the LSTAR MSR, and switches CS to ring 0 — in a single instruction, no IDT walk. SYSRET reverses it. All 64-bit Linux processes use this path.

### The Syscall Table

The kernel keeps an array of function pointers indexed by number (`arch/x86/entry/syscalls/syscall_64.tbl`). Number 0 = `read`, 1 = `write`, 2 = `open`, 60 = `exit`. These numbers are frozen ABI — every glibc-linked binary depends on them. The syscall number goes in **rax** before executing SYSCALL.

### Argument Passing Registers (x86_64)

| Purpose        | Syscall | C ABI  | Why they differ                        |
|----------------|---------|--------|----------------------------------------|
| syscall number | rax     | —      | —                                      |
| arg 1          | rdi     | rdi    | same                                   |
| arg 2          | rsi     | rsi    | same                                   |
| arg 3          | rdx     | rdx    | same                                   |
| arg 4          | **r10** | rcx    | SYSCALL destroys rcx (stores RIP there)|
| arg 5          | r8      | r8     | same                                   |
| arg 6          | r9      | r9     | same                                   |
| return value   | rax     | rax    | same                                   |

### What the Kernel Does on Entry

1. **SYSCALL fires:** CPU saves RIP→RCX, RFLAGS→R11, loads LSTAR→RIP, CS→ring 0.
2. **swapgs:** Swaps GS base from user value to kernel value (per-CPU area pointer).
3. **Stack switch:** Loads kernel stack from per-CPU area; saves user RSP.
4. **Register save:** Pushes all user registers into a `pt_regs` struct on the kernel stack.
5. **Dispatch:** `sys_call_table[rax]` called; kernel C handler runs.
6. **Return:** Restores registers, swapgs, SYSRET restores RIP from RCX and RFLAGS from R11.

### The vDSO (Virtual Dynamic Shared Object)

The kernel maps a small shared library into every process at a randomized address. It contains user-space implementations of syscalls that need no privilege — `clock_gettime`, `gettimeofday`, `time`, `getcpu`. For `clock_gettime(CLOCK_MONOTONIC)` the vDSO reads a kernel-maintained `vvar` page (mapped read-only into every process), applies a cotime formula, and returns — entirely in user space at ~20-30 cycles vs ~300 for a real syscall. Run `grep vdso /proc/self/maps` to see it.

### Syscall Cost Model

| Call                        | Typical cost    | Reason                                 |
|-----------------------------|-----------------|----------------------------------------|
| vDSO clock_gettime          | 20-30 cycles    | User-space read of shared memory page  |
| getpid (kernel-cached)      | ~30 cycles      | Cached in user-space on modern Linux   |
| gettid                      | ~300 cycles     | Always a real syscall, no vDSO         |
| write(fd, buf, 4096)        | 500-800 cycles  | Real syscall + kernel copy             |
| write(fd, buf, 1)           | 500-800 cycles  | Same overhead, nearly zero payload     |

### Batching Strategies

**Buffered I/O:** stdio buffers writes in user space, flushes at 4-8KB. Reduces syscalls from N to N/4096. The difference between 1 MB/s and 1 GB/s on sequential writes is almost entirely this.

**sendmmsg:** One syscall sends multiple UDP datagrams. 10x improvement on DNS/game-server UDP workloads.

**io_uring (Linux 5.1+):** Two shared ring buffers (submission queue + completion queue) between user and kernel. Fill the SQ, call `io_uring_enter()` once (or never in SQPOLL mode), drain completions later. Millions of IOPS from one thread vs ~100K with blocking write().

## Practice

See `practice.py` — 5 TODO exercises with solutions covering timing, `os.times()` user/kernel split, print overhead, syscall-bound vs CPU-bound benchmarks, and a buffered write wrapper. See `syscall_tracer.py` for the live measurement demo.

## Checkpoint Questions

1. A program calls `write(fd, buf, 1)` one million times vs `write(fd, buf, 4096)` 244 times. At 600 cycles fixed overhead and 1 cycle/byte, calculate total cycles for each and the speedup ratio.

2. Why does SYSCALL save the return address into RCX rather than the stack? What must the kernel entry stub do immediately because of this?

3. Why can `clock_gettime(CLOCK_MONOTONIC)` be implemented in the vDSO but `gettid()` cannot? What property of the data matters?

4. KPTI (Meltdown fix) added 100-800 cycles to syscalls on Intel. Explain the mechanism: what does KPTI change about page tables, and why does that interact with syscall frequency?

5. io_uring uses shared ring buffers rather than a batched syscall like sendmmsg. Why is this fundamentally lower overhead? What does SQPOLL mode add on top?
