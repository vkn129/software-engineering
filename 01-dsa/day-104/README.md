# Day 104: Sorting Networks & Batcher's Bitonic Sort

## Why It Matters

Every sort in days 99-103 decides what to do next by **looking at the data**.
Quicksort's partition depends on the pivot comparison; Timsort's run detection
depends on whether the next element rose or fell. That is normally a virtue — it
is exactly how Timsort exploits presorted input.

A **sorting network** gives it up on purpose. The comparator sequence is fixed
before any data exists. Same wires, same order, same count — for a sorted input,
a reversed input, or noise. That buys three things you cannot otherwise have:

- **It fits in hardware.** No branches means no control unit. A sorting network
  is a pile of compare-exchange cells and wires. Network switches sort priority
  queues this way at line rate; FPGA and ASIC sorters are almost always Batcher
  networks.
- **It fits SIMD and GPU.** GPU threads in a warp execute in lockstep; a
  data-dependent branch makes them *diverge*, and the hardware then serialises
  both sides. Bitonic sort has no divergence, which is why it is the standard
  building block for GPU sorting and why SIMD sorters use fixed networks for
  their small-array base cases (n ≤ 16) instead of an insertion sort.
- **It is constant-time, so it does not leak.** How long your sort ran is
  observable. If the duration depends on the values, and the values are a secret
  key or a set of sealed bids, the duration *is* a side channel. Oblivious
  sorting is a standard primitive in secure multi-party computation, ORAM, and
  encrypted databases, precisely because the access pattern reveals nothing.

The cost is that a network is fixed-size and does **more** total work. It never
finishes early. That trade — more comparisons, but a schedule known in advance —
is the whole subject.

## Comparators

A comparator is a pair of wire indices `(lo, hi)`:

```
    wire lo  ──────●──────  min(x, y)
                   │
    wire hi  ──────●──────  max(x, y)
```

In software that is `if a[lo] > a[hi]: swap`. In hardware it is one comparison
driving two multiplexers — and crucially it **executes either way**. The swap is
not a branch taken or not taken; it is a mux select. That is why "branch-free"
and "constant-time" are the same claim here.

Emitting a pair **reversed** — `(3, 2)` instead of `(2, 3)` — puts the larger
value first. That is how a descending comparator is written without inventing a
second kind of comparator at all.

## Size and Depth Are Different Numbers

| Metric | Definition | This is the latency when… |
|---|---|---|
| **size** | total comparator count | you have one comparator, run serially |
| **depth** | number of parallel layers | you have as many comparators as you want |

Two comparators can share a layer iff they touch no common wire — sharing a wire
is the only dependency a network has. Depth is the number hardware people care
about, and it is why Batcher's construction is worth its extra comparisons.

## Bitonic Sequences

A sequence is **bitonic** if it rises then falls, or is a rotation of one:

```
1 4 7 6 2         bitonic  (up, then down)
7 5 3 1 0 2 4 6   bitonic  (down, then up — a rotation)
1 4 2 5 3         NOT bitonic (up, down, up, down)
```

Batcher's 1968 observation: **a bitonic sequence of length n can be sorted in
log n parallel layers.** Take the half-length compare-exchange

```
for i in 0 .. n/2 - 1:
    compare_exchange(a[i], a[i + n/2])
```

Afterwards three things are true at once:

1. every element of the low half ≤ every element of the high half,
2. the low half is itself bitonic,
3. the high half is itself bitonic.

So recurse on the halves — and they never interact again. That independence is
the whole reason it parallelises: after the first layer, the two halves are two
completely separate problems.

## Batcher's Bitonic Sort

Build a full sort out of that merge:

```
bitonic_sort(n):
    sort the first  half ASCENDING
    sort the second half DESCENDING    <- the concatenation is now bitonic
    bitonic_merge(the whole thing)
```

`log n` merge stages, with stage `i` having depth `i`:

```
depth = 1 + 2 + ... + log n = log n (log n + 1) / 2   =  O(log^2 n)
size  = (n/2) * depth                                 =  O(n log^2 n)
```

**The direction trick.** The implementation never branches on direction either.
Whether wire `i` sits in an ascending or a descending block is read straight out
of one bit of its index — `i & k`. A descending comparator is simply the pair
emitted backwards. The entire schedule is a function of `n` and nothing else.

```
n=8 bitonic network, 24 comparators, depth 6:

  layer 0: (0,1) (3,2) (4,5) (7,6)
  layer 1: (0,2) (1,3) (6,4) (7,5)
  layer 2: (0,1) (2,3) (5,4) (7,6)
  layer 3: (0,4) (1,5) (2,6) (3,7)
  layer 4: (0,2) (1,3) (4,6) (5,7)
  layer 5: (0,1) (2,3) (4,5) (6,7)
```

Reversed pairs like `(3,2)` and `(6,4)` are the descending blocks.

## The 0-1 Principle — How You Prove One Is Correct

You cannot test a network on all `n!` orderings. For n = 16 that is
20,922,789,888,000 cases.

> **0-1 principle.** A comparator network sorts all inputs **iff** it sorts all
> inputs made only of 0s and 1s.

