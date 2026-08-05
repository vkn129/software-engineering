# Day 111: Fractional Cascading

## The Problem

You hold `k` sorted lists. A query gives you one value `x` and asks for its
position in **every** one of them — the successor, the insertion point, the
matching record, whatever `lower_bound` means for your data.

The obvious answer is `k` independent binary searches: `O(k log n)`.

That is wasteful in a way that is easy to miss. The first binary search spends
`log n` comparisons learning *precisely* where `x` sits in the value space.
The second search throws all of that away and rediscovers it. So does the
third. You pay `log n` for information you already own.

Fractional cascading pays `log n` **once**, then walks the remaining `k - 1`
lists in `O(1)` each:

```
O(k log n)   ->   O(log n + k)
```

Chazelle and Guibas, 1986. It is a preprocessing technique — you pay in space
and build time to make the query cheap.

## Why It Matters

The `k`-sorted-lists shape is everywhere once you look for it:

- **LSM-tree reads** (LevelDB, RocksDB, Cassandra): a point or range read must
  consult every level's sorted run. That is exactly `k` sorted lists and one
  key. Real engines use bloom filters to *skip* levels instead — a different
  trade (probabilistic, no build-time pointer structure) aimed at the same
  cost.
- **Computational geometry**: the canonical use. Segment-tree and range-tree
  nodes each hold a sorted list; a stabbing or range query descends a
  root-to-leaf path and must binary search at every node. Cascading turns
  `O(log^2 n)` into `O(log n)`. This is the reason the technique exists.
- **Inverted-index posting lists**: intersecting `k` postings for a
  multi-term query, seeking each to the same document id.
- **Time-series shards**: one timestamp, `k` per-shard sorted arrays.
- **Multi-version / MVCC scans**: one visibility timestamp, one sorted version
  chain per key.

## The Structure

Build the augmented lists **from the last list backwards**. `A[k-1]` is just
`L[k-1]`. For every earlier `i`:

```
A[i] = merge( L[i],  every second element of A[i+1] )
```

Those borrowed elements are the **bridges**. They are not data — they are
`x`'s position in the next list, precomputed and planted where a search in
this list will trip over it.

Each entry of `A[i]` carries two pointers:

- `own[i][j]`  — the position in the original `L[i]` of the first element `>= A[i][j]`
- `next[i][j]` — the position in `A[i+1]` of the first element `>= A[i][j]`

```
L0 = [10, 40]
L1 = [20, 30, 50]
L2 = [25, 60]

A2 = [25, 60]                          (= L2)
A1 = merge([20,30,50], [60])           A2[1::2] = [60]
   = [20, 30, 50, 60]
A0 = merge([10,40], [30, 60])          A1[1::2] = [30, 60]
   = [10, 30, 40, 60]
```

Taking **every second** element is the whole design. Take all of them and each
list doubles the next, so `|A[0]|` blows up exponentially in `k`. Take every
second and the recurrence is `|A[i]| = |L[i]| + |A[i+1]| / 2`, which sums to at
most `2 * sum(|L[i]|)` — linear total space, by a geometric series.

## The Query

One binary search, then a walk:

1. `p = lower_bound(A[0], x)` — the only `log n` you pay.
2. For each level `i`: the answer for `L[i]` is `own[i][p]`. Then hop with
   `q = next[i][p]` and correct.

The correction is the subtle part. `next[i][p]` points at the successor of
`A[i][p]`, and `A[i][p] >= x`, so the pointer may sit slightly **past** the
true successor of `x`. Walk backwards while `A[i+1][q-1] >= x`.

That walk is `O(1)`, and here is why: `A[i]` contains every second element of
`A[i+1]`, so between two consecutive bridges lie at most 2 unrepresented
elements of `A[i+1]`. The overshoot is bounded by a constant, not by `n`. This
is the single claim the whole `O(log n + k)` bound rests on, and
`demo_bridge_walk` measures it rather than asserting it.

