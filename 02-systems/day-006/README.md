# Day 6: Memory Allocators — `malloc` from Scratch

## Why This Exists

Every time you call `malloc`, `new`, or even allocate a Python list, something underneath is asking the operating system for raw memory and then handing you a slice of it. The OS only hands out memory in large chunks (pages, typically 4 KB). Your program may want 24 bytes. Something has to bridge that gap — that something is the memory allocator.

Without an allocator you would either waste enormous amounts of virtual address space (asking the OS for a new page every time you need 8 bytes) or write every program to manage its own memory pool by hand. The allocator is the layer that makes dynamic memory practical: it maintains a pool, divides it into user-requested sizes, and reclaims it when the user is done.

Understanding allocators matters because they are on the critical path of almost every program. A bad allocator choice or a misuse pattern (fragmentation, false sharing, repeated small allocations) can slow a high-performance service by 2-5x. Engineers at Facebook, Google, and Mozilla rewrote their allocators (jemalloc, tcmalloc, mimalloc) precisely because the system allocator was a bottleneck.

### What If This Didn't Exist?

Without a general-purpose allocator, programs would have two choices: static allocation (declare every variable at compile time — no dynamic data structures, no variable-length inputs) or direct OS calls (mmap/brk for every allocation — catastrophically slow and wasteful). Neither scales. Dynamic languages would be impossible. Web servers could not handle variable-length requests. Essentially, modern software as we know it would not exist.

### Why This Name?

`malloc` is short for "memory allocation," coined in the original C standard library. The companion `free` releases it back. The underlying syscalls are `brk`/`sbrk` (move the "program break" — the end of the data segment) and `mmap` (map anonymous pages). The word "heap" for dynamically allocated memory comes from the unordered pile of available memory, as opposed to the stack which is strictly ordered by call depth.

### The Physics Connection

DRAM is organized into rows and columns on a silicon die. Accessing a new row incurs an "RAS latency" (~15 ns) to charge a sense amplifier. Spatial locality — placing objects near each other in memory — means you are more likely to reuse the same row and stay in L1/L2 cache (0.5–4 ns latency). A fragmented heap scatters objects across many pages; traversing a linked list of scattered nodes can touch dozens of different cache lines, each costing a full DRAM round-trip. Allocator design is therefore inseparable from memory hierarchy physics: the goal is to keep hot objects close together in physical addresses.

### The Mathematics Connection

Fragmentation is fundamentally about packing problems. Internal fragmentation is the waste inside an allocated block (you asked for 13 bytes, you received 16 due to alignment — 3 bytes wasted). External fragmentation is the waste between blocks: free regions exist but are too small or wrongly shaped to satisfy the next request. The buddy system reduces external fragmentation by constraining sizes to powers of 2, which makes splitting and merging simple bit operations. Formally, in a buddy system of size 2^k, any block of size 2^j has exactly one buddy at address XOR 2^j — a relationship derivable from binary arithmetic. The best-fit strategy minimizes expected internal fragmentation but maximizes fragmentation measurement complexity (O(n) scan vs O(log n) for trees).

### The Economics Connection

Allocator design is a trade-off surface with three axes: throughput (allocations per second), space efficiency (how much of the heap is actually usable), and latency (worst-case time for a single allocation). A bump allocator optimizes purely for throughput and latency at the cost of never reclaiming memory — optimal for arenas that are freed all at once (one HTTP request). A best-fit free list optimizes space efficiency at the cost of O(n) search time. Thread-caching allocators (tcmalloc, jemalloc) add a fourth axis — thread scalability — by giving each thread a private pool to avoid lock contention, accepting higher per-thread memory overhead in exchange for near-zero contention at high core counts. The right choice depends on your workload's allocation size distribution, object lifetime distribution, and thread count — all economic decisions about which resource is scarce.

## When Does This Break?

- **Heap exhaustion**: if you never free memory (leak), the heap grows until the OS refuses to give more. The allocator cannot recover — it returns NULL.
- **Double free**: freeing a pointer twice corrupts the free list, leading to two allocations returning the same address and silent data corruption.
- **Use-after-free**: reading or writing a block after `free` reads allocator metadata or another live object's data. A common source of security vulnerabilities.
- **Alignment violations**: some hardware instructions (SIMD, atomic operations) require 16- or 64-byte aligned addresses. If the allocator does not guarantee alignment, these fault with a SIGBUS.
- **Fragmentation death spiral**: a long-running server with mixed large/small allocations can exhaust the heap even when total live bytes are much less than total heap size, because free space exists only in fragments too small to satisfy new large requests.
- **False sharing**: thread-local caches reduce lock contention, but if two threads frequently allocate/free objects that land on the same cache line, they still incur coherence traffic — a hidden performance cliff.

## When Should You Violate This?

