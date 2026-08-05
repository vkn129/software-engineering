# Day 162: Consistent Hashing — Production Ring

## Why Revisit This?

Day-74 built the bare ring: `hash(key) % N` failed because adding a node
remapped every key. Consistent hashing fixed this — only `K/N` keys move.

But Day-74 skipped what makes consistent hashing actually work in
production:

1. **Virtual nodes (vnodes)** — without them, the ring is dangerously
   unbalanced. One physical node can own 50% of the keyspace by bad luck.
2. **Rebalancing** — what actually moves when a node joins/leaves?
3. **Replication & quorum** — N replicas, R reads, W writes.
4. **Heterogeneous capacity** — bigger nodes own more vnodes.

This is the algorithm running Cassandra, DynamoDB, Riak, BunnyCDN's edge
cache, and Discord's session router.

## The Problem with Plain Consistent Hashing

```
Ring with 3 nodes, hashed naively:
  A at position 0.10
  B at position 0.15
  C at position 0.80
```

A owns [0.80, 0.10] = 30%. B owns [0.10, 0.15] = 5%. C owns [0.15, 0.80] = 65%.

**B has 13x less load than C**. One bad hash and a node melts.

## Virtual Nodes Fix Balance

Each physical node owns V virtual positions on the ring. With V=150 per
node, variance drops by roughly sqrt(V).

```
Standard deviation of load ≈ 1/sqrt(V * N)
```

| vnodes | std dev (3 physical nodes) |
|--------|---------------------------|
| 1      | ~57%                      |
| 10     | ~18%                      |
| 100    | ~6%                       |
| 500    | ~2.5%                     |

Cassandra default: 256 vnodes per physical node.
DynamoDB: thousands of partitions, each acts like a vnode.

## What Moves When a Node Joins?

Add node D with V=100 vnodes. Each vnode steals a slice from whichever
node currently owns that ring position.

Total keys moved ≈ `1/(N+1)` of the keyspace. With N=10 nodes, adding
one moves ~9% of keys. Without consistent hashing, you'd move ~91%.

## What Moves When a Node Leaves?

D's 100 vnodes each "die." The next vnode clockwise inherits each slice.
Total keys moved ≈ `1/N` of the keyspace.

**Failure modes**:
- If D leaves uncleanly (crash), in-flight writes during the rebalance
  window can land on the wrong node → temporary inconsistency until
  hinted handoff or anti-entropy repair catches up.
- If D's successor is also unhealthy, double-failure cascades.

## Replication on the Ring

For key K hashed to position P, write to the next R distinct physical
nodes clockwise from P. This gives R replicas without a separate
placement table.

**Pitfall**: with vnodes, two adjacent vnodes might belong to the same
physical node. You must skip duplicates → walk until you find R distinct
physical nodes.

## Heterogeneous Capacity

A 32-core box can hold more than a 4-core box. Give it 8x more vnodes:

```
node_vnodes = base_vnodes * (capacity_units)
```

Same algorithm, weighted distribution. This is how AWS handles mixed
instance types in a partitioned service.

## Real Systems

| System | Variant |
|--------|---------|
| Cassandra | 256 vnodes/node, replication factor + LOCAL_QUORUM |
| DynamoDB | Hidden partitions, automatic split/merge |
| Riak | Fixed ring (default 64 partitions), claim algorithm for placement |
| Discord | Consistent hashing for session affinity to gateway nodes |
| BunnyCDN | Edge cache routing — `hash(URL)` picks the cache server |
| memcached (ketama) | Original consistent hashing client lib, 160 vnodes |

## Checkpoint Questions

1. Why does increasing vnodes reduce variance as `1/sqrt(V)`?
2. With R=3 replication, what's the minimum physical nodes needed for
   true durability under single-node failure?
3. What does "hinted handoff" do when a node is temporarily down?
4. Why might Cassandra use **256** vnodes but Riak use **64 partitions**?
   What tradeoff?
5. When you double a node's vnodes, does load shift smoothly or in jumps?
6. Sketch the consistency window during a vnode rebalance — when can a
   read miss?
