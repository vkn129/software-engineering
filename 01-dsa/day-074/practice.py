"""
Day 74 Practice: Consistent Hashing Exercises

5 exercises that build intuition for how consistent hashing behaves
under real-world conditions: redistribution, load balance, bounded load,
replication, and cache hit rates.

Run: python3 practice.py
"""

import hashlib
import bisect
import math
import random
from collections import defaultdict


# ---------------------------------------------------------------------------
# Shared utility: lightweight consistent hash ring
# ---------------------------------------------------------------------------

class HashRing:
    """Minimal consistent hash ring for exercises."""

    def __init__(self, vnodes=150):
        self.vnodes = vnodes
        self._sorted_positions = []
        self._pos_to_server = {}
        self._server_positions = defaultdict(list)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

    def add(self, server: str):
        for i in range(self.vnodes):
            pos = self._hash(f"{server}#vn{i}")
            if pos not in self._pos_to_server:
                bisect.insort(self._sorted_positions, pos)
                self._pos_to_server[pos] = server
                self._server_positions[server].append(pos)

    def remove(self, server: str):
        for pos in self._server_positions.get(server, []):
            idx = bisect.bisect_left(self._sorted_positions, pos)
            if idx < len(self._sorted_positions) and self._sorted_positions[idx] == pos:
                self._sorted_positions.pop(idx)
            self._pos_to_server.pop(pos, None)
        self._server_positions.pop(server, None)

    def get(self, key: str) -> str | None:
        if not self._sorted_positions:
            return None
        pos = self._hash(key)
        idx = bisect.bisect_right(self._sorted_positions, pos)
        if idx == len(self._sorted_positions):
            idx = 0
        return self._pos_to_server[self._sorted_positions[idx]]

    @property
    def servers(self):
        return list(self._server_positions.keys())


def naive_assign(key: str, n: int) -> int:
    """Naive hash-modulo assignment."""
    h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    return h % n


# ===========================================================================
# Exercise 1: Measure Key Redistribution
# ===========================================================================

def exercise_1():
    """
    Measure how many keys change assignment when servers are added/removed.

    Compare consistent hashing (few keys move) vs naive modulo (most move).
    """
    print("=" * 65)
    print("  Exercise 1: Key Redistribution Measurement")
    print("=" * 65)

    NUM_KEYS = 50_000
    keys = [f"obj-{i}" for i in range(NUM_KEYS)]
    servers = [f"node-{i}" for i in range(10)]

    # --- Consistent hashing: remove a server ---
    ring = HashRing(vnodes=150)
    for s in servers:
        ring.add(s)

    before = {k: ring.get(k) for k in keys}
    ring.remove("node-4")
    after_remove = {k: ring.get(k) for k in keys}

    moved_remove = sum(1 for k in keys if before[k] != after_remove[k])

    # --- Consistent hashing: add a server ---
    ring_add = HashRing(vnodes=150)
    for s in servers:
        ring_add.add(s)
    before_add = {k: ring_add.get(k) for k in keys}
    ring_add.add("node-10")
    after_add = {k: ring_add.get(k) for k in keys}

    moved_add = sum(1 for k in keys if before_add[k] != after_add[k])

    # --- Naive modulo ---
    naive_before = {k: naive_assign(k, 10) for k in keys}
    naive_after_remove = {k: naive_assign(k, 9) for k in keys}
    naive_after_add = {k: naive_assign(k, 11) for k in keys}

    naive_moved_remove = sum(1 for k in keys if naive_before[k] != naive_after_remove[k])
    naive_moved_add = sum(1 for k in keys if naive_before[k] != naive_after_add[k])

    print(f"\n  {NUM_KEYS} keys across {len(servers)} servers\n")
    print(f"  {'Scenario':<35} {'Consistent Hash':>16} {'Naive Modulo':>14}")
    print(f"  {'-' * 65}")
    print(f"  {'Remove 1 server (10 -> 9)':<35} "
          f"{moved_remove:>10} ({moved_remove/NUM_KEYS*100:.1f}%) "
          f"{naive_moved_remove:>8} ({naive_moved_remove/NUM_KEYS*100:.1f}%)")
    print(f"  {'Add 1 server (10 -> 11)':<35} "
          f"{moved_add:>10} ({moved_add/NUM_KEYS*100:.1f}%) "
          f"{naive_moved_add:>8} ({naive_moved_add/NUM_KEYS*100:.1f}%)")
    print(f"\n  Ideal redistribution for remove: {100/10:.1f}%")
    print(f"  Ideal redistribution for add:    {100/11:.1f}%")


