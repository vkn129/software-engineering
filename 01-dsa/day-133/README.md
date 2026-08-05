# Day 133: Mini-Project — Online vs Offline, Belady's Optimum & Competitive Ratio

## What We're Building

A measuring instrument, not a cache. The question is not "which eviction
policy wins" — it is **how much does not knowing the future cost you, and can
that cost be bounded?**

- **Belady's MIN** — the optimal *offline* paging algorithm. Sees the whole
  request sequence, evicts the page needed farthest in the future.
- **FIFO** — an *online* algorithm, defined here because it is the vehicle for
  Belady's **anomaly**.
- **LRU** — the other online algorithm. It already exists in **day-070**
  (`cache.py`), so this project **imports** it and measures it. Rewriting it
  would prove nothing.
- **An exhaustive referee** — brute-force search over every eviction choice,
  to demonstrate that Belady's greedy rule really is optimal rather than
  merely reasonable.
- **Competitive-ratio machinery** — the ratio itself, the Sleator-Tarjan
  `k`-competitive bound, and the adversarial sequence that shows the bound
  is tight.

## The Distinction This Day Exists For

> **Offline algorithm** — gets the entire input before deciding anything.
> **Online algorithm** — must commit to each decision before seeing the next
> input, and can never take it back.

Almost everything the curriculum has covered so far is offline: sort an array
you already have, shortest path in a graph you already have. Real systems are
mostly the other kind. A cache does not know tomorrow's requests. A scheduler
does not know what jobs arrive next. A router does not know the next packet.

The offline optimum is not a competitor. It is a **yardstick** — the score
you would get with perfect foresight, so the gap is exactly the price of
ignorance and nothing else.

## Belady's MIN

```
on a request for page p:
    if p is cached:        hit
    else:                  fault
        if cache is full:  evict the page whose NEXT USE is farthest ahead
                           (never used again = infinitely far)
        insert p
```

**Why farthest-future is optimal** (exchange argument): take any optimal
algorithm `OPT` that at some fault evicts `x` while Belady evicts `y`, where
`y`'s next use is farther away than `x`'s. Build `OPT'` that evicts `y`
instead and otherwise mimics `OPT`. The two caches now differ in exactly one
page. Every request until `x`'s next use is handled identically; at that
point `OPT'` has `x` and does not fault where `OPT` does, and `OPT'` can
restore agreement by evicting `y` on its own next fault. `OPT'` faults no
more than `OPT`. Repeat, and every eviction becomes Belady's, without ever
increasing the fault count.

This is the same shape as every optimality proof in the greedy family: show
that any other choice can be swapped for the greedy one **without loss**.

Belady's rule is unimplementable in production — that is not a defect, it is
the definition. It is measured against, never shipped.

## Competitive Ratio

> An online algorithm `A` is **c-competitive** if there is a constant `b` such
> that for *every* request sequence `s`:
> `A(s) <= c · OPT(s) + b`.

Three things to notice:

1. **Worst case over all sequences**, not average. One bad sequence sets the
   ratio.
2. **The additive `b` is essential.** Cold-start faults are unavoidable for
   any policy; without `b`, no algorithm is competitive at any `c` on short
   sequences.
3. **`OPT` is the offline optimum**, not another online algorithm. You are
   competing against an oracle.

**Sleator-Tarjan (1985)**: LRU and FIFO are both `k`-competitive with a cache
of `k` pages, and **no deterministic online paging algorithm is better than
`k`-competitive**. The bound is tight.

### The adversary argument (the lower-bound half)

Give the online algorithm a cache of `k` pages, and use `k + 1` distinct
pages. The adversary watches: whatever the algorithm evicts, request *that*
next.

- Online: faults on **every single request**, forever.
- Belady, knowing the cycle, evicts the page needed farthest ahead and faults
  roughly **once every `k` requests**.

Ratio → `k`. The adversary needs no cleverness, only the algorithm being
deterministic — which is exactly why randomisation helps: the randomised
MARKING algorithm is `2·H_k`-competitive (`H_k ≈ ln k`), an exponential
improvement, because the adversary can no longer predict the eviction.

## Belady's Anomaly — Different Thing, Same Surname

Two unrelated results carry the name. Keeping them apart is half the value of
this day.

| | Belady's MIN | Belady's anomaly |
|---|---|---|
| What it is | the optimal offline policy | FIFO faulting **more** with **more** memory |
| Applies to | the offline optimum | FIFO (and other non-stack policies) |
| Good news? | it is the yardstick | it is a bug in your intuition |

