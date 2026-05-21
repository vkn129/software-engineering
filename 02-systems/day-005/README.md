# Day 5: Virtual Memory & Paging — Why Your Program Thinks It Has All The RAM

## Why This Exists

Your program believes it owns 4 GB (or 256 TB on 64-bit) of contiguous memory starting at address 0. This is a lie, and it is one of the best lies in computer science. The CPU and OS collaborate to give every process the illusion of its own private address space — no matter how many other processes are running, no matter how much physical RAM is actually installed.

Without this illusion, every program would need to know exactly where other programs were loaded. Linking would require runtime coordination. A buggy process could corrupt another's memory. A process needing 2 GB could not run on a machine with 2 × 1 GB RAM banks. You would manually manage which program gets which physical addresses, and one mistake would crash the entire system.

Virtual memory solves four distinct problems at once: isolation (no process can touch another's memory), over-commitment (sum of all process allocations can exceed physical RAM), simplicity (every process starts at address 0 and does not know about others), and efficiency (only load pages a process actually touches).

### What If This Didn't Exist?

Early systems like MS-DOS ran a single program at a time with direct physical addresses. Multiple programs required swapping the entire program in and out. IBM's OS/360 used "real storage" where programmers specified physical load addresses — shipping a program meant specifying a base address and hoping nothing else was loaded there. The coordination cost was enormous. Multitasking without virtual memory requires hardware segment registers (as in early 8086 protected mode), which provide isolation but not the illusion of full address space. You are always aware of physical constraints. Programs cannot be position-independent by default; relocation tables add complexity. Security isolation requires trust in every program not to write to arbitrary physical addresses — which is untenable once you have multiple users.

### Why This Name?

"Virtual" because the addresses are not real — they do not correspond to physical memory locations. The word was coined by Fritz-Rudolf Güntsch in his 1957 dissertation at TU Berlin, describing a memory hierarchy where the machine appeared to have more fast memory than it physically had. The Atlas Computer at Manchester (1962) implemented the first full virtual memory system, calling the technique "one-level storage." The "page" metaphor comes from books: memory is divided into fixed-size chunks (pages) just as a book is divided into pages, and you can flip to any page without carrying the whole book in your head.

## Physics / Math / Economics Connections

**Physics:** RAM is SRAM or DRAM — capacitors that leak charge. DRAM refresh cycles (every ~64ms) are why memory has latency. A page fault that hits disk spans ~10ms, while a TLB hit spans ~1ns. That is a 10^7 difference, directly from the physics of magnetic platters (seek + rotation) vs electron flow in silicon. Huge pages (2 MB vs 4 KB) exist because the TLB is a small SRAM structure (typically 64–1024 entries) and the silicon area for more TLB entries competes with silicon area for cache or execution units.

**Math:** A 32-bit address space has 2^32 = 4 GB of virtual addresses. With 4 KB pages (2^12 bytes), there are 2^20 = 1,048,576 pages. A single-level page table storing a 4-byte entry per page costs exactly 4 MB — per process. On a 64-bit system with 48-bit addresses: 2^48 / 2^12 = 2^36 entries × 8 bytes = 512 GB just for the page table. Multi-level tables solve this because most of that space is unmapped; a 4-level table only allocates nodes for regions that are actually used.

**Economics:** Physical RAM costs roughly $5–$10 per GB. Disk costs $0.02 per GB. Virtual memory exploits this 500x price difference by keeping frequently used pages in RAM and spilling cold pages to disk. The working set model (Denning, 1968) formalizes this: a process needs only its "working set" of recently accessed pages in RAM; the OS profits by lending unused frames to other processes. Cloud providers oversell RAM just as airlines oversell seats — virtual memory (and page compression, e.g., zswap) is how they avoid crashing when the oversubscription bet is lost.

## When Does This Break?

**Thrashing** is the catastrophic failure mode: the system spends more time handling page faults than running useful code. It occurs when the sum of working sets exceeds physical RAM. CPU utilization collapses while disk I/O saturates. Adding more processes makes it worse, not better.

**TLB shootdowns** are a scalability bottleneck on multicore: when one core modifies a page table entry (e.g., munmap), it must send inter-processor interrupts (IPIs) to every other core to flush their TLBs. On a 128-core machine, one munmap can pause 127 cores. Huge pages reduce TLB pressure but make shootdowns more expensive per entry.

**Swap exhaustion** causes the OOM killer to shoot processes. On systems without swap, any memory overcommit that cannot be reclaimed crashes processes immediately.

**Belady's anomaly:** FIFO page replacement can produce *more* page faults with *more* physical frames — more resources makes things worse. This violates intuition and is why LRU (which does not exhibit Belady's anomaly) is preferred.

**NUMA effects:** On multi-socket machines, accessing memory attached to the remote socket costs ~2x the latency of local memory. Virtual memory hides which physical socket a page lives on, so code that is correct can have wildly variable performance depending on where the OS placed the physical pages.

## When Should You Violate This?

**mlock():** Lock pages into physical RAM, preventing them from being paged out. Required for real-time systems (audio, control systems), cryptographic key storage (you cannot let a secret key be written to swap), and latency-sensitive trading systems.

**Huge pages (2 MB / 1 GB):** Bypass the standard 4 KB page size to reduce TLB misses for large working sets. Databases (PostgreSQL, Oracle), JVMs, and HPC codes use `madvise(MADV_HUGEPAGE)` or explicit hugeTLBfs mounts. The trade-off is increased internal fragmentation and more expensive page faults.

