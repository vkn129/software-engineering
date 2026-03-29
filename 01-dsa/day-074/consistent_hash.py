"""
Day 74: Consistent Hashing

A hash ring that maps keys to servers with minimal disruption when
servers are added or removed. Uses virtual nodes for even distribution
and bisect for O(log N) lookups.
"""

import hashlib
import bisect
from collections import defaultdict


class ConsistentHashRing:
    """
    Consistent hash ring with configurable virtual nodes per server.

    Each physical server is mapped to `num_vnodes` positions on a
    [0, 2^32) ring. Keys are assigned to the nearest server clockwise.
    """

    def __init__(self, num_vnodes=150):
        # Why 150? Empirically gives <10% standard deviation in load
        # across servers. Fewer vnodes = cheaper memory but worse balance.
        self.num_vnodes = num_vnodes

        # Sorted list of ring positions — enables O(log n) bisect lookup
        self._ring_positions = []

        # Maps ring position -> physical server name
        self._position_to_server = {}

        # Tracks which positions belong to each server (for removal)
        self._server_to_positions = defaultdict(list)

    def _hash(self, key: str) -> int:
        """
        Hash a string to a 32-bit integer position on the ring.

        We use MD5 (not for security — for uniform distribution).
        SHA-256 would also work but MD5 is faster and collision
        resistance doesn't matter here.
        """
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(digest[:8], 16)  # First 32 bits

    def add_node(self, server: str) -> None:
        """
        Add a physical server with `num_vnodes` virtual nodes on the ring.

        Each virtual node is hashed from "server#i" to spread positions
        uniformly. O(V * log(NV)) due to V sorted insertions.
        """
        for i in range(self.num_vnodes):
            # The virtual node key must be deterministic and unique
            vnode_key = f"{server}#vn{i}"
            pos = self._hash(vnode_key)

            # Avoid collisions — extremely rare with 32-bit space but
            # worth guarding against in production code
            if pos in self._position_to_server:
                continue

            bisect.insort(self._ring_positions, pos)
            self._position_to_server[pos] = server
            self._server_to_positions[server].append(pos)

    def remove_node(self, server: str) -> None:
        """
        Remove a physical server and all its virtual nodes from the ring.

        Keys that were on this server will fall through clockwise to the
        next server — only those keys move. O(V * log(NV)).
        """
        if server not in self._server_to_positions:
            return

        for pos in self._server_to_positions[server]:
            # Remove from sorted ring — find index via bisect, then pop
            idx = bisect.bisect_left(self._ring_positions, pos)
            if idx < len(self._ring_positions) and self._ring_positions[idx] == pos:
                self._ring_positions.pop(idx)
            del self._position_to_server[pos]

        del self._server_to_positions[server]

    def get_node(self, key: str) -> str | None:
        """
        Find which server owns a key.

        Hash the key, then walk clockwise (bisect right) to find the
        next server position. Wrap around if we pass the end of the ring.
        O(log(NV)) via binary search.
        """
        if not self._ring_positions:
            return None

        pos = self._hash(key)
        # bisect_right gives us the insertion point — the first ring
        # position >= our key's position (i.e., next clockwise server)
        idx = bisect.bisect_right(self._ring_positions, pos)

        # Wrap around: if we're past the last position, go to index 0
        # This is the "ring" part — the number line wraps
        if idx == len(self._ring_positions):
            idx = 0

        ring_pos = self._ring_positions[idx]
        return self._position_to_server[ring_pos]

    def get_nodes(self, key: str, replicas: int = 3) -> list[str]:
        """
        Get `replicas` distinct physical servers for a key, walking clockwise.

        Used for replication: the first server is the primary, the rest
        are replicas. We skip duplicate physical servers (from virtual nodes)
        to ensure replicas land on different machines.
        """
        if not self._ring_positions:
            return []

        # Can't return more replicas than we have physical servers
        unique_servers = set(self._position_to_server.values())
        replicas = min(replicas, len(unique_servers))

        pos = self._hash(key)
        idx = bisect.bisect_right(self._ring_positions, pos)

        result = []
        seen = set()
        ring_len = len(self._ring_positions)

        # Walk clockwise, collecting distinct physical servers
        for i in range(ring_len):
            ring_pos = self._ring_positions[(idx + i) % ring_len]
            server = self._position_to_server[ring_pos]
            if server not in seen:
                seen.add(server)
                result.append(server)
                if len(result) == replicas:
                    break

        return result

    @property
    def nodes(self) -> list[str]:
        """List all physical servers currently on the ring."""
        return list(self._server_to_positions.keys())

    def __len__(self) -> int:
        """Number of physical servers on the ring."""
        return len(self._server_to_positions)

    def __contains__(self, server: str) -> bool:
        return server in self._server_to_positions


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

