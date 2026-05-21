# Day 10: System Calls — Crossing the User/Kernel Boundary

## Why This Exists

Every program eventually needs something it cannot do alone. Writing to a file, opening a socket, allocating memory beyond the stack, reading from stdin — all of these require the OS kernel to act on the program's behalf. System calls are the controlled gate through which user-space code requests kernel services.

Without this gate, every program would have direct access to every hardware device, every other process's memory, every file on the disk. Security, isolation, and stability would be impossible. The kernel's job is to be the trusted arbiter of shared resources — system calls are the only legal way to ask it for help.

Day 1 introduced syscalls as a concept. Today you go one level deeper: what happens at the CPU instruction level when you cross the boundary, why that crossing costs 200-1000 cycles, how the vDSO shortcircuits some of that cost, and how modern APIs like io_uring batch calls to amortize the overhead.

### What If This Didn't Exist?

Without the user/kernel boundary, the only alternative is to run everything in a single privilege level — which is how early MS-DOS worked. Any program could write directly to the disk controller's I/O ports, overwrite the interrupt vector table, or corrupt another program's memory simply by writing to the wrong address. A single buggy program could halt the machine. Multi-user systems, virtual machines, and process isolation are all built on top of this boundary. The hardware privilege ring model (rings 0-3 on x86) exists precisely because software-only solutions to isolation are too slow and too fragile.

### Why This Name?

The term "system call" dates to the 1960s Multics project, where the design principle was that programs should *call* the *system* rather than directly manipulate hardware. The word "call" was intentional — it was meant to feel like a procedure call, with the kernel playing the role of a library you are invoking. The key difference from a library call is the mode switch: a syscall changes the CPU's privilege level, which a normal function call cannot do. The POSIX standard (1988) formalized the set of syscalls that every Unix-compatible OS must provide, turning the interface from an implementation detail into an API contract.

### The Physics Connection

The syscall cost (200-1000 cycles) is not arbitrary — it is dominated by three physical constraints. First, saving and restoring registers is a write to L1/L2 cache (~4 cycles per write), and there are 15+ registers to save. Second, switching the stack pointer means touching a different cache line, which costs one L1 hit (~4 cycles) if warm. Third, after the Spectre/Meltdown patches (2018), many CPUs perform a full page-table isolation flush on every syscall, which invalidates TLB entries and forces the MMU to re-walk page tables on the next user-space memory access — this alone adds 100-800 cycles on modern Intel chips. The vDSO exists because the kernel engineers recognized that a few syscalls (clock_gettime, gettimeofday) are called millions of times per second and the physics of crossing the boundary every time is indefensible.

### The Mathematics Connection

Syscall batching follows the same amortization logic as any fixed-overhead operation. If each syscall costs F cycles of fixed overhead and P cycles of per-byte processing, then writing N bytes one at a time costs N * (F + P) cycles. Writing in chunks of size B costs (N/B) * F + N * P cycles. The ratio of throughput improves by a factor of B when F >> P — which is exactly the regime syscalls operate in. This is the same analysis as the "startup cost dominates" model in amortized analysis, and it directly explains why io_uring's ring buffer design can saturate NVMe drives that individual pwrite() calls cannot — the batch size B can be made as large as the ring buffer, driving the fixed overhead per byte toward zero.

### The Economics Connection

The syscall boundary is an economic trade-off between safety and performance. A fully trusted monolithic program with no boundary would run 5-20% faster on I/O-bound workloads. The price you pay for that boundary is ~1000 cycles per crossing. For a program making 1 million syscalls per second (a busy web server), that is 10^9 cycles per second dedicated purely to boundary crossing — roughly one full CPU core. The decision to pay that cost was made in the 1960s, and every subsequent OS has inherited it because the security and isolation guarantees are worth more than the CPU time. The vDSO and io_uring are the market's answer to cases where the economics tip back: when the call is safe to make without privilege (read a kernel clock register) or when the overhead can be shared across a batch.

### When Does This Break?