**MAP_FIXED / direct physical mapping:** Embedded systems and drivers sometimes need to map a specific physical address (memory-mapped I/O register) into virtual space. This requires bypassing normal allocation entirely.

**Disabling swap:** Redis and latency-sensitive databases (`vm.swappiness=0` or `swapoff`) prefer an OOM kill over the latency spike of swapping a hot page.

## Theory

### Virtual vs Physical Addresses

Every instruction in your program uses *virtual addresses*. The CPU's Memory Management Unit (MMU) translates them to *physical addresses* before reaching RAM. Translation is per-process: VA 0x1000 in process A maps to physical frame 42, while VA 0x1000 in process B maps to physical frame 87. The mapping is defined by the page table, which the OS writes and the hardware reads.

### Page Tables (Multi-Level, Why)

A *page* is the unit of mapping — typically 4 KB. A *frame* is a physical page of the same size. The page table maps virtual page numbers (VPN) to physical frame numbers (PFN).

A single-level page table for a 32-bit address space needs 2^20 entries × 4 bytes = 4 MB per process. For 64-bit spaces, a flat table is impossible (terabytes). Multi-level tables solve this: x86-64 uses 4 levels (PGD → PUD → PMD → PTE). Each level is a 4 KB table of 512 8-byte entries. A process using only 10 MB of virtual space needs only a handful of these nodes, not a full tree. Only the paths that lead to mapped pages are allocated.

### TLB and TLB Shootdowns

The Translation Lookaside Buffer (TLB) is a small hardware cache (64–1024 entries) of recent VA→PA translations, sitting inside the MMU. A TLB hit costs ~1 clock cycle. A TLB miss requires a hardware page table walk (~10–100 cycles). A page fault (page not in RAM) requires OS involvement (~100,000+ cycles).

TLB shootdowns occur when a mapping is removed or changed. The OS must IPI all cores running the affected process and force them to invalidate their TLB entries (`INVLPG` instruction). On highly parallel workloads, this serialization is a significant bottleneck.

### Page Faults (Minor vs Major)

A *minor fault* means the page is already in physical RAM (e.g., a freshly allocated but not yet mapped page, or a shared page from another process). The OS just updates the page table — no I/O. Cost: microseconds.

A *major fault* means the page must be read from disk (swap or a memory-mapped file). Cost: milliseconds. Major faults are visible as I/O wait; too many is a sign of insufficient RAM.

### Demand Paging and Copy-on-Write

*Demand paging:* Pages are not loaded when a process starts. They are loaded on first access (the fault that would otherwise crash instead causes the OS to allocate a frame, load the page, and retry the instruction). This makes process startup fast and avoids loading code that is never executed.

*Copy-on-write (COW):* When a process forks, the child initially shares all physical frames with the parent — both map the same physical frames read-only. On the first write to a shared page, the CPU raises a protection fault. The OS copies the frame, maps the copy into the writing process's address space as writable, and retries the instruction. The other process still sees the original. This makes `fork()` almost free.

### Page Replacement: LRU, Clock, Working Set

When a fault occurs and all frames are full, one must be evicted. Optimal (Belady's OPT) evicts the page that will not be used for the longest time — clairvoyant and impossible to implement. It is the theoretical best to compare against.

**FIFO:** Evict the oldest-loaded page. Simple but ignores access frequency. Suffers Belady's anomaly.

**LRU:** Evict the least recently used page. Excellent empirically (exploits temporal locality). True LRU requires tracking access order on every memory access — too expensive in hardware. Real systems approximate it.

**Clock (Second-Chance):** A circular list of frames, each with a "recently used" bit. The clock hand sweeps; if the bit is set, clear it and advance; if not, evict that frame. Approximates LRU with O(1) overhead. Used in Linux (via the active/inactive list variant).

**Working Set:** Track the set of pages accessed in the last T time units. Evict pages outside the working set. Adapts to changing access patterns; theoretical basis for understanding thrashing.

### Thrashing

When physical frames < sum of working sets, every page fault evicts a page that another process immediately needs. Fault rate → infinity, useful work → zero. The fix is to reduce the degree of multiprogramming (suspend some processes) until the working sets fit in RAM.

### Huge Pages

Standard 4 KB pages require many TLB entries for large data. A 2 MB huge page covers 512× more space with a single TLB entry. Databases and scientific codes use them to avoid TLB thrashing. The cost is that a huge page must be contiguous in physical memory, increasing fragmentation.

## Practice

Work through `page_table_sim.py` to see demand paging, page faults, and replacement policies in action. Then work through `practice.py` for five targeted exercises.

## Checkpoint Questions

1. A 64-bit system uses 48-bit virtual addresses and 4 KB pages. How many levels of page table does x86-64 use, and why can a single-level table not work? Compute exactly how much RAM a flat page table would require.

2. Explain why `fork()` is fast even if a process has 1 GB of heap. What triggers the actual copy of a page, and at what granularity does the copy happen?

3. You have 4 physical frames and the following access string: 1 2 3 4 1 2 5 1 2 3 4 5. Compare FIFO, LRU, and OPT page fault counts. Which policy suffers the most?

4. A server is experiencing high CPU wait-I/O and its page fault rate is 10,000 major faults/second. Disk throughput is 100 MB/s and pages are 4 KB. Is the disk the bottleneck? What would you do first?

5. Describe a scenario where using huge pages (2 MB) could *hurt* performance compared to 4 KB pages. Think about what happens when a mostly-sparse 2 MB region is mapped.