**Why.** A comparator network commutes with any monotone function `f`: since
`min(f(x), f(y)) = f(min(x, y))` and likewise for max, running the network on
`f(x)` gives exactly `f(run(x))`. Now suppose the network fails on some input
`x`, leaving `out[i] > out[j]` for `i < j`. Choose the threshold function

```
f(v) = 0 if v < out[i] else 1
```

`f` is monotone, so `f(x)` is a **binary** input, and the network fails on it in
the same two positions. So any counter-example implies a binary counter-example.
Contrapositive: no binary counter-example means no counter-example at all.

That takes verification from `n!` to `2^n`:

| n | permutations | binary inputs |
|---|---|---|
| 8 | 40,320 | 256 |
| 12 | 479,001,600 | 4,096 |
| 16 | 20,922,789,888,000 | 65,536 |

This is not a testing shortcut. It is *the* standard proof technique for
comparator networks, and it is why this day ships a verifier rather than a
handful of examples.

## The Depth Baseline

**Odd-even transposition** — n phases of adjacent compare-exchanges, alternating
between starting at wire 0 and wire 1 — is also a valid sorting network, works
for any n, and needs only adjacent wires (so a linear chain of hardware
suffices). Its depth is n.

| n | bitonic size | bitonic depth | transposition size | transposition depth |
|---|---|---|---|---|
| 4 | 6 | 3 | 6 | 4 |
| 8 | 24 | 6 | 28 | 8 |
| 16 | 80 | 10 | 120 | 16 |
| 32 | 240 | 15 | 496 | 32 |
| 64 | 672 | 21 | 2016 | 64 |

At n = 64 bitonic is 3x smaller and 3x shallower, and the gap keeps widening —
`O(log^2 n)` against `O(n)`.

## Complexity

| Network | Size | Depth | Notes |
|---|---|---|---|
| **Batcher bitonic** | O(n log²n) | O(log²n) | this day; requires n = 2^k |
| Batcher odd-even merge | O(n log²n) | O(log²n) | ~half the comparators, messier to generate |
| Odd-even transposition | O(n²) | O(n) | any n; adjacent wires only |
| AKS network | O(n log n) | **O(log n)** | asymptotically optimal, constant ≈ 2000 — never used |
| Best known, n=16 | 60 comparators | 10 | found by search; no general construction |
| Information-theoretic floor | Ω(n log n) | Ω(log n) | `day-006/lower_bounds.py` derives the size floor |

AKS is the classic cautionary tale: provably optimal depth, and utterly useless,
because the hidden constant makes it slower than bitonic for any n that fits in
a data centre.

## Failure Modes

1. **n is not a power of two.** `bitonic_network` raises rather than silently
   producing a network that does not sort. Padding is the fix, and it costs: 33
   items need a 64-wire network — 672 comparators for 33 values.
2. **Padding with `max(values)`.** Looks fine until there are duplicates of the
   maximum, at which point the padding is indistinguishable from real data on
   the way out. Use a sentinel that compares greater than *everything*.
3. **Assuming stability.** Networks compare non-adjacent wires, so equal elements
   are freely reordered. Bitonic sort is **not stable**. Decorate with the
   original index if you need it — and note that this doubles the comparison cost.
4. **Trusting a hand-built network.** Drop exactly one comparator from the 8-wire
   network and it still sorts the vast majority of inputs; the demo finds the
   failing case at `(1,0,0,1,0,0,0,1)`. Random testing would very likely miss it.
   Run the 0-1 check.
5. **Applying a merge network to non-bitonic input.** `bitonic_merge_network` is
   correct *only* on bitonic sequences — it is not a sorting network, and the
   practice tests assert exactly that. Feeding it arbitrary data yields garbage
   with no error raised.
6. **Expecting it to beat a real sort in software.** It will not. It performs
   strictly more comparisons than Timsort, gains nothing from presorted input,
   and pays for padding. Choose it for the *properties* — obliviousness, fixed
   depth, no branches — never for raw single-threaded speed.
7. **Claiming "constant-time" without checking the comparator.** The schedule is
   oblivious, but if your *comparison* branches or short-circuits
   (variable-length strings, early-exit `memcmp`), the timing leak is back.
   Obliviousness has to hold all the way down.

## Checkpoint Questions

1. Define data-oblivious precisely. Which of days 99-103's sorts could be made
   oblivious, and what would each one lose?
2. Why is depth, not size, the figure of merit for a hardware sorter? Give a case
   where size is the one that matters instead.
3. State the 0-1 principle and reconstruct the monotone-function argument. Where
   exactly is monotonicity required?
4. A bitonic sequence of length n undergoes the half-length compare-exchange.
   Prove the low half is bitonic afterwards.
5. Derive `depth = log n (log n + 1) / 2` from the recursive structure.
6. How is the ascending/descending direction of each comparator chosen without a
   branch? Why does that matter for a GPU warp specifically?
7. You must sort 1000 items with a bitonic network. How many wires, how many
   comparators, and what fraction of that work is on padding?
8. AKS has O(log n) depth and is never used. What does that tell you about
   reading asymptotic bounds without their constants?
9. Your comparison function is `strcmp` on variable-length strings. Is your
   sorting-network-based sort still constant-time? Justify.
