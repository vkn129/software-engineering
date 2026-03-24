# Day 28: Memory Allocator (Mini-project)

## Why This Exists

Every time you write `x = [1, 2, 3]` in Python or `malloc(64)` in C, something has to decide **where** in memory that data lives. The memory allocator is the invisible layer between your program and the OS that:

1. Requests large chunks of memory from the OS (via `sbrk` or `mmap`)
2. Subdivides those chunks into smaller blocks for your program
3. Tracks which blocks are in use and which are free
4. Reclaims memory when you call `free()` (or when the GC does it for you)

This is one of the most performance-critical pieces of any runtime. A bad allocator can make a fast algorithm slow. Understanding allocators connects directly to:

- **Physics**: Memory is a finite, linear address space. Locality matters because caches are small and fast, main memory is large and slow.
- **Economics**: Every allocation is a trade-off between speed (how fast can we find a block?), space efficiency (how much memory do we waste?), and complexity (how hard is the bookkeeping?).
- **Mathematics**: Fragmentation is an entropy problem. Over time, free memory scatters into unusable small pieces unless we actively fight it.

## Theory

### The Free List

The simplest allocator maintains a **free list** — a collection of available memory blocks. When an allocation request comes in, we search the free list for a suitable block.

#### First-Fit

Scan the free list from the beginning. Return the **first** block that is large enough.

```
Free list: [16] -> [64] -> [32] -> [128]
Request: 30 bytes

First-fit picks: [64] (first one >= 30)
```

- **Pros**: Fast — stops at the first match.
- **Cons**: Tends to fragment the beginning of memory. Small leftover fragments accumulate at the front.

#### Best-Fit

Scan the **entire** free list. Return the smallest block that is large enough.

```
Free list: [16] -> [64] -> [32] -> [128]
Request: 30 bytes

Best-fit picks: [32] (smallest block >= 30)
```

- **Pros**: Minimizes wasted space per allocation.
- **Cons**: Slow (must scan everything). Creates many tiny, unusable fragments.

#### Worst-Fit

Scan the entire free list. Return the **largest** block.

```
Free list: [16] -> [64] -> [32] -> [128]
Request: 30 bytes

Worst-fit picks: [128] (largest block)
```

- **Pros**: Leftover fragments are large enough to be useful.
- **Cons**: Slow. Breaks up large blocks quickly, so large allocations fail sooner.

### Splitting

When a free block is larger than the requested size, we **split** it:

```
Before: [FREE: 128 bytes]
Request: 32 bytes

After:  [USED: 32 bytes] [FREE: 96 bytes]
```

We only split if the leftover is large enough to be useful (typically > some minimum block size, to avoid creating tiny unusable fragments).

### Coalescing

When a block is freed, we check its neighbors. If adjacent blocks are also free, we **merge** them into one larger block:

```
Before free(B):  [FREE: 32] [USED: 64 (B)] [FREE: 48]
After free(B):   [FREE: 144]  (32 + 64 + 48, merged)
```

Without coalescing, the free list degrades into many small fragments that cannot satisfy large requests even though total free memory is sufficient.

### Fragmentation

#### External Fragmentation

Total free memory is sufficient, but it is scattered in non-contiguous blocks:

```
Memory: [USED:32] [FREE:16] [USED:64] [FREE:16] [USED:32] [FREE:16]
Total free: 48 bytes
Request: 48 bytes -> FAILS (no single block is 48 bytes)
```

#### Internal Fragmentation

Allocated blocks are larger than what the program requested:

```
Request: 30 bytes
Allocated: 32 bytes (rounded up to alignment)
Wasted: 2 bytes per block (internal fragmentation)
```

This happens due to alignment requirements, minimum block sizes, or power-of-2 rounding (as in the buddy system).

### Buddy System

The buddy system restricts all block sizes to **powers of 2**. This makes splitting and coalescing extremely fast:

1. Start with one large block of size 2^N.
2. To allocate size S, find the smallest power of 2 >= S.
3. If no block of that size exists, split a larger block in half repeatedly.
4. To free, check if the "buddy" (the other half from the same split) is also free. If so, merge them back.

```
Initial:    [1024]
Alloc(100): Split 1024->512+512, split 512->256+256, split 256->128+128
            [USED:128] [FREE:128] [FREE:256] [FREE:512]
            (100 bytes requested, 128 allocated = 28 bytes internal fragmentation)
```

Finding the buddy is a single XOR operation on the address:

```
buddy_address = block_address XOR block_size
```

- **Pros**: O(log N) allocation and free. Coalescing is trivial. No external fragmentation within size classes.
- **Cons**: Significant internal fragmentation (up to ~50%). Only power-of-2 sizes.

### Real-World: glibc malloc (ptmalloc2)

Production allocators are far more sophisticated. glibc's malloc uses:

1. **Small bins**: Exact-size free lists for sizes 16-512 bytes. O(1) allocation.
2. **Large bins**: Sorted free lists for larger sizes. Best-fit search.
3. **Unsorted bin**: Recently freed chunks go here first (temporal locality optimization).
4. **Top chunk**: The boundary with unallocated heap space. Extended via `sbrk`.
5. **mmap threshold**: Very large allocations (>128KB default) bypass the heap entirely and use `mmap`.
6. **Per-thread arenas**: Reduce lock contention in multithreaded programs.
7. **Chunk headers**: Each chunk stores its size and whether the previous chunk is in use (for coalescing).

The design reflects decades of real-world profiling: most allocations are small, most lifetimes are short, and contention kills throughput.

## Practice

`memory_allocator.py` implements three allocators from scratch:
- **SimpleAllocator** (first-fit with coalescing)
- **BestFitAllocator** (best-fit variant)
- **BuddyAllocator** (power-of-2 splitting and buddy merging)

`practice.py` contains four exercises:
1. Worst-fit allocation strategy
2. Block coalescing (merge adjacent free blocks)
3. Fragmentation measurement after random alloc/free workloads
4. Simple mark-and-sweep garbage collector

## Checkpoint Questions

1. **Why does best-fit often perform worse than first-fit in practice?** Best-fit creates many tiny unusable fragments. First-fit's fragments at the front tend to get coalesced or reused. Best-fit also requires scanning the entire list.

2. **What is the maximum internal fragmentation in the buddy system?** Just under 50%. Requesting 2^(k-1) + 1 bytes allocates 2^k bytes, wasting nearly half.

3. **Why does glibc malloc use per-thread arenas?** The free list is shared mutable state. Without per-thread arenas, every malloc/free requires a lock, which becomes a severe bottleneck under contention. Arenas let threads allocate independently most of the time.

4. **How does coalescing prevent external fragmentation?** By merging adjacent free blocks into larger ones, coalescing reconstructs contiguous free regions that can satisfy large requests. Without it, free memory fragments into many small pieces over time.

5. **Why does the buddy system use XOR to find buddies?** Two buddies differ in exactly one bit (the bit corresponding to their size level). XOR with the block size flips that bit, giving the buddy's address in O(1). This only works because all sizes are powers of 2 and blocks are aligned to their size.
