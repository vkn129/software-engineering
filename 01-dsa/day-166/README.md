# Day 166: Write-Ahead Log (WAL)

## The Problem WAL Solves

A database wants two things that fight each other:

1. **Durability**: an acknowledged write must survive a crash.
2. **Performance**: don't fsync after every byte; the disk is slow.

Naïve solution: write straight to the data files. But:
- Multiple pages may need updates per transaction. A crash midway leaves
  the data files in an inconsistent state.
- fsync per write = 100s of microseconds. Throughput tanks.

**WAL**: append every change to a sequential log first. Once the log
entry is durable (fsync'd), the transaction is **logically committed**,
even though the actual data files have not been updated yet.

This is the single most important durability primitive in databases.

## How WAL Works

```
Client commits txn:
  1. Append (txn_id, "BEGIN") to WAL
  2. Append (txn_id, op1, op2, ...) to WAL
  3. Append (txn_id, "COMMIT") to WAL
  4. fsync(WAL)           <-- commit point
  5. Acknowledge client
  6. (Asynchronously) apply changes to data pages
```

Crash between 4 and 6: **recovery replays** the WAL on restart. Every
COMMIT-tagged transaction is re-applied. Uncommitted (no COMMIT marker)
is discarded.

## Checkpoints

Replaying the entire WAL from disk birth is impractical. **Checkpoint**
periodically: flush all dirty data pages to disk, then mark a position
in the WAL — "everything before this is already on disk."

On recovery, only replay from the last checkpoint. Old WAL segments can
be deleted (or archived for point-in-time recovery).

```
WAL:  ----checkpoint_lsn_42---- entry43 ---- entry44 ---- crash ----
                                ^^^^^^^^^^^^^^^^^^^^^^^^
                                only replay this region
```

## Sequential I/O Wins

Appending to one file is **sequential**. Modern NVMe: ~3 GB/s sequential
write, ~700 K random IOPS but only on small ops. WAL aligns with the
disk's strong axis.

This is exactly why LSM trees (Day 165) also rely on a WAL: any in-memory
write must be in the WAL before the memtable acknowledges. The same
sequential-write trick powers both.

## Group Commit

fsync is expensive. **Group commit** batches multiple transactions'
COMMIT records and fsyncs once. Per-txn latency stays modest, throughput
multiplies.

Postgres: `commit_delay` / `commit_siblings` knobs.
MySQL: `innodb_flush_log_at_trx_commit = 1` (durable) vs `2` (fsync per second).

## Failure Modes

1. **fsync lies**: some consumer disks ack fsync but only push to a
   volatile cache. Power loss = data gone. Postgres added `wal_sync_method
   = fdatasync` vs `open_datasync` vs `pwritev` to fight this; ZFS / btrfs
   bypass with their own integrity layers.

2. **Torn writes**: WAL entry is partially written (one disk sector OK,
   next sector zero). Postgres uses full-page writes after checkpoint;
   InnoDB uses double-write buffer; both pay a write-amp tax for this.

3. **Disk full**: WAL append fails. Database stops accepting writes
   (good — beats data loss). Operationally: monitor WAL disk usage
   separately from data disk.

4. **Replay loop**: a malformed entry causes recovery to crash. On
   restart, recovery hits the same entry. Postgres: `pg_resetwal` (very
   destructive). MySQL: `innodb_force_recovery` levels 1-6 with
   progressively more aggressive truncation.

## Real Systems

| System | WAL impl |
|--------|---------|
| **PostgreSQL** | `pg_wal/` directory, 16 MB segments, archived for PITR |
| **MySQL / InnoDB** | redo log (`ib_logfile0/1`), circular, ~512 MB by default |
| **SQLite** | `journal_mode=WAL`, separate `-wal` file |
| **RocksDB / LevelDB** | per-column-family WAL; pairs with memtable |
| **Kafka** | partition log *is* the WAL; consumers tail it |
| **Cassandra** | commitlog/, segments rotated and replayed |
| **etcd / Raft logs** | the consensus log doubles as the WAL |

## Why Kafka Looks Like a WAL

Kafka was literally inspired by database commitlogs. A partition is an
append-only log; consumers replay from a checkpoint (their committed
offset). The same primitive scaled out as a network service.

## Checkpoint Questions

1. Why is appending to one file faster than updating many pages?
2. What does fsync actually do? Why is it slow?
3. Sketch the recovery procedure step by step.
4. Why must the COMMIT marker be the *last* thing fsync'd for a txn?
5. Explain how a torn write corrupts the WAL, and one mitigation.
6. Group commit improves throughput. Does it improve or hurt per-txn
   latency? Why?