## Correctness of the `own` Pointer

`own[i][p]` is the lower bound of `A[i][p]`, not of `x`. Those are the same
index, and the argument is short:

Every element of `L[i]` also appears in `A[i]`. Suppose some `v` in `L[i]`
satisfied `x <= v < A[i][p]`. Then `v` would be an element of `A[i]` that is
`>= x` and strictly below index `p` — contradicting `p` being the first such
index. So no element of `L[i]` lies between `x` and `A[i][p]`, and both values
have the same lower bound in `L[i]`.

## The Empty-List Case

An empty `L[i]` is not a corner case to special-case away — it is the case
that breaks naive implementations, because `A[i]` can then be empty while
`A[i+1]` is not (that happens exactly when `A[i+1]` has one element, whose
`[1::2]` slice is empty). A query then has `p == 0 == len(A[i])` and there is
no entry to read a pointer from.

The fix is structural, not conditional: give both pointer arrays **length
`len(A[i]) + 1`** with a sentinel at the end.

```
own[i][ len(A[i]) ]  = len(L[i])        "x is past everything in L[i]"
next[i][len(A[i]) ]  = len(A[i+1])      "start the backward walk at the end"
```

Now `p` ranges over `[0, len(A[i])]` and is always a legal index. Empty lists,
`x` above every element, and `x` below every element all fall out of the same
code path with no branches. The backward walk from the sentinel is still
`O(1)`: if `x` exceeds everything in `A[i]`, then no odd-indexed element of
`A[i+1]` exceeds `x`, and a contiguous tail containing no odd index holds at
most one element.

## Complexity

| | Naive `k` binary searches | Fractional cascading |
|---|---|---|
| Query | O(k log n) | **O(log n + k)** |
| Space | O(N) | O(N), at most 2N with the every-second rule |
| Build | O(N) | O(N) with a merge pass, O(N log N) as written here |
| Update (insert/delete) | O(log n) into one list | **rebuild** — pointers are not local |

`N = sum(|L[i]|)`. The query win is real, and the update cost is the reason
you will not see this in a write-heavy system.

## Failure Modes

| Failure | When | Fix |
|---------|------|-----|
| Index error on an empty list | `A[i]` empty while `A[i+1]` is not | Sentinel entry at index `len(A[i])` in both pointer arrays |
| Exponential space | promoting *every* element instead of every second | `A[i+1][1::2]`. The factor-2 sampling is what makes the series converge |
| Off-by-one, answers one slot late | trusting `next[i][p]` without correction | Walk back while `A[i+1][q-1] >= x` — the pointer may overshoot |
| Walk is not O(1) | promoting every third or fourth element | Sparser bridges mean longer walks. Every-second is the balance point |
| Stale pointers | inserting into any `L[i]` after building | Rebuild. Pointers encode global positions and do not survive local edits |
| Wrong answers with duplicates | `upper_bound` semantics in one place, `lower_bound` in another | Pick one convention and use it in the pointers, the query, and the correction walk |
| Silently wrong on unsorted input | a caller hands you an unsorted list | Validate at build time; every argument above assumes sortedness |

## Checkpoint Questions

1. Why does the second of `k` binary searches repeat work the first already
   did? Name the information that gets discarded.
2. What breaks if `A[i]` borrows *every* element of `A[i+1]` rather than every
   second? Write the space recurrence for both.
3. `own[i][p]` is the lower bound of `A[i][p]`, but the query wants the lower
   bound of `x`. Prove they are the same index.
4. Why can `next[i][p]` overshoot the true answer, and why is the backward
   correction bounded by a constant?
5. Construct the input where `A[i]` is empty but `A[i+1]` is not. What does
   the sentinel do there?
6. Why is this a query-only structure? What exactly does an insert into
   `L[3]` invalidate?
7. LSM-trees have this exact shape and use bloom filters instead. What do
   they buy, what do they give up, and when would cascading be preferable?