# ===========================================================================
# Exercise 2: Load Balancing Quality
# ===========================================================================

def exercise_2():
    """
    Compare standard deviation of keys-per-server with different vnode counts.

    Shows that more virtual nodes -> better balance, with diminishing returns.
    """
    print(f"\n{'=' * 65}")
    print("  Exercise 2: Load Balancing Quality vs Virtual Node Count")
    print("=" * 65)

    NUM_KEYS = 100_000
    NUM_SERVERS = 8
    keys = [f"item-{i}" for i in range(NUM_KEYS)]
    servers = [f"srv-{i}" for i in range(NUM_SERVERS)]
    ideal = NUM_KEYS / NUM_SERVERS

    vnode_counts = [1, 5, 10, 25, 50, 100, 150, 300]

    print(f"\n  {NUM_KEYS} keys, {NUM_SERVERS} servers")
    print(f"  Ideal per server: {ideal:.0f}\n")
    print(f"  {'VNodes':>8} {'Std Dev':>10} {'CV %':>8} {'Min':>8} {'Max':>8} {'Max/Min':>9}")
    print(f"  {'-' * 55}")

    for vn in vnode_counts:
        ring = HashRing(vnodes=vn)
        for s in servers:
            ring.add(s)

        counts = defaultdict(int)
        for k in keys:
            counts[ring.get(k)] += 1

        values = [counts.get(s, 0) for s in servers]
        mean = sum(values) / len(values)
        std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
        cv = std / mean * 100
        mn, mx = min(values), max(values)
        ratio = mx / mn if mn > 0 else float("inf")

        print(f"  {vn:>8} {std:>10.0f} {cv:>7.1f}% {mn:>8} {mx:>8} {ratio:>8.2f}x")


# ===========================================================================
# Exercise 3: Bounded-Load Consistent Hashing
# ===========================================================================

def exercise_3():
    """
    Implement bounded-load consistent hashing (Google 2017 paper).

    Each server is capped at (1 + epsilon) * average_load. If the primary
    server is over capacity, the key walks clockwise to the next server
    that has room. This prevents hot spots.
    """
    print(f"\n{'=' * 65}")
    print("  Exercise 3: Bounded-Load Consistent Hashing")
    print("=" * 65)

    class BoundedLoadHashRing(HashRing):
        """
        Extends consistent hashing with a per-server load cap.

        When a server would exceed (1 + epsilon) * (total_keys / N),
        the key overflows to the next clockwise server with capacity.
        """

        def __init__(self, vnodes=150, epsilon=0.25):
            super().__init__(vnodes)
            self.epsilon = epsilon
            self._load = defaultdict(int)
            self._total_keys = 0

        @property
        def _capacity(self):
            """Max keys any single server can hold."""
            n = len(self._server_positions)
            if n == 0:
                return 0
            avg = self._total_keys / n
            # Cap = ceil((1 + eps) * avg), minimum 1 so empty ring works
            return max(1, math.ceil((1 + self.epsilon) * avg))

        def assign(self, key: str) -> str | None:
            """
            Assign key respecting bounded load.

            Walk clockwise from the key's hash position. Skip any server
            that has hit its capacity cap.
            """
            if not self._sorted_positions:
                return None

            pos = self._hash(key)
            idx = bisect.bisect_right(self._sorted_positions, pos)
            ring_len = len(self._sorted_positions)
            cap = self._capacity

            seen_servers = set()
            for i in range(ring_len):
                ring_pos = self._sorted_positions[(idx + i) % ring_len]
                server = self._pos_to_server[ring_pos]

                if server in seen_servers:
                    continue
                seen_servers.add(server)

                if self._load[server] < cap:
                    self._load[server] += 1
                    self._total_keys += 1
                    return server

            # All servers full (shouldn't happen if epsilon > 0 and keys < inf)
            # Fall back to the natural choice
            ring_pos = self._sorted_positions[idx % ring_len]
            server = self._pos_to_server[ring_pos]
            self._load[server] += 1
            self._total_keys += 1
            return server

        def reset_load(self):
            self._load.clear()
            self._total_keys = 0

    NUM_KEYS = 50_000
    NUM_SERVERS = 8
    keys = [f"req-{i}" for i in range(NUM_KEYS)]
    servers = [f"bounded-srv-{i}" for i in range(NUM_SERVERS)]
    ideal = NUM_KEYS / NUM_SERVERS

    for epsilon in [0.10, 0.25, 0.50]:
        ring = BoundedLoadHashRing(vnodes=150, epsilon=epsilon)
        for s in servers:
            ring.add(s)

        # Assign all keys
        assignment = {}
        for k in keys:
            assignment[k] = ring.assign(k)

        counts = defaultdict(int)
        for s in assignment.values():
            counts[s] += 1

        values = list(counts.values())
        mn, mx = min(values), max(values)
        cap = ring._capacity

        print(f"\n  epsilon={epsilon:.2f}  cap={cap}  "
              f"ideal={ideal:.0f}  min={mn}  max={mx}  "
              f"max/ideal={mx/ideal:.2f}x")

    # Compare to unbounded
    ring_ub = HashRing(vnodes=150)
    for s in servers:
        ring_ub.add(s)
    counts_ub = defaultdict(int)
    for k in keys:
        counts_ub[ring_ub.get(k)] += 1
    vals_ub = list(counts_ub.values())
    print(f"\n  Unbounded (for reference):     "
          f"min={min(vals_ub)}  max={max(vals_ub)}  "
          f"max/ideal={max(vals_ub)/ideal:.2f}x")