- Use arena/region allocation when objects have identical lifetimes (parse a JSON document into an arena, free the whole arena when done — zero per-object overhead).
- Use a slab allocator (pool of fixed-size objects) for kernel objects or hot paths where size is always known (avoiding the free-list search entirely).
- Use stack allocation (`alloca` or local arrays) for small, short-lived buffers when you know the size at compile time — zero allocator overhead.
- Use reference-counted or garbage-collected memory (Python, Go, Java) when developer productivity outweighs the overhead — the GC is a general allocator with different trade-offs, not a violation of the principle.

## Theory (45 min)

### Level 1: Bump Allocator

The simplest allocator: maintain a pointer to the next free byte. Allocation bumps the pointer forward by the requested size. Free does nothing. Throughput is O(1) and essentially as fast as pointer arithmetic. The cost is that memory is never reclaimed until the entire arena is reset.

```
heap: [used | used | used | FREE ...]
                            ^
                           bump ptr
```

Used for: request-scoped arenas, game frame allocators, parser temporaries.

### Level 2: Free-List Allocator

When a block is freed, insert it into a linked list of free regions. When allocating, search the free list for a block that fits.

Each free block stores a small header containing its size and a pointer to the next free block. This header lives in the block itself, so there is zero extra memory overhead.

**Placement policies:**
- **First-fit**: take the first block that is large enough. Fast (stop at the first hit), but leaves many small fragments at the front of the list over time.
- **Best-fit**: scan the entire list, take the smallest block that fits. Minimizes internal fragmentation but is O(n) and tends to create many tiny unusable slivers.
- **Worst-fit**: take the largest available block. Leaves larger leftover fragments that are more likely to be reusable — almost never used in practice.

**Coalescing**: when freeing a block, check if its neighbors are also free. If so, merge them into one larger block. Without coalescing, repeated alloc/free cycles of different sizes turn the heap into a checkerboard of small free fragments (external fragmentation).

### Level 3: Buddy Allocator

Restrict block sizes to powers of 2. The heap of size 2^k is split recursively: a request for 2^j bytes splits a 2^(j+1) block into two "buddies" of size 2^j. When a block is freed, if its buddy is also free, they merge back into a 2^(j+1) block.

Finding a block's buddy is pure arithmetic: `buddy_addr = block_addr XOR block_size`. Merging is O(log n) in the worst case (bubbles up through the size classes).

The Linux kernel uses a buddy allocator for physical page allocation. The tradeoff: internal fragmentation of up to 50% (a 33-byte request uses a 64-byte block), but external fragmentation is nearly eliminated.

### Level 4: Slab Allocator

Pre-allocate a "slab" — a large region divided into fixed-size slots for a single object type (e.g., all `struct inode` objects). Allocation is O(1): pop a slot off a free stack. Free is O(1): push the slot back. No fragmentation because all objects are the same size.

The Linux kernel's slab allocator (and its successors slub/slob) also keeps constructor/destructor state: a freed inode is not zero-initialized again — its initialized fields are preserved, saving re-initialization cost on the next allocation.

### Level 5: Thread-Caching Allocators (tcmalloc / jemalloc)

Production allocators add a thread-local cache (tcache) in front of the global heap. Each thread has size-class bins for small objects. Allocation and free for small objects never touch a lock. When a thread's bin is full, it flushes a batch to the central heap under a lock. This reduces lock contention from O(threads) to O(1) amortized.

jemalloc (used in Firefox, FreeBSD) separates the heap into independent "arenas" to reduce false sharing across threads. tcmalloc (used at Google) adds a page heap for large objects and a transfer cache for medium objects. Both use size classes (8, 16, 32, 48, 64, 80, 96, 112, 128, ... bytes) so that internal fragmentation is bounded to ~12.5%.

### Alignment

Hardware often requires or prefers naturally aligned addresses: a 4-byte int at an address divisible by 4, an 8-byte double at an address divisible by 8. SIMD instructions (SSE, AVX) may require 16- or 32-byte alignment. Allocators guarantee a minimum alignment (typically 8 or 16 bytes) by rounding up every allocation size to a multiple of the alignment and starting the heap at an aligned address.

## Practice (20 min)

See `practice.py` for 5 exercises: best-fit search, double-free detection, alignment-aware allocation, slab allocator, and fragmentation measurement.

Also run `allocator.py` to see bump, free-list, and buddy allocators operating on the same workload with fragmentation stats printed at the end.

## Checkpoint Questions

1. A bump allocator returns addresses starting at offset 0 in a 1024-byte heap. Requests come in for 7, 13, and 4 bytes. Assuming 8-byte alignment, what are the three returned addresses and how many bytes are wasted to padding?

2. Explain why first-fit tends to leave small fragments near the beginning of the free list over time, and how "next-fit" (start each search where the last one left off) partially addresses this.

3. In a buddy allocator with a 512-byte heap, what sequence of splits happens to satisfy a 20-byte request? What is the address of the buddy of the block at offset 64 with size 64?

4. A production service leaks 1 KB per request and handles 10,000 requests per second. How long until it exhausts a 32 GB heap? What allocator change would make this leak immediately visible in metrics?

5. Why does a slab allocator completely eliminate external fragmentation for its object type, and what is its worst-case internal fragmentation percentage? When does the slab approach become impractical?