```
requests = 1 2 3 4 1 2 5 1 2 3 4 5

capacity   FIFO faults   Belady faults
   1            12             12
   2            12              9
   3             9              7
   4            10  <-- MORE!   6
   5             5              5
```

**Why FIFO can do this.** A **stack algorithm** has the property that its
cache with `k` frames is always a *subset* of its cache with `k+1` frames.
That containment forces faults to be non-increasing in capacity. LRU and
Belady's MIN are stack algorithms — LRU's cache is always the `k` most
recently used pages, and the `k` most recent are a subset of the `k+1` most
recent. FIFO's cache is "the last `k` *inserted*", and insertion order itself
changes when the capacity changes, so no containment holds and the guarantee
evaporates.

Practical consequence: you cannot benchmark FIFO at one cache size and
extrapolate. With a stack algorithm you can.

## Architecture

```
  requests (a list of page ids)
     |
     +--> belady_faults        offline optimum        <- the yardstick
     |       belady_trace      step-by-step story
     |
     +--> fifo_faults          online, non-stack      <- anomaly vehicle
     |
     +--> lru_faults           online, stack          <- IMPORTED from day-070
     |
     +--> optimal_faults_bruteforce                   <- referee for Belady
     |
     +--> competitive_ratio / satisfies_k_competitive
             cyclic_worst_case(k)                     <- the adversary
             find_anomaly / is_stack_algorithm
```

`load_lru_class()` imports `../day-070/cache.py` by file path (a directory
named `day-070` is not a legal module name). If day-070 is not there it
returns `None` and the demo says so rather than quietly substituting a
different cache — a missing baseline must never look like a measurement.

## Complexity

| Operation | Time | Space |
|---|---|---|
| `belady_faults` | O(n log n) — binary search per eviction candidate | O(n) |
| `fifo_faults` | O(n) | O(k) |
| `lru_faults` (day-070) | O(n) | O(k) |
| `optimal_faults_bruteforce` | exponential in distinct pages | memo table |
| `find_anomaly` | O(C · n) over capacities 1..C | O(k) |

Belady's `O(n log n)` comes from `bisect` into each page's occurrence list.
An `O(n log k)` heap version exists; it is not the lesson here.

## What Could Go Wrong (and the Test for Each)

1. **Belady is not actually optimal.** Compare with
   `optimal_faults_bruteforce` on short traces. A plausible-looking eviction
   rule that is subtly wrong fails only here.
2. **Faults counted on hits.** Faults must equal misses exactly; with a cache
   at least as large as the distinct-page count, faults must equal the number
   of distinct pages (compulsory misses and nothing more).
3. **Capacity 1 mis-handled.** With one frame, every request to a different
   page than the last is a fault. Easy to get wrong with an off-by-one on
   `len(cache) >= capacity`.
4. **`k`-competitive bound violated.** Check `online <= k*OPT + k` across
   random traces and capacities. Forgetting the `+ k` makes the check fail on
   short traces and look like an algorithm bug.
5. **Assuming more memory always helps.** `find_anomaly` must report a hit for
   FIFO on the sequence above, and `is_stack_algorithm` must be `True` for
   Belady and `False` for FIFO.
6. **Timing instead of counting.** Every assertion here is a fault count or a
   ratio. Wall-clock numbers are hardware, not algorithms, and belong nowhere
   near a correctness test.

## Checkpoint Questions

1. State the difference between offline and online in one sentence, without
   using the word "cache".
2. Give the exchange argument for Belady's optimality in your own words.
   Where exactly does "farthest next use" get used?
3. Why does the definition of `c`-competitive need the additive constant `b`?
   Construct a sequence that breaks the claim if you drop it.
4. Build the adversarial sequence for `k = 3` and count faults for FIFO and
   for Belady. What is the ratio, and what does it approach?
5. Randomised MARKING is `2·H_k`-competitive while every deterministic
   algorithm is stuck at `k`. What does randomness take away from the
   adversary?
6. Prove that LRU is a stack algorithm. Where does the same argument fail for
   FIFO?
7. You measure a production cache at 64 GB and want to predict the hit rate
   at 128 GB. What must be true of the eviction policy for the extrapolation
   to be sound?
8. Belady's MIN cannot be implemented. Name two ways real systems approximate
   the information it uses.