# ===========================================================================
# Exercise 4: Replication — N Consecutive Distinct Servers
# ===========================================================================

def exercise_4():
    """
    For each key, assign to N consecutive *distinct* physical servers on
    the ring. Verify that replicas always land on different machines.
    """
    print(f"\n{'=' * 65}")
    print("  Exercise 4: Replication Across Distinct Servers")
    print("=" * 65)

    ring = HashRing(vnodes=150)
    servers = [f"replica-node-{i}" for i in range(6)]
    for s in servers:
        ring.add(s)

    def get_replicas(ring: HashRing, key: str, n: int) -> list[str]:
        """Walk clockwise collecting n distinct physical servers."""
        if not ring._sorted_positions:
            return []
        n = min(n, len(ring._server_positions))

        pos = ring._hash(key)
        idx = bisect.bisect_right(ring._sorted_positions, pos)
        ring_len = len(ring._sorted_positions)

        result = []
        seen = set()
        for i in range(ring_len):
            rp = ring._sorted_positions[(idx + i) % ring_len]
            srv = ring._pos_to_server[rp]
            if srv not in seen:
                seen.add(srv)
                result.append(srv)
                if len(result) == n:
                    break
        return result

    REPLICA_COUNT = 3
    NUM_KEYS = 20

    print(f"\n  Replication factor: {REPLICA_COUNT}")
    print(f"  Servers: {len(servers)}\n")

    all_valid = True
    for i in range(NUM_KEYS):
        key = f"document-{i}"
        replicas = get_replicas(ring, key, REPLICA_COUNT)

        # Verify all distinct
        if len(replicas) != len(set(replicas)):
            print(f"  ERROR: duplicate servers for {key}: {replicas}")
            all_valid = False

        if i < 8:  # Print first 8 for readability
            print(f"  {key:<20} -> {replicas}")

    if NUM_KEYS > 8:
        print(f"  ... ({NUM_KEYS - 8} more keys)")

    print(f"\n  All {NUM_KEYS} keys have {REPLICA_COUNT} distinct replicas: "
          f"{'PASS' if all_valid else 'FAIL'}")

    # Show replica distribution — each server should hold roughly equal
    # share of primary + replica assignments
    replica_counts = defaultdict(int)
    for i in range(10_000):
        key = f"doc-{i}"
        for srv in get_replicas(ring, key, REPLICA_COUNT):
            replica_counts[srv] += 1

    print(f"\n  Replica load distribution (10K keys x {REPLICA_COUNT} replicas):")
    total_assignments = sum(replica_counts.values())
    for srv in sorted(replica_counts):
        print(f"    {srv:<25} {replica_counts[srv]:>6} "
              f"({replica_counts[srv]/total_assignments*100:.1f}%)")


# ===========================================================================
# Exercise 5: Cache Cluster Simulation
# ===========================================================================

