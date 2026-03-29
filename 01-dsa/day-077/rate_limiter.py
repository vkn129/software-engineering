"""
Day 77: Distributed Rate Limiter Mini-Project
Week 11 Capstone — Tying together probabilistic data structures

Why build this: Rate limiting is approximate counting under time pressure.
Probabilistic structures (CMS, Bloom, HLL) trade tiny error for massive
efficiency — exactly what distributed rate limiting needs.
"""

import time
import math
import random
import hashlib
import struct
from collections import defaultdict


# ---------------------------------------------------------------------------
# Probabilistic building blocks (self-contained, no external deps)
# ---------------------------------------------------------------------------

class CountMinSketch:
    """
    Approximate frequency counter. Overestimates but never underestimates.
    Used here for distributed approximate request counting.
    """

    def __init__(self, width=1000, depth=5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]

    def _hashes(self, key):
        """Generate `depth` independent hash positions for a key."""
        key_bytes = str(key).encode('utf-8')
        positions = []
        for i in range(self.depth):
            h = hashlib.md5(key_bytes + struct.pack('I', i)).hexdigest()
            positions.append(int(h, 16) % self.width)
        return positions

    def add(self, key, count=1):
        for i, pos in enumerate(self._hashes(key)):
            self.table[i][pos] += count

    def estimate(self, key):
        return min(self.table[i][pos] for i, pos in enumerate(self._hashes(key)))

    def merge(self, other):
        """Merge another CMS into this one (element-wise addition)."""
        assert self.width == other.width and self.depth == other.depth
        for i in range(self.depth):
            for j in range(self.width):
                self.table[i][j] += other.table[i][j]


class BloomFilter:
    """
    Probabilistic set membership. No false negatives, tunable false positive rate.
    Used here to check "has this IP been seen recently?"
    """

    def __init__(self, expected_items=1000, fp_rate=0.01):
        # Optimal size: m = -n*ln(p) / (ln2)^2
        self.size = max(64, int(-expected_items * math.log(fp_rate) / (math.log(2) ** 2)))
        # Optimal hash count: k = (m/n) * ln2
        self.num_hashes = max(1, int((self.size / expected_items) * math.log(2)))
        self.bits = [False] * self.size

    def _hashes(self, key):
        key_bytes = str(key).encode('utf-8')
        positions = []
        for i in range(self.num_hashes):
            h = hashlib.sha256(key_bytes + struct.pack('I', i)).hexdigest()
            positions.append(int(h, 16) % self.size)
        return positions

    def add(self, key):
        for pos in self._hashes(key):
            self.bits[pos] = True

    def might_contain(self, key):
        return all(self.bits[pos] for pos in self._hashes(key))

    def union(self, other):
        """OR two filters together (for time-bucketed merging)."""
        assert self.size == other.size
        result = BloomFilter.__new__(BloomFilter)
        result.size = self.size
        result.num_hashes = self.num_hashes
        result.bits = [a or b for a, b in zip(self.bits, other.bits)]
        return result


class HyperLogLog:
    """
    Cardinality estimator. ~2% error with 16KB memory.
    Used here for "how many unique users hit this endpoint?"
    """

    def __init__(self, precision=14):
        self.p = precision
        self.m = 1 << precision  # number of registers
        self.registers = [0] * self.m
        # Alpha constant for bias correction
        if self.m >= 128:
            self.alpha = 0.7213 / (1 + 1.079 / self.m)
        elif self.m == 64:
            self.alpha = 0.709
        elif self.m == 32:
            self.alpha = 0.697
        else:
            self.alpha = 0.673

    def _hash(self, key):
        h = hashlib.sha256(str(key).encode('utf-8')).hexdigest()
        return int(h, 16) & ((1 << 64) - 1)  # 64-bit hash

    def add(self, key):
        x = self._hash(key)
        # First p bits determine register index
        idx = x & (self.m - 1)
        # Remaining bits: count leading zeros + 1
        remaining = x >> self.p
        # Count trailing zeros of remaining (equivalent to leading zeros from MSB)
        rho = 1
        while rho <= 64 - self.p and (remaining & 1) == 0:
            rho += 1
            remaining >>= 1
        self.registers[idx] = max(self.registers[idx], rho)

    def estimate(self):
        # Harmonic mean of 2^(-register)
        indicator = sum(2.0 ** (-r) for r in self.registers)
        raw = self.alpha * self.m * self.m / indicator

        # Small range correction
        if raw <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros > 0:
                return self.m * math.log(self.m / zeros)
        return raw


