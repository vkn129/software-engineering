# Day 4: Context Switching & CPU Scheduling

## Why This Exists

Every CPU can only execute one instruction at a time per core. But modern systems run hundreds of processes simultaneously — your browser, editor, music player, and kernel daemons all appear to "run at once." This illusion requires a mechanism to rapidly switch the CPU between processes, and a policy to decide which process runs next.

Context switching is the mechanism: save the running process's state, load the next process's state, resume. Scheduling is the policy: which process gets the CPU, for how long, and in what order. Without these two pieces, you cannot have multitasking, interactive systems, or any form of fairness between competing programs.

The decisions made here propagate upward into everything: why your terminal feels sluggish when compiling, why video calls stutter when another tab runs JavaScript, why database queries sometimes take 10x longer than expected. The scheduler is one of the most consequential pieces of software ever written.

### What If This Didn't Exist?

Without context switching, each program would run to completion before the next could start — batch processing. The IBM 360 era: submit a punch card deck, wait hours for your turn, get your printout back. Interactive computing is impossible. A single infinite loop would hang the entire machine. Preemptive multitasking, invented in the 1960s with Multics and Unix, changed the economics of computing: one machine could serve dozens of users simultaneously, collapsing hardware costs by orders of magnitude.

Without a scheduler, you have no way to prioritize: a low-priority background job would starve interactive work. The OS would have no mechanism to give more CPU to a video renderer than to a background log rotator.

### Why This Name?

"Context" here means everything the CPU needs to resume a process exactly where it left off: the program counter (where in the code we are), stack pointer, general-purpose registers, floating-point registers, CPU flags, and virtual memory mappings. "Switching" captures the act of swapping one context out for another. The term emerged in operating systems literature in the 1960s-70s. "Scheduling" is borrowed from operations research — the same mathematics that optimizes factory production lines and airline gates applies to CPU time allocation.

## Physics, Math, and Economics Connections

**Physics:** Context switch cost is bounded by memory latency. Saving ~200 registers at 4 bytes each = ~800 bytes written to RAM. At 100ns per cache line (64 bytes), a full register flush costs microseconds. TLB flush cost matters too: the TLB holds ~1000–4000 virtual-to-physical address translations. After a context switch, the new process starts with a cold TLB, causing page-table walks for every new address. On modern hardware, a context switch costs 1–10 microseconds — fast compared to disk I/O (milliseconds) but expensive compared to function calls (nanoseconds).

**Mathematics:** Scheduling is applied queueing theory. M/G/1 queues model CPU scheduling. Little's Law (L = λW) tells you that average queue length equals arrival rate times average wait time — increasing throughput requires either reducing arrival rate or reducing service time. The optimal preemptive scheduler for minimizing average response time is Shortest Remaining Time First (SRTF), provable via exchange argument. MLFQ approximates SRTF without knowing burst times in advance.

**Economics:** CPU time is a scarce resource allocated under uncertainty. Schedulers make trade-offs between throughput (total work done per second), latency (time to first result), fairness (no process starved), and response time (time from request to visible output). These goals conflict: optimizing throughput favors long batch jobs; optimizing response time favors short interactive jobs. Every scheduling algorithm implicitly encodes an economic priority ordering.

## When Does This Break?

- **Priority inversion:** A high-priority thread blocks waiting for a mutex held by a low-priority thread. A medium-priority thread preempts the low-priority holder, which never releases the mutex. The high-priority thread starves. The Mars Pathfinder mission experienced this in 1997, resetting the spacecraft repeatedly.
- **Convoy effect:** One long CPU-bound job at the head of a FCFS queue makes all short jobs behind it wait. Average wait time explodes. Common in disk I/O queues too.
- **Starvation:** In priority scheduling, low-priority jobs may never run if high-priority jobs continuously arrive. Aging (gradually increasing priority of waiting jobs) is the fix.
- **False sharing / cache trashing:** When processes are scheduled across different CPU cores, they fight over shared cache lines. Context switching between cores causes more cache pollution than switching on the same core.
- **Thundering herd:** When a blocking resource becomes available, all waiting processes are woken simultaneously — only one wins the resource, the rest do useless context switches back to sleep.
- **Short quantum pathology:** Round Robin with a very short quantum (1ms) spends more time context switching than doing real work. At extreme limits, overhead exceeds throughput.

## When Should You Violate This?

- **Cooperative scheduling (coroutines, async/await):** When you control all code and can guarantee yields happen quickly, cooperative scheduling avoids context switch overhead entirely. Python asyncio, Go goroutines (partially), and most game engines use this.
- **Real-time systems:** Preemptive priority scheduling with hard deadlines is correct — but standard Unix schedulers are wrong. Use SCHED_FIFO or SCHED_RR with explicit priorities. Sometimes "violate fairness, guarantee latency."
- **NUMA awareness:** For memory-intensive workloads, pinning processes to specific cores and not preempting them (reducing context switches) outperforms fair time-slicing. Databases like PostgreSQL benefit from process affinity.
- **Spin-wait instead of blocking:** When lock hold time is shorter than context switch cost (< ~1–5 µs), spinning beats yielding. This is why kernel spinlocks exist.

