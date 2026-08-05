# Day 103: Timsort — The Adaptive Merge Sort

## Why Timsort Won

Tim Peters wrote Timsort in 2002 for Python 2.3, replacing CPython's quicksort.
Within 15 years it was Python's stdlib sort, Java's `Arrays.sort(Object[])`,
Android's framework sort, V8's JavaScript sort, and Rust's `slice::sort`.

Why? Three insights that classical CS textbooks underweight:

1. **Real data is rarely random.** Logs are mostly sorted. Database results
   are pre-grouped. UI lists are append-then-sort. Timsort exploits this.
2. **Comparisons are expensive in high-level languages.** A Python comparison
   is ~100 ns. Cutting comparisons matters more than reducing memory.
3. **Stability is non-negotiable.** Python's `sort(key=...)` semantics require
   it. Quicksort can't provide it.

Timsort delivers **O(n) on already-sorted input**, **O(n log n) worst case**,
and **stability** in 1000 lines of C.

## The Core Ideas

### 1. Natural Run Detection

Scan the input for "runs" — maximal monotonic subsequences. Ascending runs
are kept as-is. Descending runs are reversed in-place (since strict descent
is unique → reverse is also stable).

```
find_run(a, i):
    j = i + 1
    if j == len(a): return j
    if a[j] < a[i]:                    # strictly descending
        while j+1 < n and a[j+1] < a[j]: j += 1
        reverse(a, i, j)
    else:                               # non-decreasing
        while j+1 < n and a[j+1] >= a[j]: j += 1
    return j + 1
```

**Why strict descent (not non-increasing)?** To preserve stability. Equal
elements in a descending stretch must stay in original order; reversing
would flip them.

### 2. Minimum Run Length (minrun)

Pure run-detection gives runs of length 1 on random data → log(n) merge
passes of O(n) each. Timsort enforces a **minimum run length** (24–32 for
real implementations) by padding short runs using **binary insertion sort**.

The minrun formula picks a value in [32, 64] such that `n/minrun` is close
to (but ≤) a power of 2. This makes the merge tree balanced.

### 3. Merge Stack with Invariants

As runs are detected, push them onto a stack. After each push, enforce:

```
For top three runs A, B, C (C on top):
    |A| > |B| + |C|   AND   |B| > |C|
```

If violated, **merge the smaller of B's neighbors with B**. This keeps the
stack short (O(log n)) and balanced (merge sizes roughly equal).

These invariants were famously found to be **incorrect** in the original
Timsort paper — a 2015 paper by de Gouw et al. proved that the original
invariants could allow the stack to grow past its preallocated size on
inputs of size ~2⁶⁴. The fix: tighter invariants, plus a stack of size 85
(suffices for any 64-bit length).

### 4. Galloping Mode

When merging two runs A and B, naive merge compares head-of-A and head-of-B
one at a time. But if **many consecutive elements come from A**, this wastes
comparisons. After 7 consecutive picks from one side, Timsort switches to
**galloping**: exponential search into the other side, then binary search.

For runs where one is much smaller than the other (common when merging tails),
galloping cuts comparisons from O(min) to O(min · log(max/min)).

## Complexity Table

| Input pattern         | Comparisons |
|-----------------------|-------------|
| Already sorted        | **n - 1** (O(n)) |
| Reverse sorted        | n - 1 (one reverse + no merges) |
| Random                | O(n log n) |
| k pre-sorted runs     | O(n log k) |
| Worst case            | O(n log n) — tighter than quicksort |

## Pathological Inputs (for Timsort, there aren't many)

The only "bad" case is uniform-random data, where Timsort matches plain
merge sort. **There is no input that makes Timsort O(n²).**

The **stack-overflow bug** (de Gouw et al. 2015) is a memory bug, not a
complexity bug — fixed in Python 3.6, Java 9, Android API 26.

## Real-World Usage

| System                       | Adopted Timsort       | Notes                            |
|------------------------------|-----------------------|----------------------------------|
| CPython `list.sort`          | 2002 (Python 2.3)     | The original implementation      |
| Java `Arrays.sort(Object[])` | 2009 (JDK 7)          | Required by spec for stability   |
| Android framework            | 2010 (Honeycomb)      | Inherited from Java              |
| V8 (Chrome / Node.js)        | 2018 (V8 v7.0)        | Stable sort spec since ES2019    |
| SpiderMonkey (Firefox)       | 2019                  | Same ES2019 spec push            |
| Rust `slice::sort`           | Custom Timsort-like   | Pattern-defeating quicksort for unstable |
| Swift `sort()`               | Introsort (not Timsort) | Apple chose introsort for perf  |

## What's in CPython's listsort.c

Tim Peters' implementation in `Objects/listobject.c` (~1500 lines) is one of
the most-read source files in CS education. It includes:

- `merge_lo` / `merge_hi`: merges where left/right is smaller
- `gallop_left` / `gallop_right`: galloping exponential search
- `merge_compute_minrun`: bit-twiddling minrun formula
- `merge_collapse`: enforce stack invariants

Reading listsort.c after implementing your own simplified version is
one of the best ways to learn production-grade systems C.

## Checkpoint Questions

1. Why does Timsort reverse a strictly-descending run but not a
   non-increasing run? Give an example where reversing a non-increasing run
   would break stability.
2. The minrun formula picks a value in [32, 64]. What goes wrong if you
   pick minrun = 1? What goes wrong if you pick minrun = n?
3. Walk through Timsort's stack invariant enforcement on runs of sizes
   `[16, 8, 4, 2, 1]`. Which merges happen, in what order?
4. Galloping mode kicks in after 7 consecutive picks from one side. Why 7?
   What input pattern would benefit most from galloping?
5. The 2015 de Gouw et al. paper found a stack-overflow bug in Timsort.
   Without reading the paper, can you sketch how a sequence of pushes
   could violate the original invariant?
6. V8 switched from quicksort to Timsort in 2018 — JavaScript's spec changed
   to require stability. Name one user-observable program that breaks under
   the old quicksort behavior but works under Timsort.
