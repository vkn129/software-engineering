# Day 3: Threads — Concurrency vs Parallelism, Race Conditions, the GIL

## Why This Exists

Your CPU has 8 cores sitting idle while your program waits for a network response. A web server should handle 10,000 concurrent connections but only has 10,000 real things to do at any given moment. A database needs to serve many clients simultaneously without corrupting data when two of them modify the same row.

Threads exist because a single sequential instruction stream cannot use all the hardware you paid for. More fundamentally, they exist because the *waiting* problem and the *parallelism* problem look similar from the outside but have completely different solutions under the hood.

The catch: shared memory makes threads dangerous. Two threads reading and writing the same variable will produce garbage results in ways that are timing-dependent, non-reproducible, and nearly impossible to debug after the fact. Understanding *why* this happens at the instruction level — not just "use a lock" — is the difference between an engineer who can reason about concurrent systems and one who sprinkles synchronization primitives and hopes for the best.

### What If This Didn't Exist?

Without threads, you get one of two bad outcomes. Option one: block on every slow operation. Your web server handles one request at a time; while it waits for the database, every other client stares at a spinner. Option two: never block — use non-blocking I/O and callbacks everywhere. This works (Node.js does it), but you lose sequential reasoning entirely; every function becomes a callback registered on a future event, and control flow becomes a graph you cannot read. Threads give you the *illusion* of sequential code while letting the OS interleave execution during blocking points. That illusion is enormously valuable for programmer comprehension.

### Why This Name?

"Thread" comes from the metaphor of a thread of execution running through your program's instructions — a single path from start to finish. A process has an address space, file descriptors, and signal handlers; a thread is just the execution state (program counter, stack, registers) that runs *within* that address space. "Concurrency" means multiple things are in progress simultaneously (they may not be literally running at the same instant). "Parallelism" means multiple things are *literally executing at the same instant* on different CPU cores. These are distinct: a single-core CPU can be concurrent (via time-slicing) but never parallel.

### Physics, Math, and Economics Connections

**Physics:** Context-switching has a real energy cost. When the OS saves and restores a thread's register state (~100–200 registers on x86-64), it flushes the CPU pipeline and likely invalidates cache lines the thread was using. Each context switch costs roughly 1–10 microseconds plus the cache refill penalty. At 10,000 threads, context-switch overhead can dominate total CPU time — which is why event loops (single-threaded concurrency via I/O multiplexing) can outperform thread-per-connection servers at high concurrency. Physics sets a hard limit: the memory controller can only serve one cache line miss at a time per core.

**Math:** The speedup from parallelism is bounded by Amdahl's Law: if fraction `s` of your program is serial (non-parallelizable), the maximum speedup with N processors is `1 / (s + (1-s)/N)`. As N → ∞, speedup → `1/s`. A program that is 10% serial can never be more than 10x faster regardless of how many cores you add. This is not a software limitation — it is a mathematical identity about dependencies.

**Economics:** Threads are cheap in memory (a thread stack is typically 1–8 MB, configurable) but expensive in coordination cost. Every shared mutable variable becomes a potential source of bugs that cost engineering hours to find. The economic optimum is often: use threads for I/O-bound work (cheap to add, large latency gain), avoid threads for CPU-bound work in Python (the GIL makes them net-negative), and reach for processes or async/await before adding more threads than you can reason about.

### When Does This Break?

**Race conditions:** Any read–modify–write operation on shared state without synchronization is a race. `x += 1` is three machine instructions (LOAD, ADD, STORE). Between any two of them, the OS can preempt your thread. Two threads doing this simultaneously will lose increments. This is not a theoretical concern — it is the default behavior.

**Deadlock:** Thread A holds Lock 1 and waits for Lock 2. Thread B holds Lock 2 and waits for Lock 1. Neither can proceed. The program hangs silently. Deadlocks require: mutual exclusion, hold-and-wait, no preemption, and circular wait. Removing *any* one of these four conditions prevents deadlock.