The syscall interface breaks down in four ways. First, **frequency**: a program calling write() on every byte pays 1000x the overhead of one that writes 4KB at a time — this is why stdio buffers output. Second, **Spectre mitigations**: on Intel CPUs with IBPB/IBRS enabled, each syscall flushes the branch predictor, adding 500-1000 extra cycles beyond the baseline. Third, **signal delivery**: a signal arriving during a syscall can interrupt it, returning EINTR, which many programs fail to handle correctly — this is a class of real bugs in production code. Fourth, **32-bit vs 64-bit ABI confusion**: mixing 32-bit and 64-bit calling conventions (int 0x80 in a 64-bit process) works but uses the 32-bit syscall table, returning different numbers and silently truncating 64-bit pointers.

### When Should You Violate This?

Use the vDSO — it is the kernel's own sanctioned shortcut. For clock_gettime() calls in hot loops, the vDSO version reads a kernel-maintained memory page directly from user space without privilege switch, at ~20 cycles instead of ~300. Use io_uring for any workload doing many small reads or writes — it amortizes syscall overhead by submitting and collecting completions in batches via shared ring buffers, with zero syscalls needed if the ring never fills. Use mmap() instead of read()/write() for large files — after the initial syscall, page faults are handled by the kernel without a full privilege switch (they go through the hardware fault handler, not the syscall dispatch table). Avoid these shortcuts in security-sensitive code where the added complexity creates more risk than the performance gain is worth.

## Theory

### The Three Entry Mechanisms

**int 0x80 (legacy 32-bit):** The original x86 Unix syscall mechanism. Triggers a software interrupt, the CPU looks up vector 0x80 in the IDT (Interrupt Descriptor Table), switches to ring 0, and jumps to the kernel's interrupt handler. Cost: ~200 cycles on modern CPUs, more on chips with full IDT-based dispatch overhead. Still works in 64-bit mode but uses the 32-bit syscall table and is considered obsolete.

**SYSENTER/SYSEXIT (Intel 32-bit fast path, Pentium II+):** Intel's attempt to speed up the int 0x80 path. Loads the kernel CS/EIP/ESP from MSRs (Model-Specific Registers) without the full IDT walk. Roughly 2x faster than int 0x80. AMD did not implement SYSENTER in early 64-bit CPUs, which created a portability mess. Linux still emits SYSENTER-compatible vDSO stubs for 32-bit processes.

**SYSCALL/SYSRET (x86_64 native):** The 64-bit standard. SYSCALL saves RIP and RFLAGS into RCX and R11 respectively, loads the kernel entry point from the LSTAR MSR, and switches CS to kernel mode — in a single instruction. No IDT lookup, no stack switch yet (that happens in the kernel entry stub). SYSRET reverses this. This is what all 64-bit Linux processes use and what `man 2` describes.

### The Syscall Table

The kernel maintains a table of function pointers indexed by syscall number. On x86_64 Linux, this table is defined in `arch/x86/entry/syscalls/syscall_64.tbl` and compiled into the kernel image. Syscall number 0 is `read`, 1 is `write`, 2 is `open`, 60 is `exit`. The numbers are part of the ABI — they never change for a given architecture, because every program compiled against glibc depends on them.

### Register Convention on x86_64

The calling convention for syscalls differs from the C calling convention (System V AMD64 ABI):

| Purpose        | Syscall register | C function register |
|----------------|------------------|---------------------|
| Syscall number | rax              | (not used)          |
| Argument 1     | rdi              | rdi                 |
| Argument 2     | rsi              | rsi                 |
| Argument 3     | rdx              | rdx                 |
| Argument 4     | r10              | rcx                 |
| Argument 5     | r8               | r8                  |
| Argument 6     | r9               | r9                  |
| Return value   | rax              | rax                 |

Note argument 4: syscalls use r10 because SYSCALL destroys rcx (saves the return RIP there). The kernel's entry stub moves r10 into rcx before calling the C handler so the handler sees a normal argument list.

### What the Kernel Does on Entry

