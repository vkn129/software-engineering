# Day 74: Consistent Hashing

## Why Naive Hashing Fails for Distributed Caches

The simplest approach to distributing keys across N servers is `hash(key) % N`.
This works until N changes. When you add or remove a single server, the modulus
changes and **almost every key remaps to a different server**. For a cache
cluster, this means a near-total cache miss storm — every client suddenly asks
the backend for data that was already cached, just on the wrong server.

Concretely: with 5 servers holding 10K keys, adding a 6th server remaps roughly
80% of keys. Remove one and ~80% move again. This is catastrophic at scale —
imagine invalidating millions of cache entries because one machine rebooted.

## Consistent Hashing: The Hash Ring

Consistent hashing solves this by placing servers on a **hash ring** spanning
`[0, 2^32)`. Each server is hashed to a position on the ring. To find which
server owns a key:

1. Hash the key to a position on the ring.
2. Walk clockwise until you hit a server.
3. That server owns the key.

### What happens when servers change?

- **Adding a server**: it lands between two existing servers on the ring. Only
  keys between the new server and its counter-clockwise predecessor move to the
  new server. Everything else stays put.
- **Removing a server**: only its keys move to the next clockwise server.

In both cases, only **O(1/N)** of all keys are affected — roughly 1/N of the
total, not nearly all of them. This is the fundamental improvement.

## The Imbalance Problem and Virtual Nodes

With only a few physical servers, their hash positions may cluster on one part of
the ring, leaving large arcs assigned to a single server. The distribution is
uneven.

**Virtual nodes** fix this: instead of one point per server, each server gets
**V points** (virtual nodes) spread around the ring. When a key maps to a virtual
node, it routes to that virtual node's real server.

- With V=1 (no virtual nodes), standard deviation of load is very high.
- With **V=150**, load variance drops dramatically — each server holds close to
  `total_keys / N` keys.
- Trade-off: more virtual nodes means more memory for the ring and slightly
  slower lookups (more entries to binary search through), but this is negligible
  in practice.

## Real-World Usage

| System | How it uses consistent hashing |
|--------|-------------------------------|
| **Amazon DynamoDB** | The original Dynamo paper (2007) popularized consistent hashing for partitioning key-value data across a cluster of nodes. Virtual nodes handle heterogeneous hardware. |
| **Apache Cassandra** | Uses consistent hashing (with virtual nodes called "vnodes") to assign partition ranges to nodes in the ring. Default vnode count is 256. |
| **CDN Routing** | Akamai and others use consistent hashing to map content URLs to edge servers. Adding a new edge server only redirects a fraction of requests. |
| **Redis Cluster** | Uses 16384 hash slots (a form of consistent hashing) distributed across nodes. Adding a node transfers a subset of slots. |

## Complexity

| Operation | Time | Why |
|-----------|------|-----|
| `add_node` | O(V log(NV)) | Insert V virtual nodes into sorted ring |
| `remove_node` | O(V log(NV)) | Remove V virtual nodes from sorted ring |
| `get_node` (lookup) | O(log(NV)) | Binary search on sorted ring positions |

Where N = number of physical servers, V = virtual nodes per server.

## Checkpoint Questions

1. **Why does `hash(key) % N` cause massive redistribution when N changes?**
   Because changing the divisor shifts the remainder for nearly every input.
   Mathematically, `hash(key) % 5` and `hash(key) % 6` produce the same result
   only for keys where both remainders happen to coincide — roughly 1/N of them.

2. **How does consistent hashing limit key movement to O(1/N)?**
   Keys are pinned to ring positions, not to a modulus. When a server is added,
   it only "steals" keys from the arc between itself and the previous server.
   That arc is on average 1/N of the ring.

3. **Why are virtual nodes necessary, and what is the trade-off?**
   Few physical nodes produce uneven arc lengths on the ring. Virtual nodes
   spread each server across many points, smoothing the distribution. The
   trade-off is increased memory for ring entries and marginally slower lookups.

4. **How does consistent hashing support replication?**
   For each key, walk clockwise past the primary server and assign replicas to
   the next K distinct physical servers on the ring. This ensures replicas land
   on different machines.

5. **What is bounded-load consistent hashing and when do you need it?**
   Google's 2017 paper caps each server at `(1 + epsilon) * average_load`.
   If the clockwise server is over-capacity, the key continues clockwise to the
   next eligible server. This prevents hot-spot servers while preserving the
   minimal-disruption property.

6. **In Redis Cluster's 16384-slot design, how does slot migration differ from
   pure consistent hashing?**
   Redis uses a fixed slot count (not a continuous ring). Migration moves entire
   slots between nodes. This is simpler to implement and reason about, but less
   granular than virtual-node consistent hashing. The fixed slot count limits
   the cluster to ~16K effective partitions.