# ---------------------------------------------------------------------------
# Consistent hashing (for routing keys to servers)
# ---------------------------------------------------------------------------

class ConsistentHashRing:
    """
    Maps keys to servers using a hash ring with virtual nodes.
    Why virtual nodes: prevents hot spots when servers are added/removed.
    """

    def __init__(self, servers, virtual_nodes=150):
        self.ring = {}  # hash -> server_id
        self.sorted_hashes = []

        for server in servers:
            for vn in range(virtual_nodes):
                key = f"{server}:vn{vn}"
                h = int(hashlib.md5(key.encode()).hexdigest(), 16)
                self.ring[h] = server
                self.sorted_hashes.append(h)
        self.sorted_hashes.sort()

    def get_server(self, key):
        """Find the server responsible for this key."""
        if not self.sorted_hashes:
            return None
        h = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        # Binary search for the first hash >= h
        lo, hi = 0, len(self.sorted_hashes)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.sorted_hashes[mid] < h:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(self.sorted_hashes):
            lo = 0  # wrap around
        return self.ring[self.sorted_hashes[lo]]


# ---------------------------------------------------------------------------
# Rate Limiter implementations
# ---------------------------------------------------------------------------

class FixedWindowLimiter:
    """
    Simplest rate limiter: divide time into fixed windows, count per window.

    Weakness: boundary burst. A user can send `limit` requests at the end of
    one window and `limit` more at the start of the next = 2x limit in a
    short burst.
    """

    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        # key -> (window_start_time, count)
        self.counters = {}

    def allow(self, key, now=None):
        now = now or time.time()
        window = int(now // self.window_seconds)

        if key not in self.counters or self.counters[key][0] != window:
            self.counters[key] = [window, 0]

        if self.counters[key][1] >= self.limit:
            return False
        self.counters[key][1] += 1
        return True

    def get_count(self, key, now=None):
        now = now or time.time()
        window = int(now // self.window_seconds)
        if key in self.counters and self.counters[key][0] == window:
            return self.counters[key][1]
        return 0


class SlidingWindowLimiter:
    """
    Approximate sliding window using weighted combination of two fixed windows.

    rate = prev_count * ((window - elapsed) / window) + current_count

    This smooths the boundary burst problem with minimal extra state
    (just two counters instead of a full log).
    """

    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        # key -> {window_id: count}
        self.counters = defaultdict(lambda: defaultdict(int))

    def _estimate(self, key, now):
        window = int(now // self.window_seconds)
        elapsed = now - window * self.window_seconds
        overlap_fraction = (self.window_seconds - elapsed) / self.window_seconds

        prev_count = self.counters[key].get(window - 1, 0)
        curr_count = self.counters[key].get(window, 0)

        return prev_count * overlap_fraction + curr_count

    def allow(self, key, now=None):
        now = now or time.time()
        window = int(now // self.window_seconds)

        if self._estimate(key, now) >= self.limit:
            return False

        self.counters[key][window] += 1

        # Garbage collect old windows (keep only current and previous)
        old_keys = [w for w in self.counters[key] if w < window - 1]
        for w in old_keys:
            del self.counters[key][w]

        return True

    def get_estimated_count(self, key, now=None):
        now = now or time.time()
        return self._estimate(key, now)


class TokenBucketLimiter:
    """
    Tokens refill at a constant rate up to a maximum (burst size).
    Each request consumes one token. If no tokens, request is denied.

    Key insight: don't actually refill on a timer — calculate tokens
    available at request time using elapsed time since last refill.
    This is called "lazy refill" and avoids background threads.
    """

    def __init__(self, rate, burst):
        """
        rate: tokens per second (sustained rate)
        burst: max tokens (max burst size)
        """
        self.rate = rate
        self.burst = burst
        # key -> (tokens, last_refill_time)
        self.buckets = {}

    def allow(self, key, now=None):
        now = now or time.time()

        if key not in self.buckets:
            # Start with a full bucket
            self.buckets[key] = [self.burst, now]

        tokens, last_refill = self.buckets[key]

        # Lazy refill: add tokens based on elapsed time
        elapsed = now - last_refill
        tokens = min(self.burst, tokens + elapsed * self.rate)

        if tokens < 1:
            self.buckets[key] = [tokens, now]
            return False

        self.buckets[key] = [tokens - 1, now]
        return True

    def get_tokens(self, key, now=None):
        now = now or time.time()
        if key not in self.buckets:
            return self.burst
        tokens, last_refill = self.buckets[key]
        elapsed = now - last_refill
        return min(self.burst, tokens + elapsed * self.rate)


class LeakyBucketLimiter:
    """
    Requests enter a queue. The queue drains at a constant rate.
    If the queue is full, new requests are dropped.

    Unlike token bucket, this enforces a strict constant output rate —
    no bursts at all. Good for traffic shaping.
    """

    def __init__(self, capacity, leak_rate):
        """
        capacity: max queue size
        leak_rate: requests drained per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        # key -> (water_level, last_leak_time)
        self.buckets = {}

    def allow(self, key, now=None):
        now = now or time.time()

        if key not in self.buckets:
            self.buckets[key] = [0.0, now]

        water, last_leak = self.buckets[key]

        # Leak: drain based on elapsed time
        elapsed = now - last_leak
        water = max(0.0, water - elapsed * self.leak_rate)

        if water >= self.capacity:
            self.buckets[key] = [water, now]
            return False

        self.buckets[key] = [water + 1, now]
        return True

    def get_queue_level(self, key, now=None):
        now = now or time.time()
        if key not in self.buckets:
            return 0.0
        water, last_leak = self.buckets[key]
        elapsed = now - last_leak
        return max(0.0, water - elapsed * self.leak_rate)


# ---------------------------------------------------------------------------
# Distributed Rate Limiter
# ---------------------------------------------------------------------------

class DistributedRateLimiter:
    """
    Combines:
    - Consistent hashing: route each user key to a specific server
    - Count-Min Sketch: approximate request counts per server
    - Bloom filter: track recently-seen IPs
    - HyperLogLog: count unique users per endpoint

    Each "server" is simulated as a local CMS + Bloom filter.
    Periodic merge combines all server sketches for a global view.

    Why this design: In a real distributed system, exact counting requires
    coordination (locks, consensus). Approximate counting with probabilistic
    structures lets each server operate independently, only syncing sketches
    periodically — and merging is just element-wise addition.
    """

    def __init__(self, num_servers=3, limit=100, window_seconds=60,
                 cms_width=1000, cms_depth=5, bloom_expected=10000, bloom_fp=0.01):
        self.num_servers = num_servers
        self.limit = limit
        self.window_seconds = window_seconds

        server_ids = [f"server-{i}" for i in range(num_servers)]
        self.hash_ring = ConsistentHashRing(server_ids)

        # Per-server state
        self.server_cms = {s: CountMinSketch(cms_width, cms_depth) for s in server_ids}
        self.server_bloom = {s: BloomFilter(bloom_expected, bloom_fp) for s in server_ids}
        self.server_window = {s: 0 for s in server_ids}

        # Global merged CMS (updated periodically)
        self.global_cms = CountMinSketch(cms_width, cms_depth)

        # Per-endpoint HyperLogLog for unique user counting
        self.endpoint_hll = defaultdict(lambda: HyperLogLog(precision=12))

        self.stats = {
            'allowed': 0,
            'denied': 0,
            'bloom_hits': 0,
            'merges': 0,
        }

    def _get_window(self, now):
        return int(now // self.window_seconds)

    def _maybe_rotate_window(self, server, now):
        """Reset server CMS/Bloom when window changes."""
        current_window = self._get_window(now)
        if self.server_window[server] != current_window:
            self.server_cms[server] = CountMinSketch(
                self.server_cms[server].width,
                self.server_cms[server].depth,
            )
            self.server_bloom[server] = BloomFilter()
            self.server_window[server] = current_window

    def allow(self, key, ip=None, endpoint=None, now=None):
        """
        Check if request from `key` should be allowed.
        Optionally track IP in bloom filter and endpoint cardinality in HLL.
        """
        now = now or time.time()
        server = self.hash_ring.get_server(key)
        self._maybe_rotate_window(server, now)

        cms = self.server_cms[server]

        # Check approximate count
        estimated = cms.estimate(key)
        if estimated >= self.limit:
            self.stats['denied'] += 1
            return False

        # Record the request
        cms.add(key)

        # Track IP in bloom filter if provided
        if ip:
            bloom = self.server_bloom[server]
            if bloom.might_contain(ip):
                self.stats['bloom_hits'] += 1
            bloom.add(ip)

        # Track unique users per endpoint with HLL
        if endpoint:
            self.endpoint_hll[endpoint].add(key)

        self.stats['allowed'] += 1
        return True

    def merge_all(self):
        """
        Merge all server CMS into a global view.
        In production, this would happen on a timer (e.g., every 5 seconds).
        """
        servers = list(self.server_cms.keys())
        merged = CountMinSketch(
            self.server_cms[servers[0]].width,
            self.server_cms[servers[0]].depth,
        )
        for s in servers:
            merged.merge(self.server_cms[s])
        self.global_cms = merged
        self.stats['merges'] += 1

    def get_global_estimate(self, key):
        """Get the merged global count estimate for a key."""
        return self.global_cms.estimate(key)

    def get_unique_users(self, endpoint):
        """Estimate unique users for an endpoint using HLL."""
        if endpoint in self.endpoint_hll:
            return int(self.endpoint_hll[endpoint].estimate())
        return 0

    def get_stats(self):
        return dict(self.stats)


# ---------------------------------------------------------------------------
# Demo: Simulate 1000 requests from 50 users, compare all limiters
# ---------------------------------------------------------------------------

def demo():
    print("=" * 70)
    print("DAY 77: DISTRIBUTED RATE LIMITER — COMPARING ALL ALGORITHMS")
    print("=" * 70)

    # Simulation parameters
    num_users = 50
    num_requests = 1000
    limit = 20          # max requests per user per window
    window_seconds = 10  # 10-second window

    # Create all limiters with comparable settings
    fixed = FixedWindowLimiter(limit, window_seconds)
    sliding = SlidingWindowLimiter(limit, window_seconds)
    token = TokenBucketLimiter(rate=limit / window_seconds, burst=limit)
    leaky = LeakyBucketLimiter(capacity=limit, leak_rate=limit / window_seconds)
    distributed = DistributedRateLimiter(
        num_servers=3, limit=limit, window_seconds=window_seconds
    )

    limiters = {
        'Fixed Window': fixed,
        'Sliding Window': sliding,
        'Token Bucket': token,
        'Leaky Bucket': leaky,
        'Distributed (CMS)': distributed,
    }

    # Generate requests: some users are heavy (simulate abuse)
    random.seed(42)
    users = [f"user-{i}" for i in range(num_users)]
    heavy_users = set(random.sample(users, 5))  # 5 heavy users

    requests = []
    base_time = 1000000.0

    for i in range(num_requests):
        # Heavy users generate 5x more traffic
        if random.random() < 0.3:
            user = random.choice(list(heavy_users))
        else:
            user = random.choice(users)

        # Spread requests over ~30 seconds (3 windows)
        t = base_time + random.uniform(0, 30)
        ip = f"192.168.1.{hash(user) % 256}"
        endpoint = random.choice(['/api/data', '/api/users', '/api/search'])
        requests.append((user, ip, endpoint, t))

    # Sort by time (as they would arrive)
    requests.sort(key=lambda x: x[3])

    # Run all limiters
    results = {}

    for name, limiter in limiters.items():
        allowed = 0
        denied = 0

        for user, ip, endpoint, t in requests:
            if name == 'Distributed (CMS)':
                ok = limiter.allow(user, ip=ip, endpoint=endpoint, now=t)
            elif hasattr(limiter, 'allow'):
                ok = limiter.allow(user, now=t)

            if ok:
                allowed += 1
            else:
                denied += 1

        results[name] = (allowed, denied)

    # Print results
    print(f"\nSimulation: {num_requests} requests from {num_users} users "
          f"({len(heavy_users)} heavy)")
    print(f"Limit: {limit} requests per {window_seconds}s window")
    print(f"Time span: ~30 seconds (3 windows)\n")

    print(f"{'Algorithm':<22} {'Allowed':>8} {'Denied':>8} {'Allow %':>8}")
    print("-" * 50)
    for name in limiters:
        allowed, denied = results[name]
        pct = allowed / num_requests * 100
        print(f"{name:<22} {allowed:>8} {denied:>8} {pct:>7.1f}%")

    # Distributed limiter extra stats
    print(f"\n--- Distributed Limiter Details ---")
    distributed.merge_all()

    print(f"\nPer-endpoint unique users (HLL estimates):")
    for ep in ['/api/data', '/api/users', '/api/search']:
        est = distributed.get_unique_users(ep)
        print(f"  {ep}: ~{est} unique users")

    print(f"\nHeavy user global count estimates (after merge):")
    for user in sorted(heavy_users):
        est = distributed.get_global_estimate(user)
        print(f"  {user}: ~{est} requests (CMS estimate)")

    stats = distributed.get_stats()
    print(f"\nDistributed stats: {stats}")

    # Demonstrate boundary burst problem
    print(f"\n--- Boundary Burst Demo ---")
    fw = FixedWindowLimiter(limit=10, window_seconds=1.0)
    sw = SlidingWindowLimiter(limit=10, window_seconds=1.0)

    base = 1000.0
    burst_allowed_fw = 0
    burst_allowed_sw = 0

    # Send 10 requests at t=0.95 (end of window) and 10 at t=1.05 (start of next)
    for i in range(10):
        if fw.allow("bursty", now=base + 0.95 + i * 0.001):
            burst_allowed_fw += 1
        if sw.allow("bursty", now=base + 0.95 + i * 0.001):
            burst_allowed_sw += 1
    for i in range(10):
        if fw.allow("bursty", now=base + 1.05 + i * 0.001):
            burst_allowed_fw += 1
        if sw.allow("bursty", now=base + 1.05 + i * 0.001):
            burst_allowed_sw += 1

    print(f"20 requests spanning a window boundary (10 before, 10 after):")
    print(f"  Fixed Window allowed:   {burst_allowed_fw}/20  (boundary burst!)")
    print(f"  Sliding Window allowed: {burst_allowed_sw}/20  (smoothed)")

    # Token bucket burst behavior
    print(f"\n--- Token Bucket Burst Demo ---")
    tb = TokenBucketLimiter(rate=2, burst=10)
    # User has been idle — full bucket of 10 tokens
    burst_count = 0
    t = 5000.0
    for i in range(15):
        if tb.allow("burst-user", now=t + i * 0.01):
            burst_count += 1
    print(f"After idle period, 15 rapid requests:")
    print(f"  Allowed {burst_count}/15 (burst=10, then rate-limited)")

    # After 3 seconds, some tokens refill
    refilled = 0
    t2 = t + 3.0
    for i in range(10):
        if tb.allow("burst-user", now=t2 + i * 0.01):
            refilled += 1
    print(f"After 3s wait (rate=2/s, expect ~6 tokens):")
    print(f"  Allowed {refilled}/10")

    print(f"\n{'=' * 70}")
    print("Key takeaway: Each algorithm makes different trade-offs between")
    print("accuracy, memory, burst tolerance, and implementation complexity.")
    print("Probabilistic structures (CMS, Bloom, HLL) enable distributed")
    print("rate limiting with minimal coordination overhead.")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    demo()