**Priority inversion:** A low-priority thread holds a lock needed by a high-priority thread. The high-priority thread blocks while lower-priority threads (which don't need the lock) run freely. The Mars Pathfinder spacecraft hit this in 1997 and rebooted repeatedly until engineers diagnosed it from Earth.

**The GIL:** CPython's Global Interpreter Lock means only one thread executes Python bytecode at a time. CPU-bound Python threads do not parallelize — they take turns. Adding more threads to a CPU-bound Python program makes it *slower* due to lock contention.

**False sharing:** Two threads write different variables that happen to sit on the same 64-byte cache line. Each write forces the other core to invalidate its cache copy. Performance collapses even though the threads are not touching the same *logical* data. The CPU's coherence protocol cannot distinguish cache-line granularity from variable granularity.

### When Should You Violate This?

Use threads even knowing their dangers when: (1) you have I/O-bound work in Python — the GIL is released during I/O and threads genuinely parallelize; (2) you are wrapping C extensions that release the GIL (NumPy, hashlib, most database drivers); (3) you need to keep a UI responsive while a background task runs — one thread per concern is often cleaner than event-loop callbacks. Avoid threads when: your workload is CPU-bound in Python, when your shared state is complex enough that reasoning about all interleavings is infeasible, or when you can achieve the same result with `multiprocessing` (true parallelism, no GIL) or `asyncio` (single-threaded, cooperative concurrency).

## Theory

### Thread = Lightweight Shared-Memory Process

A process owns: virtual address space, file descriptor table, signal handlers, and at least one thread. A thread owns: a program counter, a stack, and CPU register state. All threads in a process share the heap, global variables, and file descriptors. Creating a thread is ~10x cheaper than forking a process because it skips copying the address space.

### Kernel Threads vs User Threads

**Kernel threads** (1:1 model, used by Linux and macOS today): The OS schedules threads directly. Blocking a thread does not block the process. True parallelism on multi-core hardware. Cost: each thread needs a kernel stack (~4–8 KB kernel memory) and context switches require a syscall.

**User threads** (N:1 model, early Java green threads, Go goroutines are M:N): A user-space scheduler multiplexes many user threads onto one (or few) kernel threads. Context switches are cheap (no syscall). Drawback: if one user thread blocks on a syscall, all user threads on that kernel thread block too. Go solves this with a scheduler that detects blocking syscalls and moves goroutines to other kernel threads.

**M:N model:** M user threads mapped to N kernel threads. Best of both worlds in theory. Hard to implement correctly. Go's goroutine scheduler is the most successful modern example.

### The Race Condition: Read–Modify–Write

`counter += 1` in Python compiles to roughly:
```
LOAD_FAST counter    # read current value into register
LOAD_CONST 1
BINARY_ADD           # compute new value
STORE_FAST counter   # write back
```
Between LOAD and STORE, another thread can run, load the same value, and store its own incremented result. Your STORE then overwrites theirs. Both threads did `+1` but the counter only went up by 1. With 100 threads each doing 100,000 increments, you expect 10,000,000 but reliably observe far less.

### Python's GIL

CPython uses reference counting for garbage collection. Reference counts are modified on every object creation and deletion. Making every reference count update thread-safe with fine-grained locks proved too slow in practice, so Guido van Rossum added the GIL in 1992: a single mutex that a thread must hold to execute any Python bytecode. The GIL is released periodically (every 5ms by default in Python 3.2+, or between I/O calls). This means:

- CPU-bound threads take turns executing Python — no actual parallelism
- I/O-bound threads release the GIL while waiting — true concurrency
- C extensions can release the GIL manually (and well-written ones do)

Python 3.13 introduced an experimental "free-threaded" build (no GIL), but it is not yet the default.

### Memory Models and Reordering

CPUs and compilers reorder memory operations for performance. What you write as sequential code may execute out of order at the hardware level. A lock does not just provide mutual exclusion — it is also a memory barrier that prevents the CPU from moving loads or stores across the boundary. Without locks (or explicit memory barriers), one thread's writes may appear in a different order to another thread depending on CPU architecture. Python's GIL acts as a memory barrier, which is why some Python concurrent code "works" even without locks — but you should not rely on this.

## Practice

Work through `thread_demo.py` to observe race conditions and GIL behavior empirically. Run it multiple times — the race condition results vary between runs, which itself is diagnostic. Then work through `practice.py` for five structured exercises.

## Checkpoint Questions

1. Two threads each do `counter += 1` one million times on a shared counter. The final value is sometimes 1,200,000, sometimes 1,800,000, never exactly 2,000,000. Explain mechanistically (at the bytecode level) why the result is non-deterministic and always less than 2,000,000, never more.

2. You add `threading.Lock` around the increment and the counter reaches exactly 2,000,000 every time. But now the program runs 5x slower than the single-threaded version. Where is the time going, and what does this tell you about the appropriate use case for threading vs. multiprocessing?

3. You write a Python program that downloads 100 URLs using 100 threads. It completes in 0.5 seconds. You rewrite it to compute 100 SHA-256 hashes using 100 threads. It takes *longer* than the single-threaded version. Explain both results in terms of the GIL. What would you use instead for the hash computation?

4. Describe a scenario where two threads can deadlock using exactly two locks. What is the minimal code change that prevents the deadlock? What are the trade-offs of that fix?

5. A teammate says "I use `threading.local` so my threads don't share state, therefore I don't need locks." Under what conditions are they correct? Under what conditions is this dangerously wrong?
