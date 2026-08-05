# Day 168: Mini-Project — Durable Key-Value Store

## What We're Building

A real KV store that ties the week together:

- **WAL** (Day 166) for crash-recoverable durability.
- **Memtable** (Day 165) for fast in-memory writes.
- **SSTable + compaction** (Day 165) for sorted, durable, write-amplified
  long-term storage.
- **Tombstones** for deletes.
- **Crash recovery**: kill the process mid-stream, reopen, no data loss
  for committed writes.

This is the structural core of LevelDB, RocksDB, Cassandra (per-node),
and ScyllaDB. We're skipping bloom filters, block compression, and
multi-level compaction — focus is correctness across crash.

## Architecture

```
  put(k, v)
     |
     v
  [ WAL.append; fsync ]          <-- durable here
     |
     v
  [ memtable: dict ]              <-- in-memory, fast reads
     |  when full:
     v
  [ flush -> SSTable on disk ]    <-- immutable, sorted
     |  when too many L0 files:
     v
  [ compaction -> merged SSTable ]

  get(k):
     memtable -> L0 (newest->oldest) -> L1
```

## Crash Recovery Story

When `open(path)`:
1. List all SSTable files. Sort by generation. These contain everything
   that was flushed before the crash.
2. Open the WAL. Replay every record into a fresh memtable. These are
   writes that were durable but not yet flushed.
3. Database is now equivalent to its state just before the crash.

**Loss boundary**: a put returns only after WAL fsync. Anything ack'd to
the user survives. Anything mid-stream that hasn't reached fsync is lost
— this is the expected contract.

## What Could Go Wrong (and Tests for Each)

1. **Crash before WAL fsync**: write not visible after restart. OK.
2. **Crash after WAL fsync, before flush**: WAL replay restores memtable.
3. **Crash mid-flush**: incomplete SSTable file. We use a temp-then-rename
   strategy so a half-written SSTable never has the canonical name.
4. **Crash mid-compaction**: same temp-then-rename. Old SSTables remain
   until the new one is durably written, then atomically swapped in.
5. **Torn WAL tail**: replay skips malformed records (Day 166).

## Why Compaction Has to Be Crash-Safe

The naive bad version: read N SSTables, write to "merged.sst" in place,
delete the originals. If you crash midway, you have a corrupt
"merged.sst" file AND no originals. Data loss.

The safe version:
- Write to `merged.sst.tmp`
- fsync the tmp file
- Atomic rename to `merged.sst`
- fsync the directory (Linux only)
- Then delete originals

POSIX guarantees rename is atomic within a filesystem. So after a crash
you either see the new merged file or the old originals, never partial.

## Comparison to Real Systems

| Concept | Our impl | Production (RocksDB) |
|---------|----------|----------------------|
| WAL | newline JSON | length-prefixed binary, CRC32 |
| Memtable | dict | skip list, lock-free |
| SSTable | JSON list | binary, block compressed, bloom filter |
| Compaction | merge all L0 + L1 | tiered or leveled, multi-threaded |
| Index per SSTable | min/max + binary scan | per-block index, footer with metadata |

The architecture is otherwise the same.

## Checkpoint Questions

1. Why must the WAL be fsync'd before `put()` returns?
2. Why is `temp file + rename` safer than `truncate + write` for SSTable
   flushes?
3. What state does the WAL hold after a successful flush? When is it
   safe to delete?
4. Sketch a sequence of operations and the on-disk state after a crash
   at each step.
5. Why is the recovery flow correct even with concurrent writes at the
   moment of crash (assuming our single-writer simplification)?
6. What's the simplest extension to support point-in-time recovery?
