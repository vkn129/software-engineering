# Day 165: LSM Trees — Write-Optimized Storage

## Why LSM Trees Exist

B-trees (Day 50) win reads: O(log n) seek, balanced fanout, predictable.
But every **write** has to find the right leaf page and update it
**in place**. On disk, that's a random write.

Random writes are the worst case for two storage realities:

1. **Spinning disks**: ~100 random IOPS. A B-tree under heavy write
   load saturates the disk on seeks, not throughput.
2. **SSDs**: in-place updates trigger read-modify-write of a whole NAND
   page (typically 4 KB or 16 KB), then erase of a much larger block
   (256 KB+) when the page is rewritten. Wear amplification.

LSM (Log-Structured Merge) trees turn random writes into **sequential
writes**. Hundreds of MB/s instead of MB/s.

## The Three-Layer Stack

```
   Writes ->  [Memtable]    (in-memory, sorted, e.g. skiplist)
                  |  flush when full
                  v
              [SSTable L0]  (immutable, sorted on disk)
              [SSTable L0]
              [SSTable L0]
                  |  compact
                  v
              [SSTable L1]  (larger, fewer files)
              ...
              [SSTable Ln]
```

1. **Memtable**: writes go here first. Sorted by key for fast lookup.
   Backed by a Write-Ahead Log (Day 166) for crash safety.
2. **SSTable** (Sorted String Table): when memtable fills, dump it to
   disk as an immutable file, keys in sorted order. Future memtable
   keeps accepting writes.
3. **Compaction**: periodically merge multiple SSTables into a larger
   one. Resolves duplicate keys (keep newest), drops tombstones.

## Reads

A read must check:
1. Memtable (newest)
2. L0 SSTables (newest to oldest)
3. L1, L2, ... SSTables (older)

**Cost**: O(levels * log(keys per level)). Without help, this means
checking many files per read.

**Bloom filters** per SSTable cut this dramatically: "is this key
*definitely not* in this SSTable?" → 99%+ of negative checks skip the
file entirely.

## Why It Beats B-Trees for Write-Heavy Workloads

| Metric | B-tree | LSM |
|--------|--------|-----|
| Sequential write throughput | low (random IO) | high (append) |
| Read latency (point query) | predictable O(log n) | variable, often multi-file |
| Space overhead | ~30% (filled to 70%) | depends on compaction strategy |
| Write amplification | 1-3x | 5-30x (compaction rewrites) |

Trade-off: LSM trees do **more total work** per byte written (compaction
rewrites the same data multiple times across levels), but they do it
**sequentially** when the disk is fast at sequential access.

## Compaction Strategies

1. **Tiered** (Cassandra default before 4.x): when N SSTables exist at
   level L, merge them all into level L+1. Good write throughput, larger
   space amplification (multiple copies during merge).

2. **Leveled** (RocksDB default, LevelDB): each level is N times larger
   than the previous. Each key appears at most once per level after
   compaction. Better read amp, more write amp.

3. **Time-Window** (Cassandra TWCS for time series): bucket SSTables by
   time. Old buckets never compact. Perfect for append-only timeseries.

## Real Systems

| System | Notes |
|--------|-------|
| **LevelDB** | Original LSM open-source impl, by Google. Leveled. |
| **RocksDB** | Facebook fork, multi-threaded compaction, ~everywhere now |
| **Cassandra** | Per-table compaction strategy choice |
| **ScyllaDB** | C++ Cassandra clone, fast LSM with thread-per-core |
| **HBase** | Hadoop's column store; HFile = SSTable |
| **InfluxDB v2** | TSM (Time-Structured Merge) — LSM variant for metrics |
| **MongoDB (WiredTiger)** | B-tree default, LSM option |

## Failure Modes

1. **Compaction can't keep up**: writes faster than compaction.
   L0 grows unbounded. Reads slow exponentially. Cassandra: "pending
   compactions backlog." Mitigation: throttle writes or scale up.

2. **Write stall on flush**: memtable is full but disk is still
   writing the previous flush. New writes block. RocksDB exposes this
   as `write_stall` and `write_stop`.

3. **Read amp under update-heavy load**: same key in 10 SSTables across
   levels. Bloom filters and per-SSTable indexes are mandatory.

4. **Tombstone garbage**: deletes are stored as tombstones until
   compaction can guarantee no older copy survives. Cassandra
   `gc_grace_seconds` defaults to 10 days — too short and you resurrect
   deletes after node downtime; too long and you accumulate junk.

## Checkpoint Questions

1. Why is "sequential write" 100-1000x faster than "random write" on
   spinning disks? Sketch the head-seek physics.
2. Compute write amplification for 5-level leveled compaction with 10x
   size ratio.
3. Why are SSTables immutable? What does immutability buy us?
4. How does a bloom filter false-positive affect correctness vs
   performance?
5. Why are tombstones necessary? What goes wrong without them?
6. Sketch the read path for a get(k) request in an LSM with 3 levels.