1. **SYSCALL instruction executes:** CPU atomically saves RIP→RCX, RFLAGS→R11, loads LSTAR into RIP, switches CS privilege level to ring 0.
2. **entry_SYSCALL_64 stub:** The kernel's hand-written assembly entry point. Immediately executes `swapgs` to switch from the user GS base to the kernel GS base (which points to per-CPU kernel state including the kernel stack pointer).
3. **Stack switch:** Loads the kernel stack pointer from the per-CPU area. Each process has a dedicated kernel stack (8KB). The user RSP is saved.
4. **Register save:** Pushes all user registers onto the kernel stack in a `pt_regs` struct. This is the snapshot the kernel can modify to change return values or inject signals.
5. **Dispatch:** Looks up `sys_call_table[rax]` and calls the C handler.
6. **Return:** The kernel handler returns into the entry stub, which restores user registers, executes `swapgs` again, and executes SYSRET to restore RIP from RCX and RFLAGS from R11.

### The vDSO (Virtual Dynamic Shared Object)

The vDSO is a small shared library that the kernel maps into every process's address space at a random address (ASLR applies). It contains kernel-provided implementations of a handful of syscalls that do not require privilege — primarily `clock_gettime`, `gettimeofday`, `time`, and `getcpu`.

For `clock_gettime(CLOCK_MONOTONIC)`, the vDSO implementation reads a kernel-maintained data structure (`vvar` page) that is mapped read-only into every process. The kernel updates this structure on each timer interrupt. The vDSO reads it, applies a cotime algorithm to get nanosecond resolution, and returns — entirely in user space, at ~20-30 cycles instead of ~300.

You can see the vDSO in any process: `cat /proc/self/maps | grep vdso`.

### Syscall Cost Model

| Mechanism            | Typical cost       | Why                                         |
|----------------------|--------------------|---------------------------------------------|
| vDSO clock_gettime   | 20-30 cycles       | Pure user-space read of shared memory page  |
| vDSO gettimeofday    | 20-30 cycles       | Same mechanism                              |
| getpid (cached)      | ~30 cycles         | Kernel caches pid in user-space on Linux    |
| gettid               | ~300 cycles        | Always a real syscall (no vDSO)             |
| write (4KB)          | ~500-800 cycles    | Real syscall + kernel copy                  |
| write (1 byte)       | ~500-800 cycles    | Same overhead, almost no payload            |

### Batching Strategies

**Buffered I/O:** stdio's fwrite buffers writes in user space and flushes when the buffer fills. Reduces syscalls from N (one per byte) to N/4096 (one per 4KB page). This alone is the difference between 1MB/s and 1GB/s on sequential writes.

**sendmmsg:** A single syscall that sends multiple UDP datagrams. On high-throughput UDP (DNS servers, game servers), this can deliver 10x throughput improvement over individual sendmsg calls.

**io_uring:** The Linux kernel's answer to async I/O done right (since 5.1, 2019). Two shared ring buffers between kernel and user space — a submission queue (SQ) and a completion queue (CQ). The user fills the SQ with I/O requests, calls `io_uring_enter()` once (or zero times if the kernel thread is polling), and later drains completions from the CQ. Peak throughput: millions of IOPS from a single thread, compared to ~100K IOPS with blocking read/write.

## Practice

See `practice.py` in this directory for 5 exercises with solutions, and `syscall_tracer.py` for the syscall counter and cost demonstration.

## Checkpoint Questions

1. A program calls `write(fd, buf, 1)` one million times vs `write(fd, buf, 4096)` 244 times (total bytes the same). Both write to the same file. Assuming 600 cycles per syscall overhead and 1 cycle per byte of kernel copy, estimate the total cycle cost for each approach and the speedup ratio.

2. Why does the SYSCALL instruction save the return address into RCX rather than pushing it onto the stack? What does this imply about the first thing the kernel entry stub must do?

3. Explain why `gettid()` cannot be implemented via the vDSO while `clock_gettime(CLOCK_MONOTONIC)` can. What property of the data being read makes vDSO safe for one and not the other?

4. After the Spectre/Meltdown patches (KPTI), syscall cost increased by 100-800 cycles on some workloads. Explain the mechanism: what does KPTI change about memory mappings, and why does that interact with syscall frequency?

5. io_uring uses two ring buffers in shared memory between kernel and user space. Why is this design fundamentally lower overhead than even a single batched syscall like sendmmsg? What additional optimization becomes possible with a kernel polling thread (SQPOLL mode)?