def distribution_stats(ring: ConsistentHashRing, num_keys: int = 10_000):
    """Hash num_keys keys and return per-server counts."""
    counts = defaultdict(int)
    for i in range(num_keys):
        server = ring.get_node(f"key-{i}")
        counts[server] += 1
    return dict(counts)


def print_distribution(counts: dict, label: str = ""):
    """Pretty-print server load distribution."""
    total = sum(counts.values())
    if label:
        print(f"\n{'=' * 60}")
        print(f"  {label}")
        print(f"{'=' * 60}")
    print(f"  {'Server':<20} {'Keys':>8} {'Share':>8}")
    print(f"  {'-' * 38}")
    for server in sorted(counts):
        share = counts[server] / total * 100
        print(f"  {server:<20} {counts[server]:>8} {share:>7.1f}%")

    values = list(counts.values())
    mean = total / len(values)
    std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
    print(f"\n  Mean: {mean:.0f}  Std Dev: {std:.0f}  "
          f"Coefficient of Variation: {std / mean * 100:.1f}%")


def demo_key_redistribution(ring: ConsistentHashRing, num_keys: int = 10_000):
    """Show how few keys remap when a server is removed."""
    # Record current assignments
    before = {}
    for i in range(num_keys):
        key = f"key-{i}"
        before[key] = ring.get_node(key)

    servers = ring.nodes[:]
    victim = servers[-1]
    print(f"\n--- Removing server: {victim} ---")
    ring.remove_node(victim)

    # Count remapped keys
    moved = 0
    for i in range(num_keys):
        key = f"key-{i}"
        after = ring.get_node(key)
        if before[key] != after:
            moved += 1

    pct = moved / num_keys * 100
    print(f"  Keys remapped: {moved}/{num_keys} ({pct:.1f}%)")
    print(f"  Ideal (1/N):   {100 / (len(servers)):.1f}%")

    # Restore the ring
    ring.add_node(victim)
    return moved


def demo():
    NUM_KEYS = 10_000
    SERVERS = ["cache-01", "cache-02", "cache-03", "cache-04", "cache-05"]

    # --- 1. Basic distribution with virtual nodes ---
    print("CONSISTENT HASHING DEMO")
    print("=" * 60)
    ring = ConsistentHashRing(num_vnodes=150)
    for s in SERVERS:
        ring.add_node(s)

    counts = distribution_stats(ring, NUM_KEYS)
    print_distribution(counts, "Distribution with 5 servers, 150 vnodes each")

    # --- 2. Key redistribution on server removal ---
    demo_key_redistribution(ring, NUM_KEYS)

    # --- 3. Show imbalance without virtual nodes ---
    ring_no_vnodes = ConsistentHashRing(num_vnodes=1)
    for s in SERVERS:
        ring_no_vnodes.add_node(s)

    counts_no_vn = distribution_stats(ring_no_vnodes, NUM_KEYS)
    print_distribution(counts_no_vn, "Distribution with 5 servers, NO virtual nodes (1 each)")

    # --- 4. Replication demo ---
    print(f"\n{'=' * 60}")
    print("  Replication: 3 replicas per key")
    print(f"{'=' * 60}")
    for i in range(5):
        key = f"user-session-{i}"
        replicas = ring.get_nodes(key, replicas=3)
        print(f"  {key} -> {replicas}")

    # --- 5. Compare with naive modulo ---
    print(f"\n{'=' * 60}")
    print("  Naive modulo: key redistribution when adding a server")
    print(f"{'=' * 60}")
    import hashlib as _hl

    def naive_assign(key, n):
        h = int(_hl.md5(key.encode()).hexdigest()[:8], 16)
        return h % n

    moved_naive = 0
    for i in range(NUM_KEYS):
        key = f"key-{i}"
        if naive_assign(key, 5) != naive_assign(key, 6):
            moved_naive += 1
    pct_naive = moved_naive / NUM_KEYS * 100
    print(f"  Naive modulo (5->6 servers): {moved_naive}/{NUM_KEYS} "
          f"keys moved ({pct_naive:.1f}%)")
    print(f"  Consistent hashing:          ~{100 // 5:.0f}% expected")


if __name__ == "__main__":
    demo()
