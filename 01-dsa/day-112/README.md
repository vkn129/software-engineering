# Day 112: Mini-Project — Searchable Sorted Index

## What We're Building

One index over integer keys, four search backends behind a single API, and a
measurement that says which one to actually use:

- **Binary search** (Day 106) — the baseline nothing has to beat, it just has
  to be beaten.
- **Interpolation with a binary fallback** (Day 108) — bets on uniform data,
  capped so the bet cannot cost more than `O(log n)`.
- **van Emde Boas** (Day 109) — bets on a bounded universe; the only backend
  whose cost does not grow with the key count.
- **Staircase over a reshaped grid** (Day 110) — deliberately the wrong tool
  here, included to show what discarding a total order costs.

Plus a **sharded** index that answers "successor in every shard" with
fractional cascading (Day 111) instead of `k` independent searches.

This is the shape of a real read path: a static sorted index, several
candidate probe strategies, and a decision made on measurements rather than
asymptotics. It is deliberately immutable — every technique in days 106-111 is
a query-time structure that a single insert would invalidate.

## Architecture

```
   build(keys)
       |
       v
  [ sorted, deduplicated key array ]      <- the one source of truth
       |
       +--> BinaryBackend          probes ~ log2(n)
       +--> InterpolationBackend   probes ~ log log n on uniform, capped
       +--> VEBBackend             probes ~ log log U   (needs bounded U)
       +--> GridBackend            probes ~ rows + cols (weaker ordering)
       |
       v
  lookup(key) / successor(key) / range_query(lo, hi)

   ShardedIndex(k shards)
       |
       +--> naive:   k binary searches       O(k log n)
       +--> cascade: fractional cascading    O(log n + k)
```

Every backend is instrumented with a **probe counter**. Probes are the unit of
measurement, not seconds — see below.

## Why Probes, Not Seconds

The tests assert correctness only. Nothing in this day asserts a wall-clock
number, and that is a deliberate constraint rather than laziness:

- Wall-clock in Python measures interpreter overhead, not algorithm shape. A
  `log log n` algorithm with dict lookups routinely loses to a `log n`
  algorithm on a contiguous list.
- Timing is nondeterministic. A test asserting "interpolation is faster" fails
  on a loaded machine and teaches the reader to distrust the suite.
- Probe counts are exact, reproducible integers. The gap between `log2(n)` and
  `log log n` is visible in the count and invisible in the clock at this scale.

So: **probe counts are asserted, timings are printed and never asserted.**
That is the honest split.

## The Measured Comparison

`compare_backends()` runs every backend over the same key set and reports
probes per lookup. The results the reader should be able to predict before
running it:

1. **Binary search is the right default.** It has no preconditions and its
   worst case equals its average case.
2. **Interpolation wins on uniform keys and loses on clustered ones.** The
   iteration cap is what converts "loses" from `O(n)` into `O(log n)`. Without
   a cap — or without a probe that is guaranteed to shrink the interval — the
   clustered case is a hang, not a slowdown. Day 108's own `practice.py`
   shipped exactly that bug.
3. **vEB's probe count is flat in `n` and grows with the universe.** Doubling
   the key count changes nothing; going from 16-bit to 32-bit keys adds one
   level. It is also the only backend that answers `successor` on a miss as
   cheaply as on a hit.
4. **The grid backend is worse than binary at every size**, which is the
   point. Reshaping a totally ordered array into a merely row+column-sorted
   grid throws information away, and `O(sqrt n)` is what that costs.
   Staircase search is for when you never had the total order.
5. **Cascading beats `k` binary searches once `k` exceeds a small constant**,
   and the crossover is visible in the printed table.

## What Could Go Wrong (and Tests for Each)

1. **Duplicate keys** — `build` deduplicates, so positions refer to the
   deduplicated array. Checked against a `sorted(set(...))` oracle.
2. **Empty index** — every operation must answer, not raise. `successor` on an
   empty index returns `-1`, `range_query` returns `[]`.
3. **Key outside the vEB universe** — the universe is sized at build time from
   the maximum key. A later query above it must report "absent", not raise.
   Checked with queries far above and below the range.
4. **Negative keys** — vEB has no representation for them, so the index
   applies a build-time offset and the backend never sees a negative. Checked
   with an all-negative key set.
5. **Interpolation on identical keys** — the classic divide-by-zero, and the
   classic infinite loop when the probe stops shrinking the interval. Checked
   with `[7] * 200`.
6. **Grid with a ragged tail** — `n` is rarely a multiple of the column count.
   The last row is padded with a sentinel above every real key so the column
   ordering still holds. Checked at every `n` from 0 to 40.
7. **Cascading with an empty shard** — Day 111's sentinel case. Checked with
   shards empty in the first, middle and last position.

## Comparison to Real Systems

| Concept | Our impl | Production |
|---------|----------|------------|
| Index storage | one sorted `list` in memory | mmap'd immutable pages, B-tree or SSTable blocks |
| Point lookup | binary / interpolation | binary search within a page after a B-tree descent |
| Successor | backend-specific | leaf-level linked list (B+tree) |
| Range query | successor + forward scan | leaf scan, prefetched |
| Multi-shard read | fractional cascading | bloom filter per level to *skip* shards (LSM) |
| Rebuild on write | full rebuild | background compaction, immutable runs |

The structural point survives the simplification: **read-optimised indexes are
immutable, and every technique in this phase is a preprocessing trade** — you
pay at build time to make queries cheap, and any write throws that work away.
That is why LSM-trees compact in the background instead of updating in place.

## Checkpoint Questions

1. Why does this index deduplicate at build time, and what would `successor`
   have to do differently if it did not?
2. The interpolation backend caps its iterations. What does the cap convert
   the worst case *from*, and *to*? What breaks without it?
3. vEB probe counts do not move when you double `n`. Explain in one sentence,
   then say what does move them.
4. The grid backend is slower than binary at every size. Why is it in the
   project at all, and when would the staircase be the only option?
5. Why are timings printed but never asserted? Name two ways a timing
   assertion fails here that a probe assertion does not.
6. Negative keys are handled with a build-time offset rather than inside the
   vEB. Why is that the right layer for the fix?
7. An LSM-tree consults `k` sorted runs per read — the exact shape the sharded
   index solves with cascading. Real engines use bloom filters instead. What
   do they give up to get that, and when would you prefer cascading?
