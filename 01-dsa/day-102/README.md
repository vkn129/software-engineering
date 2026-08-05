# Day 102: External Sorting — When Data Exceeds RAM

## The Problem

You have **100 GB** of records on disk. You have **8 GB** of RAM. Sort the
data. `sorted(list)` is not an option — the input doesn't fit.

This is the classical **external sorting** problem, and it's how every
database, every MapReduce framework, and every disk-backed sort works.

## The Disk-Memory Hierarchy

| Level    | Capacity | Random read    | Sequential read |
|----------|----------|----------------|-----------------|
| L1 cache | 64 KB    | 1 ns           | 1 ns            |
| L2 cache | 256 KB   | 3 ns           | 3 ns            |
| RAM      | 16 GB    | 100 ns         | 10 GB/s         |
| SSD      | 1 TB     | 50,000 ns      | 3 GB/s          |
| HDD      | 10 TB    | 10,000,000 ns  | 200 MB/s        |

Sequential disk access is **10-100× faster** than random. Any external sort
that does random reads loses. The algorithms below exploit sequentiality
ruthlessly.

## External Merge Sort — The Standard Algorithm

### Phase 1: Create sorted runs

Read input in chunks of size M (≤ RAM size). Sort each chunk in memory.
Write back as a "run" file.

```
runs = []
while not eof(input):
    chunk = read(M bytes)
    sort(chunk)              # in-memory sort
    write_run_file(chunk)
    runs.append(file)
```

Result: ⌈N/M⌉ sorted runs on disk.

### Phase 2: K-way merge

Open all runs simultaneously. Use a min-heap of size K = #runs. Repeatedly
pop the smallest element, write to output, advance that run.

```
heap = [(read_one(r), r) for r in runs]
heapify(heap)
while heap:
    val, r = heappop(heap)
    write(val)
    nxt = read_one(r)
    if nxt is not None:
        heappush(heap, (nxt, r))
```

**Each element moves O(log K)** through the heap. Total: O(N log K).

### Why a heap? Why not pairwise merge?

Pairwise merge does ⌈log₂ K⌉ passes, each reading all N records. That's
**O(N log K) total I/O**. The heap-based K-way merge does **1 pass over the
data** (in terms of disk I/O) — still O(N log K) compute, but I/O is what
matters.

## Multi-Pass External Sort

What if K is too large to fit all run buffers in memory? E.g., 10⁶ runs and
only 10⁴ buffer slots? Do **two passes**:

1. Merge groups of 10⁴ runs → 100 super-runs
2. Merge 100 super-runs → final output

Each pass is O(N) I/O. Total: O(N · ⌈log_M(N)⌉).

In practice: most databases get away with 1 pass because M (sort memory)
is large enough.

## Replacement Selection — Doubling Run Lengths

When creating initial runs, **don't** fill a chunk and dump it. Instead,
maintain a heap of size M and use **replacement selection**:

1. Fill heap with M elements.
2. Pop min, write to current run, read next input.
3. If next ≥ last written: add to current heap.
4. If next < last written: it can't go in this run; hold for next run.
5. When current heap empties, current run ends.

**Result**: average run length is **2M** (Knuth), halving the number of runs
and thus log K. Used in IBM mainframe sorts since the 1960s.

## Modern Cousins

| System                | External sort flavor          | Notes |
|-----------------------|-------------------------------|-------|
| PostgreSQL `tuplesort.c` | External merge with runs    | Default for `ORDER BY` larger than `work_mem` |
| SQLite                | External merge sort           | Used when temp index exceeds cache |
| Hadoop MapReduce      | External merge in shuffle     | Reduce phase merges sorted maps |
| Spark sort            | External merge + on-disk runs | Adaptive: in-memory until spill |
| GNU `sort` (coreutils)| External merge + runs in /tmp | `--buffer-size` controls M |

The 2007 paper "**TPMMS**" (Two-Phase Multi-Way Merge Sort) describes
exactly this design — and it's still the basis of every disk-backed sort
today.

## Complexity Table

| Phase           | I/O                       | Time            |
|-----------------|---------------------------|-----------------|
| Run creation    | O(N) read + O(N) write    | O(N log M)      |
| K-way merge     | O(N) read + O(N) write    | O(N log K)      |
| Total (1 pass)  | O(N) — 2 reads, 2 writes  | O(N log N)      |

For N = 10¹¹ bytes (100 GB) and disk bandwidth 200 MB/s: **~17 minutes**
minimum, limited entirely by disk I/O.

## Pathological Cases

| Input                          | Behavior              |
|--------------------------------|-----------------------|
| Already sorted                 | 1 run, no merge phase |
| All-equal                      | 1 run                 |
| Reverse sorted                 | N/M runs of length M  |
| Adversarial (alternating runs) | Maximum number of runs|

## Real-World Usage

| System              | Implementation        | When triggered                       |
|---------------------|-----------------------|--------------------------------------|
| PostgreSQL          | External merge sort   | `work_mem` (default 4 MB) exceeded   |
| MySQL InnoDB        | External merge sort   | `sort_buffer_size` exceeded          |
| Hadoop MapReduce    | External merge sort   | Reduce-side shuffle always           |
| Apache Spark        | External merge sort   | `spark.shuffle.spill=true` (default) |
| ClickHouse          | External merge sort   | `max_bytes_before_external_sort`     |
| GNU `sort`          | External merge sort   | Input > `--buffer-size`              |

## Checkpoint Questions

1. You have N=10⁹ records (each 100 bytes), M=10⁸ bytes of RAM. How many
   initial runs are created? With buffer size 1 MB per run during merge,
   does the merge fit in one pass?
2. Why does a K-way heap-based merge do O(N log K) work but only 1 pass of
   I/O over the data?
3. Walk through replacement selection on input `[5, 8, 3, 2, 9, 7, 1, 4]`
   with heap size 3. List the resulting runs.
4. Modern SSDs do random reads in ~50 μs vs ~5 ms for HDDs (100× faster).
   How does this change the design of external sort? Does sequential access
   still matter?
5. Sorting 100 GB with N records of size 100 B and 8 GB RAM: estimate the
   minimum wall-clock time on a 500 MB/s SSD.
6. PostgreSQL spills to disk when `work_mem` is exceeded. Why is the default
   only 4 MB? What goes wrong if you set it to 100 GB?
