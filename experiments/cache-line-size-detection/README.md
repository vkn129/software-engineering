# Cache Line Size Detection

## Question

What is the L1 cache line size on this machine, measured directly via stride-access timing?

## Hypothesis

Modern x86 / ARM CPUs use **64-byte** cache lines almost universally. Apple Silicon M-series uses **128-byte** lines on some cores. The experiment should reveal a clear timing discontinuity at the true line size.

## Why Cache Lines Matter

The CPU never reads a single byte from RAM. It reads a **cache line** (a contiguous chunk, typically 64 bytes) into L1. Every subsequent access *within that line* is ~1 ns. Every access that *misses* the line costs ~10 ns (L2) to ~100 ns (DRAM).

This drives an enormous amount of real-world performance:

- **Struct field ordering**: pack hot fields into the same line. False sharing between unrelated fields on the same line in multi-threaded code can tank performance by 10x.
- **Array-of-structs vs struct-of-arrays**: SoA wins for hot-loop scans because each scan only touches lines it actually uses.
- **Linked lists vs arrays**: a linked list traversal is one cache line per node (pointer-chase). An array scan is one line per ~16 nodes (if nodes are 4 bytes). 16x fewer cache misses.
- **Hash table probing**: linear probing is fast partly because adjacent slots share cache lines. Open addressing beats chaining largely because of this.
- **Locks**: a contended lock on a 64-byte line can ping-pong between core caches at ~80 ns/transition. Pad locks to their own line.

If you don't know your cache line size, you can't reason about any of the above.

## How Stride Timing Detects Line Size

Walk an array, jumping `stride` bytes per access. For each stride, measure time per access.

- **stride < line_size**: consecutive accesses hit the same line → fast (one DRAM fetch amortized over many reads).
- **stride == line_size**: every access touches a fresh line → slow (one DRAM fetch per access).
- **stride > line_size**: no further slowdown — already paying one fetch per access.

The timing curve has a **knee at stride = cache_line_size**. That knee is the answer.

We pick an array large enough to defeat the L1 cache entirely (~32 MB), so every access is forced to go to L2/L3/DRAM. This isolates the cache-line effect from cache-capacity effects.

## What This Experiment Does *Not* Measure

- L2 / L3 line sizes (usually same as L1 on modern CPUs, but not guaranteed).
- Prefetcher behavior — hardware prefetchers may hide the knee for predictable strides. We use a randomized walk within the stride pattern to make prefetching harder.
- Multi-core / NUMA effects.

## Confounders

- **Thermal throttling**: run on a cool machine. Don't run during a build.
- **Background processes**: close browsers, IDE indexers. They will skew the noise floor.
- **Python overhead**: `time.perf_counter_ns()` itself takes ~50 ns. Per-access timing is too noisy. We measure **total time for N accesses** and divide. N is chosen so total time >> timer resolution.
- **`bytes` immutability**: we use a `bytearray` so the interpreter doesn't dedupe.

## Run

```bash
python detect_cache_line.py
```

Then fill in `results.md`.

## Expected Output Shape

```
Stride (B) |  ns/access
        1  |       0.8
        2  |       0.8
        4  |       0.9
        8  |       0.9
       16  |       1.1
       32  |       1.6
       64  |       3.4   <-- KNEE
      128  |       3.5
      256  |       3.5
```

The knee position = your cache line size.

## Connection to First Principles

This is **Physics meeting Algorithms**. Cache lines exist because:
1. DRAM access latency is dominated by row-activation time, not transfer time. Bulk transfer of a line is nearly free once the row is open.
2. Spatial locality is the empirical observation that programs tend to access nearby memory soon after. Cache lines monetize this observation.

Every "constant factor" in a Big-O analysis on real hardware is downstream of cache behavior. An O(n) linked list scan can be **10x slower** than an O(n log n) array sort + scan, because the array touches 1/16th as many cache lines.
