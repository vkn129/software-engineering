# Day 159: Reservoir Sampling

## The Problem

You're processing a stream of items — log lines, tweets, sensor readings.
You don't know how many there will be. You want a **uniformly random sample**
of `k` items.

If you knew n in advance: shuffle, take first k. But you don't. You can't store
the whole stream — it might be terabytes. You get **one pass**, **O(k) memory**,
and you must produce a uniform sample.

This problem looks impossible. **Algorithm R** (Vitter, 1985) solves it in
six lines.

## Algorithm R (k items from unknown-length stream)

```
reservoir = first k items
for i = k+1, k+2, ...:
    pick j uniformly at random from [0, i)        # 0-indexed
    if j < k:
        reservoir[j] = stream[i]
```

That's it. Process each item with O(1) work; storage is exactly k.

## Why It's Uniform — The Proof

We prove by induction on i (stream length seen so far) that **every item seen
has probability exactly k/i of being in the reservoir**.

**Base case**: After i = k, all k items are in the reservoir. Probability = k/k = 1. ✓

**Inductive step**: Suppose true after seeing i items. Consider item i+1.

- **Probability item i+1 enters the reservoir** = k/(i+1) (we pick j in [0, i+1), keep if j < k).
- **Probability item i+1 ends up in reservoir** = k/(i+1). ✓
- **Probability an existing item x stays**:
  - x was in reservoir with probability k/i (inductive hypothesis)
  - Given x is in reservoir at slot s ∈ [0, k):
    - P(item i+1 replaces slot s) = (k/(i+1)) × (1/k) = 1/(i+1)
    - P(x stays at slot s) = 1 - 1/(i+1) = i/(i+1)
  - Total: (k/i) × (i/(i+1)) = k/(i+1). ✓

After seeing n items total, each is in the reservoir with probability k/n.
This is the definition of a **simple random sample without replacement**.

## Variants

### Algorithm A (k=1)

For sampling a single item: keep current with probability 1/i at step i.
This is the elegant special case used in randomized algorithms (e.g., picking
a random pivot in a streaming context).

### Algorithm L (Vitter, 1985) — Faster

For k items: instead of generating a random number per element, **skip ahead**
geometrically. Average work per item is O(1) but with a much smaller constant.

Probability that no items in the next `m` are selected = `((i)(i+1)...(i+m-1)) / ((i+k)(i+k+1)...(i+k+m-1))`.
You can sample `m` from this distribution and skip directly.

### Weighted Reservoir Sampling (Chao 1982, Efraimidis-Spirakis 2006)

If items have weights w_i, you want item i in sample with probability proportional
to w_i (in Efraimidis-Spirakis, the simplest formulation):

```
for each item i with weight w_i:
    key_i = U_i^(1/w_i)    where U_i ~ Uniform(0,1)
keep the k items with the largest keys (via min-heap of size k)
```

### Distributed Reservoir Sampling

Each worker samples k items from its shard, then a coordinator samples k from
the union. Adjust weights: each worker reports (sample, items_seen_locally).
Coordinator uses weighted sampling.

This is exactly how BigQuery's `APPROX_TOP_COUNT` runs across nodes.

## When You Use It

| System | Use case |
|---|---|
| **Postgres ANALYZE** | Sample rows for table statistics |
| **BigQuery** | Approximate aggregations on huge tables |
| **Apache Kafka Streams** | Random sampling of stream for monitoring |
| **A/B testing infra** | Random subsample of events for analysis |
| **Twitter Streaming API** | The "Sample API" (1%) is reservoir-based across servers |
| **Database backup tools** | Sample rows to estimate dump size |

## Failure Modes

1. **Bad RNG**: if `random.randint(0, i)` is biased, the sample is biased. Use a CSPRNG for security-sensitive sampling.
2. **Non-independent streams**: if items arrive in correlated batches, you still get a uniform sample over the **stream** — but the stream itself might not represent the population.
3. **Late-arriving items**: classic reservoir assumes monotonic stream. If items arrive late, they may be missed.
4. **Reservoir contention** in distributed implementations: many workers writing to one reservoir → locking. Use shard-then-merge.

## Connection to Day 157

Reservoir sampling is a **Las Vegas algorithm** — always returns a valid sample.
The randomness is in *which* sample you get, not *whether* you get one.

The single-element case (k=1) is the cleanest example of "you don't need to
know n to be uniform on n elements."

## Checkpoint Questions

1. Prove that with k=1, the probability of returning element i (1-indexed) after seeing n items is exactly 1/n.
2. You're sampling 1000 items from a stream. Halfway through (after 50 million items), how much "churn" has happened — how often is the reservoir being modified?
3. Adapt Algorithm R to sample WITH replacement of size k. Hint: k independent reservoirs of size 1.
4. Why does weighted reservoir sampling use a min-heap and not random selection per item?
5. The reservoir contains a uniform sample of the *items seen so far*. What does that NOT guarantee about the population that generated the stream?
