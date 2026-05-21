# Day 2: Processes — fork(), exec(), and the Process Control Block

## Why This Exists

Your CPU has one job: execute instructions. But your laptop runs hundreds of programs simultaneously — a browser, a music player, a text editor, a dozen background daemons. How? The operating system invents a fiction called a *process*: the illusion that your program owns the entire CPU and all of memory, when in reality it is time-sharing hardware with everything else.

A process is the operating system's unit of isolation. It is not just code running — it is code running *with a protected bubble of state*: its own memory space, its own open files, its own view of the filesystem. This isolation is the foundation of everything in systems programming. When it works, a crash in your browser does not corrupt your music player. When it is violated, you have a security vulnerability.

The mechanisms that create, duplicate, and destroy processes — `fork()`, `exec()`, `wait()` — look simple but encode decades of design decisions about how isolated computation should work. Understanding them is understanding how every shell, every server, and every container runtime works at its core.

### What If This Didn't Exist?

Without processes, every program would run in the same address space, with direct access to all memory and all hardware. One buggy loop could overwrite the kernel. One malicious program could read another program's passwords. You would need to trust every line of code on your machine, including every library. This was the reality on early microcomputers (MS-DOS ran programs with no memory isolation whatsoever). The result: a single bad program could — and routinely did — crash the entire machine. Process isolation is what makes multi-user systems, the web, and cloud computing economically viable. Without it, there is no meaningful security boundary between programs.

### Why This Name?

"Process" comes from Latin *processus*, meaning "progress" or "a moving forward." In computing, John von Neumann and his contemporaries in the 1950s used it to describe a program in the act of execution — something *progressing* through computation, distinct from a static program sitting on disk. The name `fork()` is visual: one execution path splits into two, like a fork in a road. `exec()` is short for "execute" — replace the current process image with a new one. The Process Control Block name is architectural: it is the kernel's data structure that *controls* access to and accounting for the process.

### The Physics Connection

A process's memory isolation is enforced by the Memory Management Unit (MMU), a hardware circuit on the CPU die. The MMU translates virtual addresses to physical addresses using a page table. When a process accesses memory, the MMU checks the page table entries — each entry is typically 8 bytes, and a full 4-level page table for a 64-bit address space can hold millions of entries. The act of switching between processes (a context switch) requires flushing the Translation Lookaside Buffer (TLB), a cache of recent address translations, or tagging entries with an Address Space ID. Each TLB flush costs hundreds of nanoseconds because the CPU must re-walk page tables on the next dozen memory accesses. This is not an abstraction — it is a consequence of the speed-of-light limit on how fast a cache can be invalidated and refilled.

### The Mathematics Connection

`fork()` creates a process tree — a rooted directed tree where each node is a process and edges point from parent to child. The number of processes spawned by a naive recursive fork bomb doubles with each level: n levels produce 2^n processes. This exponential growth is why fork bombs are effective attacks. More usefully, process trees let you reason about resource accounting: the `wait()` system call implements a post-order traversal, collecting exit status from leaves before parents can clean up. The zombie state exists to preserve the exit status node in the tree until the parent visits it — a form of lazy deletion in a live data structure.

### The Economics Connection

Fork-then-exec versus Windows-style `CreateProcess` is an economic design trade-off. Unix `fork()` copies one process to make another, then `exec()` replaces its image. This seems wasteful — why copy if you are about to replace? Copy-on-write (COW) solves it: the kernel marks all pages read-only and shared, and only copies a page when one process writes to it. In practice, a shell that forks then immediately execs touches almost zero pages, making fork nearly free. `CreateProcess` avoids the copy entirely but requires specifying all process attributes (handle inheritance, working directory, environment) upfront in one large call. Fork is composable: each attribute can be adjusted between fork and exec using existing syscalls (`chdir`, `dup2`, `setuid`). The economic win is simplicity of the kernel interface at the cost of a conceptually stranger user-space model.

### When Does This Break?

**Fork in multi-threaded programs is dangerous.** If a multi-threaded program calls `fork()`, only the calling thread is duplicated into the child — the other threads vanish. If any of those threads held mutexes at the moment of fork, those mutexes are now locked in the child with no thread to unlock them. This causes deadlocks that are nearly impossible to debug. **Zombie accumulation:** if a parent never calls `wait()`, all its dead children remain as zombies, consuming a PID slot forever. Enough zombies exhaust the PID namespace (default max ~32768 on Linux) and prevent any new process from starting. **Fork bombs** hit the process limit (`ulimit -u`) and starve the scheduler. **OOM killer:** Linux's optimistic memory allocation means `fork()` can succeed even when physical memory is nearly exhausted, because COW defers the actual allocation. When the system finally runs out, the OOM killer assassinates a process — often not the one that caused the problem.

### When Should You Violate This?

