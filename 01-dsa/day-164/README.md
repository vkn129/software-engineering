# Day 164: CRDTs — Conflict-Free Replicated Data Types

## Why CRDTs Exist

CAP theorem forces a choice during a partition: **C**onsistency or
**A**vailability. CRDTs pick **A** and recover **eventual** C — without
coordination, conflicts, or vector-clock merge arbitration.

The trick: design data types whose merge function is **associative,
commutative, and idempotent (ACI)**. Any node can apply updates in any
order, any number of times, and the final state converges.

```
merge(a, b) = merge(b, a)              (commutative)
merge(merge(a, b), c) = merge(a, merge(b, c))   (associative)
merge(a, a) = a                         (idempotent)
```

This is called a **join semilattice**. Convergence is mathematical, not
"hopeful."

## Two Flavors

1. **State-based (CvRDT)** — replicas exchange full state; merge picks
   the join (least upper bound). Robust to message loss and reordering.
2. **Operation-based (CmRDT)** — replicas exchange operations; each op
   must be commutative. Smaller messages but needs causal delivery.

We focus on state-based here — easier to reason about.

## G-Counter (Grow-Only Counter)

Every replica owns its own slot in a vector of counts. Increment only
your own slot. Value = sum across all slots. Merge = element-wise max.

```
A: [3, 0, 0]   B: [0, 2, 0]   C: [0, 0, 5]
merge(A, B, C) = [3, 2, 5]   value = 10
```

Application: distributed view counters, like counts.

**Cannot** decrement. Subtracting would break the lattice (max is no
longer the join).

## PN-Counter (Positive-Negative)

Two G-counters: one for increments, one for decrements. Value = P - N.

```
P = [5, 3]   N = [1, 0]   value = 8 - 1 = 7
```

Application: shopping cart quantities, social-media likes that can be
unliked.

## LWW-Register (Last-Write-Wins)

Store (value, timestamp). On merge, keep the one with the larger
timestamp. Tie-break by replica id.

Application: user profile fields, DNS records, single-value config.

**Failure mode**: clock skew. If replica A's clock is 5 minutes ahead,
its writes silently overwrite legitimate later writes from B. Mitigations:
- Hybrid logical clocks (HLC): physical time + counter
- Cassandra: client-supplied timestamp, hope NTP is good enough
- DynamoDB Global Tables: server-side timestamp, same hope

## Why It Works Under Partition

Split A,B,C. Network breaks A from {B,C}.
- A increments its counter slot.
- B and C also increment theirs.

When network heals, all three exchange state. Element-wise max gives the
correct sum. No coordination needed during the partition.

Compare to a coordinated system: during partition, either some side is
unavailable (CP system) or you accept divergence with manual conflict
resolution.

## Real Systems

| System | CRDT use |
|--------|----------|
| **Redis (enterprise)** | CRDT data types for active-active geo-distribution |
| **Riak** | First-class CRDT support (G-Counter, OR-Set, LWW-Register, Map) |
| **Figma, Linear, Notion** | OT or CRDT for real-time collaborative editing |
| **Apple Notes (sync)** | CRDT-style merge across devices, offline tolerant |
| **Automerge / Yjs** | JS libraries powering most collaborative apps |
| **CouchDB / PouchDB** | LWW-Register semantics across syncing peers |

## What CRDTs Don't Solve

- **Uniqueness invariants**: "no two users with the same email." CRDTs
  cannot enforce this without coordination.
- **Inventory constraints**: "do not oversell." A G-Counter doesn't know
  the upper bound.
- **Transactional updates**: "transfer $10 from A to B atomically." Not
  expressible as a single ACI merge.

CRDTs are perfect for **commutative semantic domains** (counters, sets,
text). They are wrong for **invariant-protecting** domains.

## Checkpoint Questions

1. Prove G-Counter merge is idempotent.
2. Why does PN-Counter need *two* G-Counters instead of allowing the
   single counter to decrement?
3. LWW-Register relies on monotonic timestamps. What goes wrong with NTP
   skew? Sketch a fix using HLC.
4. Why can't CRDTs enforce "max 100 items in stock"?
5. Compare CRDT and 2PC for a counter under partition: latency,
   availability, correctness.
6. What's the message complexity for state-based vs op-based with N
   replicas and M updates?
