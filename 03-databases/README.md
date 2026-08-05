# 03 — Databases from First Principles

Storage engines, transactions, query planning, concurrency, replication,
distributed transactions — built from scratch on top of Python's standard
library, then compared against PostgreSQL, MySQL InnoDB, SQLite, RocksDB,
LevelDB, and Cassandra.

The goal is not "use a database." The goal is to **be able to write one**
and explain every failure mode it can hit.

## Why Build This

A database is just a program that promises four things:

1. **Durability** — data survives `kill -9`, `power off`, `disk yanked`.
2. **Atomicity** — half-applied changes never become visible.
3. **Isolation** — concurrent users do not corrupt each other's view.
4. **Ordering** — operations have a defined, reproducible sequence.

A file system gives you almost none of these. Building a database is the
work of recovering each guarantee, layer by layer, from the raw block
device upward. Every "easy" SQL query is paying for thousands of lines of
recovery code, page latches, MVCC chains, and write-ahead logs.

## How To Use This Track

- Read the week's `README.md` before opening any code.
- Build each day's topic file from the spec in its `README.md`.
- Run `python practice.py` to validate — every exercise has a `_sol_*`
  reference implementation, but try yours first.
- Connect everything back to a real system: PostgreSQL, InnoDB, SQLite,
  RocksDB, LevelDB, Cassandra, FoundationDB, Spanner.
- Always ask: **what breaks if power dies right here?**

## 8-Week Curriculum

| Week | Topic | Real Systems |
|------|-------|--------------|
| **1** | Storage engines (heap, B-tree, LSM) | PostgreSQL, InnoDB, RocksDB |
| **2** | Indexes (secondary, covering, partial, bitmap, hash) | PostgreSQL, MySQL, Cassandra |
| **3** | Transactions & isolation levels | PostgreSQL MVCC, InnoDB UNDO |
| **4** | Query planning & optimization | PostgreSQL planner, SQLite VDBE |
| **5** | Concurrency control (2PL, MVCC, OCC) | PostgreSQL, FoundationDB, CockroachDB |
| **6** | Replication (sync, async, quorum, Raft) | PostgreSQL streaming, MongoDB, etcd |
| **7** | Distributed transactions (2PC, Saga, Calvin) | Spanner, FoundationDB, Calvin |
| **8** | NewSQL & NoSQL trade-offs (CAP, PACELC) | Cassandra, DynamoDB, CockroachDB |

### Week 1 — Storage Engines

How bytes hit disk and survive a crash. Heap files, slotted pages, B-trees
on simulated pages, LSM trees with memtable + SSTables + compaction.
Mini-project: pluggable KV API with B-tree and LSM backends.

### Week 2 — Indexes

Secondary indexes, covering indexes, partial indexes, bitmap indexes,
hash indexes. When indexes hurt (write amp on every update). PostgreSQL's
HOT updates and the visibility map.

### Week 3 — Transactions & Isolation

ACID, the 4 SQL isolation levels, the anomalies each one allows
(dirty read, non-repeatable read, phantom, write skew). Snapshot
isolation vs serializable. Why "READ COMMITTED" is everyone's default
and what it costs you.

### Week 4 — Query Planning

Parse → analyze → rewrite → plan → execute. Cost models. Join orderings
(nested loop, hash, merge). Cardinality estimation and why it goes wrong.
PostgreSQL's `EXPLAIN ANALYZE` decoded.

### Week 5 — Concurrency Control

Two-phase locking (2PL) — the textbook approach. MVCC — what every
production database actually uses. Optimistic concurrency control —
when contention is rare. Deadlocks: detect vs prevent.

### Week 6 — Replication

Single-leader streaming. Synchronous vs asynchronous trade-offs.
Quorum reads/writes (Dynamo-style). Raft from scratch — leader election,
log replication, snapshotting.

### Week 7 — Distributed Transactions

Two-phase commit (2PC) and why it blocks. Three-phase commit and why it
still has gaps. Sagas as an escape hatch. Calvin's deterministic ordering.
Spanner's TrueTime and external consistency.

### Week 8 — NewSQL & NoSQL Trade-offs

CAP is a lie (it's really PACELC). When you actually need a key-value
store (DynamoDB, Cassandra). When you actually need NewSQL (Spanner,
CockroachDB). When boring PostgreSQL wins.

## Directory Layout

```
03-databases/
├── README.md
├── week-01/    storage engines
├── week-02/    indexes
├── week-03/    transactions
├── week-04/    query planning
├── week-05/    concurrency control
├── week-06/    replication
├── week-07/    distributed transactions
└── week-08/    newsql vs nosql
```

Each week:
```
week-NN/
├── README.md          week overview + day plan
├── day-01/            topic intro, topic.py, practice.py
├── day-02/
├── day-03/
├── day-04/
├── day-05/
└── day-06/            mini-project tying the week together
```

## Failure-Mode Index

Every concept connects to a real failure mode. Some you will simulate
in code; some you will study via post-mortems.

- **Torn writes** — page half-written on power loss → checksums, FULL_PAGE_WRITES.
- **fsync lies** — disk cache says "done" but data is volatile → `O_DIRECT`, fsync of the WAL.
- **Crash mid-flush** — dirty pages in OS buffer never reached platter → WAL replay.
- **Lost updates** — two writers, last writer wins → locking or MVCC.
- **Phantom reads** — range query sees new rows mid-transaction → predicate locks, SSI.
- **Write skew** — two transactions each read disjoint sets and write the other → serializable only.
- **Split-brain** — two leaders simultaneously → quorum, fencing tokens.
- **Clock skew** — distributed timestamps go backward → HLC, TrueTime.

## What This Track Is Not

- Not a SQL tutorial. SQL is the surface; this is the engine.
- Not framework-shopping. ORMs do not appear here.
- Not benchmarks-of-the-month. Real databases are measured in years.

When you finish, "the database is slow" should become a precise question
about indexes, page cache, WAL contention, lock waits, or planner choice —
not a vague complaint.