## Theory

### Context Switch Cost Components

1. **Register save/restore:** All general-purpose registers, FP/SIMD registers, program counter, stack pointer, CPU flags — ~200 registers on x86-64. Cost: ~1 µs.
2. **TLB flush:** Virtual memory translations cached in TLB become invalid for the new process. Modern hardware has ASID (Address Space Identifiers) to reduce this, but many transitions still flush. Cost: many cache misses on subsequent memory accesses.
3. **Cache pollution:** The outgoing process's working set is evicted from L1/L2 cache as the new process runs. The evicted process pays a cold-cache penalty when it resumes. This is the largest real cost for CPU-bound workloads.
4. **Kernel overhead:** Save context to PCB (Process Control Block), run scheduler, load PCB, return to userspace via `iret` or equivalent.

### Preemptive vs Cooperative Scheduling

**Cooperative:** A process runs until it voluntarily yields (via `yield()`, blocking syscall, or explicit sleep). Simple to implement, no timer interrupts needed, no mid-instruction preemption. Breaks if any process misbehaves (infinite loop = machine hang).

**Preemptive:** A hardware timer interrupt fires at fixed intervals (the scheduler "tick," typically 4ms on Linux). The interrupt handler saves context and runs the scheduler. Even if a process never yields, the OS can take back the CPU. All modern general-purpose OSes are preemptive.

### Scheduling Metrics

| Metric | Definition | Favored By |
|---|---|---|
| Throughput | Jobs completed per second | Batch workloads |
| Turnaround time | Completion - Arrival | Batch |
| Response time | First output - Arrival | Interactive |
| Waiting time | Time in ready queue | Fairness |
| Fairness | CPU share proportional to weight | Multi-user systems |

### Algorithm Taxonomy

**FCFS (First Come First Served):** Non-preemptive. Simple. Suffers convoy effect — one long job blocks all short jobs. Optimal if all jobs are equal length.

**SJF (Shortest Job First):** Non-preemptive. Minimizes average wait time over FCFS. Requires knowing burst time in advance — impossible in practice. Optimal for minimizing average turnaround among non-preemptive algorithms.

**SRTF (Shortest Remaining Time First):** Preemptive SJF. Optimal for minimizing average response time. Still requires burst time knowledge.

**Round Robin (RR):** Preemptive. Each job gets a time quantum (typically 10–100ms). After quantum expires, job goes to the back of the queue. Fair, but quantum choice matters: small quantum → high context switch overhead; large quantum → degrades to FCFS.

**MLFQ (Multi-Level Feedback Queue):** Multiple queues with different priorities and quantums. New jobs enter highest priority (shortest quantum). If a job uses its full quantum, it is demoted to a lower priority queue (assumed CPU-bound). If a job yields before the quantum expires, it stays at high priority (assumed I/O-bound, which gets better response time). Periodic priority boost prevents starvation. Approximates SRTF without needing burst time. Used in Windows, early Unix.

**Linux CFS (Completely Fair Scheduler):** Each process has a `vruntime` (virtual runtime), advanced proportionally to actual CPU time weighted by niceness. The scheduler always picks the process with the smallest `vruntime` — stored in a red-black tree for O(log n) selection. "Fairness" means all processes advance `vruntime` at the same rate, ensuring equal CPU share over time. CFS replaced the O(1) scheduler in Linux 2.6.23 (2007).

### Priority Inversion and Inheritance

When low-priority task L holds a mutex that high-priority task H needs, and medium-priority task M preempts L, H is effectively blocked by M — inversion of priority order. Fix: **priority inheritance** — while L holds a lock that H waits on, L temporarily runs at H's priority, allowing it to finish and release the lock quickly.

## Practice

Work through `scheduler_sim.py` to see all four algorithms on the same workload, with Gantt charts and metrics tables. Then work through `practice.py` for hands-on implementation exercises: SRTF, convoy effect demonstration, priority inheritance, RR quantum tuning, and CFS-style scheduler.

## Checkpoint Questions

1. A context switch costs ~5 µs and your round-robin quantum is 10ms. What percentage of CPU time is wasted on context switch overhead? At what quantum would overhead exceed 50%?

2. You have 1 job with burst 100ms and 9 jobs with burst 1ms, all arriving at time 0. Calculate average turnaround time under FCFS (long job first) vs SJF. What is the ratio?

3. Explain why MLFQ demotes a job that uses its full quantum but keeps a job that yields early at high priority. What assumption does this encode about job behavior, and when is that assumption wrong?

4. In Linux CFS, two processes have been running for 10 seconds. Process A has vruntime 9.8s (niceness 0) and Process B has vruntime 8.2s (niceness 0). Which runs next, and by approximately how much wall-clock time before the scheduler reconsiders?

5. The Mars Pathfinder priority inversion reset the spacecraft repeatedly. Describe the exact sequence of events (three processes, one mutex) that caused the inversion, and explain how priority inheritance resolves each step.
