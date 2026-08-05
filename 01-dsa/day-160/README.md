# Day 160: Mini-Project — Parallel Sort

## The Goal

Build a parallel sort and **measure real speedup** against a single-threaded
baseline. This is a synthesis project tying together divide-and-conquer
(day-068 mergesort), threading (day-091 concurrency basics), and the
parallel-systems thinking from days 155-156.

We measure **actual wall-clock speedup** — not theoretical, not "logical
depth." Real numbers on real hardware.

## The Algorithm

Classic parallel mergesort:

```
parallel_sort(arr):
    if len(arr) ≤ THRESHOLD: return sequential_sort(arr)
    mid = len(arr) // 2
    left, right = arr[:mid], arr[mid:]
    in parallel:
        left  = parallel_sort(left)
        right = parallel_sort(right)
    return merge(left, right)
```

Two key knobs:

1. **THRESHOLD** — below this size, do it serially. Crossing process boundaries costs ~ms; sorting 100 items in a process costs μs. The threshold should be high enough that fork cost amortizes.

2. **Worker pool size** — more workers ≠ more speed once you exceed core count.

## Python's GIL — The Honest Picture

**Threads** in Python share an interpreter and acquire the GIL on every
bytecode dispatch. Pure-Python CPU-bound work on threads = **no parallelism**.

**Processes** in Python have their own interpreter, their own memory, no GIL
contention. But:
- Each process is heavyweight (~10-50 MB resident)
- Communicating requires pickling — `[int, int, ...]` of 1M elements takes
  noticeable time to serialize
- Fork/spawn cost is real

This means for pure-Python sort, **multiprocessing only wins on large arrays**.

We show both:
- **Threaded** parallel sort → demonstrates GIL-induced anti-speedup
- **Process** parallel sort → demonstrates real speedup with caveats

## Amdahl's Law

The maximum theoretical speedup with infinite cores is:

```
S = 1 / (s + p/N)
```

where `s` is the serial fraction (here: the final merge, since merge can't
be parallelized trivially) and `p` is the parallel fraction.

For mergesort, the final merge over n elements is O(n) — and that's a
serial bottleneck. With unlimited cores, speedup tops out at ~log n
(the number of merge layers).

This is why **parallel merge** (k-way merge by partitioning) exists in
real implementations — but it's a Day-161+ topic.

## Other Sort Strategies

| Strategy | When it wins |
|---|---|
| Parallel mergesort | General-purpose; what we do |
| Parallel quicksort | Lower constant but skew-sensitive |
| Sample sort | Better load balance; standard for ≥4 cores |
| Radix sort (parallel) | Fixed-width keys, GPU-friendly |
| TeraSort | Distributed (Day 156 covered the framework) |

## Measurement Hygiene

To get an honest speedup number:

1. **Warm-up**: first run pays JIT, allocator, import costs. Discard or use median of 5+ runs.
2. **Same data**: identical input arrays, same RNG seed.
3. **Wall-clock**: `time.perf_counter()`, not CPU time.
4. **Don't include I/O**: only the sort itself.
5. **Compare apples to apples**: parallel mergesort vs sequential mergesort, not vs `list.sort()` (which is Timsort in C — different beast).

## What We Should See

On a 4-core machine sorting 200,000 Python ints:

- **Threaded version**: ~1.0x speedup or worse (GIL anti-speedup; thread overhead)
- **Process version (cold)**: ~1.5-2.5x speedup (process spawn cost amortizes)
- **Process version (pool reused)**: closer to 2-3x

We will **not** see 4x. The merge is serial, pickling is expensive, and
Amdahl is unforgiving.

## What "Reporting Speedup" Looks Like

```
sequential mergesort:  0.842s
threaded (4 workers):  1.107s   (0.76x — anti-speedup!)
process (4 workers):   0.451s   (1.87x speedup)
list.sort() (Timsort): 0.087s   (9.7x — different game; C-level)
```

The lesson isn't "use C for everything." The lesson is: **measure honestly**.
Performance claims without measurement are worthless.

## Checkpoint Questions

1. Why does parallel mergesort's speedup top out below the number of cores even with perfect work splitting?
2. You sort an array of 100 elements with 8 processes. How much faster than sequential? Why?
3. Pickling cost: sketch the wall-clock breakdown of a `multiprocessing.Pool.map(sort, [arr])` call for a 1M-element list.
4. Why is sample sort preferred over mergesort in production parallel implementations?
5. If you switched to NumPy arrays, would the GIL still serialize? Why or why not?
