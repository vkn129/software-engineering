# Day 1: What an OS Actually Does — Kernel vs User Space

## Why This Exists

Every program you write runs in a sandbox. When you call `open("file.txt")`, you are not directly instructing the disk controller — you are asking the kernel to do it for you. This indirection is not bureaucracy; it is the foundational safety guarantee that lets thousands of programs run on the same machine without destroying each other. The operating system is the trust boundary between "code written by random people" and "hardware that costs millions of lives to get right."

The kernel/user-space split is the most important architectural decision in systems software. Get it wrong and one buggy program can corrupt kernel memory, crash every other process, and brick the device. Get it right and you can run untrusted JavaScript in a browser tab 2 centimeters from your banking app and they never touch each other. Every OS concept you will ever learn — processes, threads, virtual memory, file descriptors, signals — is a consequence of this single design decision.

## What If This Didn't Exist?

Early systems like MS-DOS ran entirely in what we now call "kernel mode." Any program could write to any memory address, talk directly to hardware, and overwrite the OS itself. A buffer overflow in a game could wipe the bootloader. A busy-wait loop in one program froze the entire machine. There was no isolation, no fairness, no safety. MS-DOS could run exactly one program at a time, and that program had godlike power over the hardware. The kernel/user split was invented precisely because this model collapsed the moment you wanted two programs to run simultaneously, or wanted to trust code you did not write.

## Why This Name?

"Kernel" comes from the nut inside a shell — the protected core. Dijkstra used the term in the 1960s at Eindhoven to describe the small, privileged nucleus that everything else depended on. "User space" (sometimes "userland") is simply everything that runs outside the kernel — the applications, libraries, and shells that actual users interact with. The division is older than Linux; Multics (1969) had protection rings, Unix (1971) collapsed them to two levels (privileged/unprivileged), and the x86 architecture generalized this to four rings (0–3) in 1985, though most OSes only use rings 0 and 3.

## The Physics Connection

The kernel/user split is enforced by hardware, not software. The x86 CPU has a 2-bit field in the CS (code segment) register called the CPL (Current Privilege Level). The CPU checks this on every memory access and every privileged instruction. When CPL=0 (ring 0, kernel), the CPU allows writes to page tables, I/O port instructions, and changes to the interrupt descriptor table. When CPL=3 (ring 3, user space), these instructions trigger a General Protection Fault — not caught by the OS, thrown by transistors. This means the isolation costs one comparison per sensitive operation, paid in nanoseconds at the silicon level. You cannot software-patch your way around it; the enforcement lives in the hardware logic gates.

## The Mathematics Connection

The dual-mode design is a formal partition. Let S be the set of all machine instructions. The kernel executes on the full set S. User processes execute on a strict subset U ⊂ S. The boundary is crossed only through a controlled gate — the system call — which the kernel defines. This is equivalent to a capability model in type theory: user processes hold unforgeable tokens (file descriptors, memory mappings) that the kernel grants and can revoke. Any attempt to forge a token (e.g., forge a page table entry) is structurally impossible because the instructions that write page tables are outside U. The security proof is: no program in U can violate kernel invariants because it cannot execute the instructions that modify kernel state.

## The Economics Connection

The kernel/user split imposes a real performance tax: every syscall requires a mode switch (~100–300 ns on modern x86), a TLB flush on some architectures, and a context save/restore. This is why high-performance systems minimize syscalls: io_uring batches I/O requests to amortize the crossing cost, mmap avoids read/write syscalls by mapping files into user address space, and vDSO (virtual dynamic shared object) moves read-only kernel data (like `gettimeofday`) into user space to eliminate the crossing entirely. The economics are clear: kernel-mode code is globally trusted and globally shared, which makes it expensive to update and impossible to customize per-tenant. User-space code is cheap to ship, cheap to crash, and cheap to replace — the architectural split directly enables the software market.

## When Does This Break?

The kernel/user boundary breaks in four known ways. First, speculative execution vulnerabilities (Spectre, Meltdown) let user-space code read kernel memory via CPU branch prediction side channels — the hardware enforcement was bypassed by exploiting the CPU's performance optimization. Second, kernel drivers run in ring 0 but are written by third parties; a buggy GPU driver can panic the kernel and take every process with it. Third, the boundary is irrelevant against physical access: DMA attacks from a malicious Thunderbolt device can write to kernel memory regardless of privilege levels. Fourth, the overhead becomes a bottleneck in syscall-heavy workloads — Redis, Nginx, and memcached have all been rewritten or patched specifically to reduce syscall frequency because the crossing cost was measurable in their latency distributions.

