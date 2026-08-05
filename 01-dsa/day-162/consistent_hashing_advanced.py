"""
Day 162: Consistent Hashing — Production Ring with Virtual Nodes

Day-74 had the toy version: one position per node. This adds:
  - V virtual positions per physical node (load balance)
  - Replication walk (R distinct physical nodes)
  - Weighted vnodes (heterogeneous capacity)
  - Rebalance measurement (what moves on join/leave)

Production references: Cassandra, DynamoDB, Riak, ketama.
"""

import hashlib
import bisect
import random
from collections import defaultdict


# ---------------------------------------------------------------------------
# Hash helper — md5 truncated to 32 bits (ketama style)
# ---------------------------------------------------------------------------

def _hash(key: str) -> int:
    h = hashlib.md5(key.encode()).digest()
    return int.from_bytes(h[:4], "big")


# ---------------------------------------------------------------------------
# Consistent Hash Ring with virtual nodes
# ---------------------------------------------------------------------------

class ConsistentHashRing:
    """
    Ring of 32-bit positions. Each physical node owns V virtual positions.
    Lookup walks clockwise to the next vnode.
    """

    def __init__(self, vnodes_per_node: int = 150):
        self.vnodes_per_node = vnodes_per_node
        self._ring = []                  # sorted ring positions
        self._pos_to_node = {}           # position -> physical node id
        self._node_vnodes = defaultdict(list)  # node -> [positions]

    def add_node(self, node: str, weight: int = 1) -> None:
        """Add a physical node with `weight * vnodes_per_node` vnodes."""
        if node in self._node_vnodes:
            return
        count = self.vnodes_per_node * weight
        for i in range(count):
            pos = _hash(f"{node}#{i}")
            # avoid the rare collision
            while pos in self._pos_to_node:
                pos = (pos + 1) & 0xFFFFFFFF
            bisect.insort(self._ring, pos)
            self._pos_to_node[pos] = node
            self._node_vnodes[node].append(pos)

    def remove_node(self, node: str) -> None:
        if node not in self._node_vnodes:
            return
        for pos in self._node_vnodes[node]:
            del self._pos_to_node[pos]
            # binary remove
            i = bisect.bisect_left(self._ring, pos)
            if i < len(self._ring) and self._ring[i] == pos:
                self._ring.pop(i)
        del self._node_vnodes[node]

    def get_node(self, key: str) -> str:
        """Primary node owning this key."""
        if not self._ring:
            raise RuntimeError("ring is empty")
        pos = _hash(key)
        i = bisect.bisect_right(self._ring, pos)
        if i == len(self._ring):
            i = 0
        return self._pos_to_node[self._ring[i]]

    def get_replicas(self, key: str, r: int) -> list:
        """First R distinct physical nodes clockwise from hash(key)."""
        if r > len(self._node_vnodes):
            raise ValueError("r exceeds physical node count")
        pos = _hash(key)
        i = bisect.bisect_right(self._ring, pos) % len(self._ring)
        seen = []
        steps = 0
        while len(seen) < r and steps < len(self._ring):
            node = self._pos_to_node[self._ring[i]]
            if node not in seen:
                seen.append(node)
            i = (i + 1) % len(self._ring)
            steps += 1
        return seen

    def load_distribution(self, keys) -> dict:
        """How many of `keys` land on each physical node."""
        counts = defaultdict(int)
        for k in keys:
            counts[self.get_node(k)] += 1
        return dict(counts)


# ---------------------------------------------------------------------------
# Rebalance measurement
# ---------------------------------------------------------------------------

def measure_rebalance(before: ConsistentHashRing,
                      after: ConsistentHashRing,
                      keys) -> float:
    """Fraction of keys whose owning node changed between rings."""
    moved = 0
    for k in keys:
        if before.get_node(k) != after.get_node(k):
            moved += 1
    return moved / len(keys)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_balance_vs_vnodes():
    print("=" * 60)
    print("DEMO 1: Load variance vs vnode count (5 physical nodes)")
    print("=" * 60)
    random.seed(7)
    keys = [f"key:{i}" for i in range(10_000)]
    nodes = [f"n{i}" for i in range(5)]

    for v in (1, 10, 100, 500):
        ring = ConsistentHashRing(vnodes_per_node=v)
        for n in nodes:
            ring.add_node(n)
        dist = ring.load_distribution(keys)
        loads = list(dist.values())
        mean = sum(loads) / len(loads)
        var = sum((x - mean) ** 2 for x in loads) / len(loads)
        std_pct = (var ** 0.5) / mean * 100
        print(f"  vnodes={v:<4} std-dev={std_pct:5.1f}%  loads={sorted(loads)}")


def demo_rebalance_on_join():
    print("\n" + "=" * 60)
    print("DEMO 2: Keys moved when one node joins")
    print("=" * 60)
    keys = [f"key:{i}" for i in range(10_000)]

    before = ConsistentHashRing(vnodes_per_node=150)
    for n in ("a", "b", "c", "d"):
        before.add_node(n)

    after = ConsistentHashRing(vnodes_per_node=150)
    for n in ("a", "b", "c", "d", "e"):
        after.add_node(n)

    moved = measure_rebalance(before, after, keys)
    print(f"  4 -> 5 nodes, moved {moved*100:.2f}% (ideal 1/5 = 20%)")


def demo_rebalance_on_leave():
    print("\n" + "=" * 60)
    print("DEMO 3: Keys moved when one node leaves")
    print("=" * 60)
    keys = [f"key:{i}" for i in range(10_000)]

    before = ConsistentHashRing(vnodes_per_node=150)
    for n in ("a", "b", "c", "d", "e"):
        before.add_node(n)

    after = ConsistentHashRing(vnodes_per_node=150)
    for n in ("a", "b", "c", "d", "e"):
        after.add_node(n)
    after.remove_node("c")

    moved = measure_rebalance(before, after, keys)
    print(f"  5 -> 4 nodes, moved {moved*100:.2f}% (ideal 1/5 = 20%)")


def demo_replicas():
    print("\n" + "=" * 60)
    print("DEMO 4: Replica placement (R=3)")
    print("=" * 60)
    ring = ConsistentHashRing(vnodes_per_node=150)
    for n in ("a", "b", "c", "d", "e"):
        ring.add_node(n)
    for k in ("user:42", "session:99", "cart:7"):
        print(f"  {k:<12} replicas={ring.get_replicas(k, 3)}")


def demo_weighted():
    print("\n" + "=" * 60)
    print("DEMO 5: Heterogeneous capacity (weighted vnodes)")
    print("=" * 60)
    keys = [f"key:{i}" for i in range(10_000)]
    ring = ConsistentHashRing(vnodes_per_node=100)
    ring.add_node("small", weight=1)   # 100 vnodes
    ring.add_node("med",   weight=2)   # 200 vnodes
    ring.add_node("big",   weight=4)   # 400 vnodes
    dist = ring.load_distribution(keys)
    total = sum(dist.values())
    for n, c in dist.items():
        print(f"  {n:<6} {c} keys ({c/total*100:.1f}%)")


if __name__ == "__main__":
    demo_balance_vs_vnodes()
    demo_rebalance_on_join()
    demo_rebalance_on_leave()
    demo_replicas()
    demo_weighted()