def exercise_5():
    """
    Simulate a cache cluster with consistent hashing vs naive modulo.

    Measure cache hit rate during a server addition event:
    1. Warm up the cache with requests.
    2. Add a server.
    3. Send the same requests again.
    4. Compare hit rates: consistent hash should retain most cache entries,
       naive modulo loses almost everything.
    """
    print(f"\n{'=' * 65}")
    print("  Exercise 5: Cache Hit Rate — Consistent Hash vs Naive Modulo")
    print("=" * 65)

    NUM_KEYS = 20_000
    INITIAL_SERVERS = 5
    keys = [f"page-{i}" for i in range(NUM_KEYS)]

    # --- Consistent hashing cache ---
    ring = HashRing(vnodes=150)
    ch_servers = [f"cache-{i}" for i in range(INITIAL_SERVERS)]
    for s in ch_servers:
        ring.add(s)

    # Each server has its own cache (set of keys it has seen)
    ch_cache = defaultdict(set)

    # Warm up: all keys are fetched and cached on their assigned server
    for k in keys:
        server = ring.get(k)
        ch_cache[server].add(k)

    # Add a new server
    ring.add("cache-new")

    # Replay requests — a "hit" means the key is still on the same server
    ch_hits = 0
    for k in keys:
        server = ring.get(k)
        if k in ch_cache[server]:
            ch_hits += 1

    ch_hit_rate = ch_hits / NUM_KEYS * 100

    # --- Naive modulo cache ---
    naive_cache = defaultdict(set)

    # Warm up
    for k in keys:
        server_id = naive_assign(k, INITIAL_SERVERS)
        naive_cache[server_id].add(k)

    # Add a server (now N = INITIAL_SERVERS + 1)
    naive_hits = 0
    for k in keys:
        server_id = naive_assign(k, INITIAL_SERVERS + 1)
        if k in naive_cache[server_id]:
            naive_hits += 1

    naive_hit_rate = naive_hits / NUM_KEYS * 100

    print(f"\n  {NUM_KEYS} cached keys, {INITIAL_SERVERS} servers, then add 1 server\n")
    print(f"  {'Method':<25} {'Hits':>8} {'Hit Rate':>10}")
    print(f"  {'-' * 45}")
    print(f"  {'Consistent Hashing':<25} {ch_hits:>8} {ch_hit_rate:>9.1f}%")
    print(f"  {'Naive Modulo':<25} {naive_hits:>8} {naive_hit_rate:>9.1f}%")

    print(f"\n  Consistent hashing preserved {ch_hit_rate:.1f}% of cache entries.")
    print(f"  Naive modulo preserved only {naive_hit_rate:.1f}% — "
          f"a {ch_hit_rate - naive_hit_rate:.1f} percentage point advantage.")

    # --- Bonus: simulate repeated add/remove cycles ---
    print(f"\n  Simulating 5 add/remove cycles:")
    ring2 = HashRing(vnodes=150)
    stable_servers = [f"s-{i}" for i in range(8)]
    for s in stable_servers:
        ring2.add(s)

    cache2 = defaultdict(set)
    sample_keys = [f"k-{i}" for i in range(NUM_KEYS)]
    for k in sample_keys:
        cache2[ring2.get(k)].add(k)

    churn_servers = [f"churn-{i}" for i in range(5)]
    random.seed(42)

    for cycle, cs in enumerate(churn_servers):
        # Add a server
        ring2.add(cs)
        hits = sum(1 for k in sample_keys if k in cache2[ring2.get(k)])
        hit_rate = hits / NUM_KEYS * 100

        # Warm the new assignments into cache
        for k in sample_keys:
            cache2[ring2.get(k)].add(k)

        # Remove the server
        ring2.remove(cs)
        hits2 = sum(1 for k in sample_keys if k in cache2[ring2.get(k)])
        hit_rate2 = hits2 / NUM_KEYS * 100

        # Warm again
        for k in sample_keys:
            cache2[ring2.get(k)].add(k)

        print(f"    Cycle {cycle + 1}: after add={hit_rate:.1f}%, "
              f"after remove={hit_rate2:.1f}%")


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("\nDAY 74 PRACTICE: CONSISTENT HASHING EXERCISES")
    print("=" * 65)

    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()

    print(f"\n{'=' * 65}")
    print("  All exercises complete.")
    print(f"{'=' * 65}\n")


if __name__ == "__main__":
    main()
