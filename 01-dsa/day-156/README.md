# Day 156: MapReduce — A Simulated Framework

## Why MapReduce Still Matters

The 2004 Dean & Ghemawat MapReduce paper is the foundational distributed-systems
paper of the 21st century. Spark, Flink, Hadoop, Beam, BigQuery, Snowflake —
every modern data system is either an evolution of MapReduce or a deliberate
rejection of it. You must understand the original before you can critique it.

MapReduce is not just an algorithm: it's a **shape** for problems.

> "If your computation can be expressed as map then reduce, you get fault tolerance,
> parallelism, and skew handling for free."

## The Model

Three user-supplied functions:

```
map:    (k1, v1) -> [(k2, v2), ...]
shuffle: group all values by k2 (framework-provided)
reduce: (k2, [v2, ...]) -> [(k3, v3), ...]
```

The framework guarantees:
1. Map runs in parallel across input splits.
2. All values for the same key reach the same reducer.
3. Failures are handled by re-execution (functions must be idempotent).

## Why It Works

The model is restrictive **on purpose**. Because map and reduce are
side-effect-free functions over disjoint data, the framework knows:

- **Re-execute on failure**: redoing map(x) is safe.
- **Speculative execution**: launch a duplicate of slow tasks, take whichever finishes first.
- **Data locality**: schedule map tasks on nodes holding the input.
- **Backpressure**: shuffle is a natural barrier.

The cost: every problem must squeeze through the (map, shuffle, reduce) shape.

## Word Count (the "hello world")

```
map(doc_id, text):
    for word in text.split():
        emit(word, 1)

reduce(word, counts):
    emit(word, sum(counts))
```

That's it. Run it on 100 GB of text across 1,000 machines — same code.

## Distributed Sort

The brilliant trick: MapReduce gives you sort for free.

```
map(_, record):
    emit(record.key, record)        # key is the sort key

reduce(key, records):
    for r in records:
        emit(key, r)
```

The shuffle phase groups by key. If the framework partitions keys
range-wise across reducers (instead of hash-wise), the output is globally sorted.

This is **TeraSort** — Google won the sort benchmark in 2008 with this.

## The Pieces of a Real Framework

| Component | Role | What we simulate |
|---|---|---|
| Input split | Chop input into chunks | List slicing |
| Map worker | Apply user `map` to a split | Thread per split |
| Combiner | Local reduce before shuffle | Optional — reduces shuffle traffic |
| Shuffle | Group by key across workers | Dict of key → list |
| Partitioner | Decide which reducer gets which key | `hash(k) % R` or range |
| Reduce worker | Apply user `reduce` per key | Thread per reducer |
| Master | Schedule, detect failures | Coordinator in our sim |

## Failure Model

The original paper's killer insight: at Google's scale, failures are the **common case**.
Out of 1,800 machines running a job, expect ~5 to fail per run.

Their answer: every task is **deterministic and idempotent**. If a worker dies,
the master simply re-schedules the task on another worker. The output is
identical because functions are pure.

We simulate this with a `fault_rate` parameter — workers randomly "die" mid-task,
and the master retries.

## Combiners — The Optimization

Word count emits `(the, 1)` billions of times. The shuffle is dominated by
network I/O. A **combiner** is a "mini-reduce" run on the mapper's output before
shuffle, replacing 10,000 `(the, 1)` pairs with `(the, 10000)`.

Combiners require the reduce operation to be **associative and commutative** —
exactly the conditions that make distributed computation safe.

## Skew

The pathological case: one key has 90% of the values. That reducer becomes
the bottleneck — straggler. Mitigations:
- Salt the key: `(word, random.randint(0, 16)) → partial sum → second reduce`
- Combiners: amortize at map side.
- Skew-aware partitioning: detect hot keys, route to multiple reducers.

## Beyond MapReduce

What MapReduce got wrong:
- Disk-based shuffle (replaced by Spark's in-memory)
- Always-batch (replaced by Flink streaming)
- Two-phase rigidity (replaced by DAG engines)

What MapReduce got right: **the functional shape**. Spark's `RDD.map().reduceByKey()`
is the same algebra.

## Checkpoint Questions

1. Why must map and reduce be deterministic? Give a non-deterministic example that breaks the framework.
2. When is a combiner NOT safe? Show a reduce operation where running the combiner changes the answer.
3. In distributed sort, why does hash-partitioning break global ordering but range-partitioning preserve it?
4. A reducer is 100x slower than the others. Name two distinct causes and one mitigation for each.
5. You have 10 TB of input, 100 workers, and a 10 Gb/s network. Estimate the shuffle time for word count. Does the combiner help? Quantify.