## When Should You Violate This?

You bypass the kernel when its overhead is unacceptable and you control the environment. DPDK (Data Plane Development Kit) maps NIC registers directly into user space to bypass the kernel networking stack entirely — at 100Gbps, the kernel interrupt model cannot keep up. SPDK does the same for NVMe SSDs. Real-time systems (medical devices, avionics) sometimes run in kernel mode or on a bare-metal RTOS to eliminate scheduler jitter. eBPF lets you run verified bytecode inside the kernel, trading the safety of user space for the performance of kernel execution. The rule: violate the boundary only when you have profiled the crossing cost, understand the failure modes you are accepting, and have a plan for what happens when your privileged code crashes.

## Theory

### Privilege Rings

x86 defines four privilege rings (0–3). Ring 0 is the kernel: it can execute any instruction, access any memory, and talk to hardware directly. Ring 3 is user space: it can execute arithmetic, call functions, and make syscalls. Rings 1 and 2 exist but modern OSes do not use them (originally intended for device drivers and OS services). Linux and Windows use only rings 0 and 3.

### The Dual-Mode Bit

The CPU tracks the current privilege level in the CS register's low 2 bits (CPL). On every privileged instruction, the CPU checks CPL. If CPL != 0, it generates a General Protection Fault (#GP), which the kernel catches via the interrupt descriptor table. The user program never sees the fault directly — it receives a signal (SIGSEGV) if the kernel decides to terminate it. The dual-mode bit is the hardware anchor for all OS security.

### Syscall Trap Mechanics

On x86_64 Linux, user space requests kernel services via the `syscall` instruction (older kernels used `int 0x80`). The sequence:
1. User code loads syscall number into `rax`, arguments into `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`.
2. `syscall` instruction atomically: saves `rip` and `rflags` to kernel-defined MSRs, switches CPL to 0, jumps to the kernel entry point defined in the `LSTAR` MSR.
3. Kernel saves remaining registers, dispatches via `sys_call_table[rax]`, executes the requested service.
4. `sysret` restores registers, switches CPL back to 3, returns to user code.

The total round-trip on modern hardware is ~100–300 ns — cheap but not free. Each crossing saves/restores ~100 bytes of register state.

### What the Kernel Owns

- **Page tables**: The kernel maps physical memory to virtual addresses. User processes see only their own mapping; they cannot read another process's pages.
- **Device drivers**: All hardware interaction (disk, NIC, keyboard) goes through kernel drivers. User space sends commands via syscalls or ioctl.
- **The scheduler**: The kernel decides which process runs on which CPU core and for how long (time quantum). User code cannot prevent preemption.
- **The interrupt descriptor table (IDT)**: Hardware interrupts (timers, NIC, keyboard) are delivered to kernel handlers, not user code. The kernel translates them to signals when user space needs to know.

### The MMU (Memory Management Unit)

The MMU is the hardware that enforces virtual memory. Every memory access from user space goes through the MMU, which translates virtual addresses to physical addresses using page tables that only the kernel can write. If a user process accesses a virtual address not in its page table, the MMU fires a page fault (#PF). The kernel's page fault handler either maps the page (e.g., for demand paging or mmap) or delivers SIGSEGV to the process. The MMU is what makes "each process thinks it owns all of memory" work — it is the hardware that makes the lie consistent.

## Practice

Work through `practice.py`. The exercises cover identifying syscalls vs library calls, measuring mode-switch overhead, observing `fork` at the kernel boundary, trapping signals, and reading `/proc/self/status`. Also run `syscall_demo.py` for a narrated demonstration of syscall mechanics.

## Checkpoint Questions

1. A user process calls `malloc(1024)`. Is this a syscall? Under what conditions does it *become* one, and which syscall is it?

2. Explain why a process cannot simply write a 0 into the CPL field of the CS register to escalate its own privilege. What hardware mechanism prevents this?

3. `int 0x80` and `syscall` both cross the user/kernel boundary. What is the architectural difference between them, and why did x86_64 introduce `syscall` if `int 0x80` already worked?

4. Two processes map the same file with `mmap`. They have different virtual addresses for the same physical pages. Who manages this aliasing, and what happens if one process writes to its mapping?

5. A syscall returns -1 and sets `errno` to `EPERM`. Where is `errno` actually stored, and why is it process-local rather than a global kernel variable?