In high-performance servers, forking per request is too expensive even with COW — the TLB flush, the PCB allocation, and the scheduler overhead add up. Modern web servers use threads or async I/O instead. In security-sensitive code, you sometimes want to `fork()` without `exec()` to run dangerous operations (parsing untrusted data, calling unsafe libraries) in an isolated child that you can kill if it behaves badly — this is the basis of Chrome's process-per-tab model and systemd's sandboxing. In Python specifically, `multiprocessing` uses fork by default on Linux but switched to `spawn` (fork+exec) on macOS after macOS 10.14 because of fork-unsafety in macOS's Objective-C runtime.

---

## Theory

### Process vs. Program

A **program** is a static artifact: a file on disk containing machine code, constants, and metadata. A **process** is a running instance of a program, with its own private memory, stack, heap, open file descriptors, CPU register state, and kernel bookkeeping. You can run ten instances of the same program simultaneously — ten processes, one program. The distinction matters because the OS manages processes, not programs.

### The Process Control Block (PCB)

The kernel keeps one PCB per process, stored in kernel memory (inaccessible to the process itself). Key fields:

- **PID**: a unique integer identifier, assigned incrementally (wraps at ~32768 by default on Linux)
- **Register state**: all CPU registers saved here during a context switch (including instruction pointer, stack pointer, general-purpose registers)
- **Page table pointer**: a physical address pointing to this process's top-level page table, loaded into the CR3 register on x86 during context switch
- **File descriptor table**: an array mapping integer FDs (0, 1, 2, ...) to kernel file objects; shared with children after `fork()` until `exec()`
- **Parent PID (PPID)**: the PID of the process that created this one; forms the process tree
- **Signal handlers, umask, working directory, resource limits**: all stored in or referenced by the PCB

### fork() Semantics and Copy-on-Write

`fork()` clones the calling process. After `fork()`:
- Both parent and child continue from the same instruction
- `fork()` returns 0 in the child, the child's PID in the parent, -1 on error
- Memory is logically copied but physically shared using COW: the MMU marks all pages read-only; the first write to any page triggers a page fault and the kernel copies that one page
- File descriptors, signal handlers, environment, working directory are inherited

### exec() Family

`exec()` replaces the current process image with a new program. The PID stays the same; the register state, memory, and code are replaced. Variants: `execl`, `execv`, `execle`, `execve`, `execvp` — differ in how arguments and environment are passed. If `exec()` succeeds, it does not return (there is no process image left to return to). If it fails, it returns -1 and the original process continues.

### wait() and waitpid()

A parent calls `wait()` or `waitpid()` to collect a child's exit status. This is mandatory: without it, dead children become **zombies** — their PCB remains in the process table, consuming a PID slot, until the parent collects the status. `waitpid(-1, ...)` waits for any child; `waitpid(pid, ...)` waits for a specific child. The `WNOHANG` flag makes it non-blocking.

### Zombies and Orphans

- **Zombie**: a process that has exited but whose parent has not yet called `wait()`. It holds no resources except its PCB entry and exit status. It is not runnable.
- **Orphan**: a process whose parent has exited. The kernel re-parents orphans to `init` (PID 1), which calls `wait()` in a loop, preventing zombie accumulation.

### The Process Tree

Every process except PID 1 (`init` or `systemd`) has a parent. This forms a tree. You can view it with `pstree`. The shell is your login session's process; every command you run is a child of the shell.

### Why Fork-then-Exec Instead of CreateProcess?

`fork()` gives you a fully configured child before the new program loads. You can close file descriptors, redirect stdin/stdout with `dup2`, change working directory, drop privileges with `setuid` — all using existing syscalls — before calling `exec()`. Windows's `CreateProcess` must accept all of this as parameters to a single complex call, making the API surface enormous. The Unix composability principle: small orthogonal syscalls combine to produce rich behavior.

---

## Practice

Work through `practice.py`. Each exercise has a TODO and a solution after `# === SOLUTIONS ===`.

Also run `process_demo.py` and study the output — especially the zombie demonstration and the reaping loop.

---

## Checkpoint Questions

1. After `fork()`, both parent and child have FD 3 open to the same file. The parent reads 10 bytes. Does the child's read position change? Why or why not? What changes after `exec()`?

2. A server forks 1000 children and never calls `wait()`. The children exit quickly. What happens to the process table? What is the visible symptom and how do you fix it?

3. Why does `fork()` return twice? Trace through what the kernel actually does: what is copied, what is shared, and how does each process know which return value it received?

4. You want to run `ls -la` as a child process and capture its output in the parent. Sketch the sequence of syscalls: which FDs do you manipulate, in which process, and when?

5. Explain why fork() in a multi-threaded process is dangerous. What specific condition causes a deadlock, and why can't the child simply unlock all mutexes after fork?
