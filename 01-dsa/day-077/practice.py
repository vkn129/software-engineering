"""
Day 77 Practice: Distributed Rate Limiter Exercises

5 exercises building on the main implementation.
Each exercise has a skeleton with TODO markers and a verify function.
Run: python3 practice.py
"""

import time
import math
import hashlib
import struct
import random
from collections import defaultdict


# ---------------------------------------------------------------------------
# Provided: minimal CMS and Bloom filter (same as rate_limiter.py)
# ---------------------------------------------------------------------------

class CountMinSketch:
    def __init__(self, width=1000, depth=5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]

    def _hashes(self, key):
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
        for i in range(self.depth):
            for j in range(self.width):
                self.table[i][j] += other.table[i][j]


class BloomFilter:
    def __init__(self, expected_items=1000, fp_rate=0.01):
        self.size = max(64, int(-expected_items * math.log(fp_rate) / (math.log(2) ** 2)))
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


class HyperLogLog:
    def __init__(self, precision=12):
        self.p = precision
        self.m = 1 << precision
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m) if self.m >= 128 else 0.673

    def add(self, key):
        h = int(hashlib.sha256(str(key).encode()).hexdigest(), 16) & ((1 << 64) - 1)
        idx = h & (self.m - 1)
        remaining = h >> self.p
        rho = 1
        while rho <= 64 - self.p and (remaining & 1) == 0:
            rho += 1
            remaining >>= 1
        self.registers[idx] = max(self.registers[idx], rho)

    def estimate(self):
        indicator = sum(2.0 ** (-r) for r in self.registers)
        raw = self.alpha * self.m * self.m / indicator
        if raw <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros > 0:
                return self.m * math.log(self.m / zeros)
        return raw


# ===========================================================================
# EXERCISE 1: Sliding Window Log (Exact)
# ===========================================================================
# Store every request timestamp. Count how many fall within the window.
# This is the "exact" approach — no approximation, but O(n) memory.

class SlidingWindowLogLimiter:
    """
    Exact sliding window rate limiter using a log of timestamps.

    For each key, maintain a sorted list of request timestamps.
    To check if a request is allowed:
      1. Remove all timestamps older than (now - window_seconds)
      2. If remaining count < limit, allow and add timestamp
      3. Otherwise deny
    """

    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window_seconds = window_seconds
        # TODO: Initialize storage for timestamps per key
        self.logs = defaultdict(list)

    def allow(self, key, now=None):
        now = now or time.time()

        # TODO: Implement sliding window log algorithm
        # 1. Get the timestamp log for this key
        # 2. Remove expired timestamps (older than now - window_seconds)
        # 3. Check if under limit
        # 4. If yes, append timestamp and return True
        # 5. If no, return False

        log = self.logs[key]

        # Remove expired entries
        cutoff = now - self.window_seconds
        # Binary search would be optimal, but linear scan is clearer
        while log and log[0] <= cutoff:
            log.pop(0)

        if len(log) >= self.limit:
            return False

        log.append(now)
        return True

    def get_count(self, key, now=None):
        """Return exact count of requests in current window."""
        now = now or time.time()
        cutoff = now - self.window_seconds
        log = self.logs[key]
        # Count entries within window
        return sum(1 for t in log if t > cutoff)


def verify_exercise_1():
    print("Exercise 1: Sliding Window Log (Exact)")
    print("-" * 45)

    limiter = SlidingWindowLogLimiter(limit=5, window_seconds=10.0)
    base = 1000.0

    # Send 5 requests at t=0..0.04 — all should be allowed
    for i in range(5):
        assert limiter.allow("user-a", now=base + i * 0.01), f"Request {i} should be allowed"

    # 6th request should be denied
    assert not limiter.allow("user-a", now=base + 0.05), "6th request should be denied"

    # After window expires, should be allowed again
    assert limiter.allow("user-a", now=base + 11), "Should be allowed after window expires"

    # Exact count check — previous 5 all expired (they were at t~=base, window=10s)
    count = limiter.get_count("user-a", now=base + 11)
    assert count == 1, f"Expected count 1, got {count}"

    # Different keys don't interfere
    assert limiter.allow("user-b", now=base + 5), "Different user should be allowed"

    # Test sliding nature: send 3 at t=0, 2 at t=5, then at t=11 the first 3 expired
    limiter2 = SlidingWindowLogLimiter(limit=5, window_seconds=10.0)
    for i in range(3):
        limiter2.allow("x", now=2000.0 + i * 0.1)
    for i in range(2):
        limiter2.allow("x", now=2005.0 + i * 0.1)

    # At t=2005.5, all 5 are in window
    assert not limiter2.allow("x", now=2005.5), "Window should be full"

    # At t=2010.5, the first 3 expired, only 2 remain
    assert limiter2.allow("x", now=2010.5), "Old entries should have expired"
    count = limiter2.get_count("x", now=2010.5)
    assert count == 3, f"Expected 3 (2 old + 1 new), got {count}"

    print("  PASSED\n")


# ===========================================================================
# EXERCISE 2: IP Reputation Scoring
# ===========================================================================
# Combine CMS (frequency), Bloom filter (known-bad list), and HLL (endpoint diversity)
# to compute a reputation score for each IP.

class IPReputationScorer:
    """
    Reputation scoring combining three probabilistic structures:

    - CMS: track request frequency per IP (high frequency = suspicious)
    - Bloom filter: check against known-bad IP list (instant block)
    - HLL per IP: count unique endpoints accessed (low diversity = bot-like)

    Score formula:
      If IP is in bad list -> score = 0.0 (blocked)
      Otherwise: score = diversity_factor * (1 - frequency_factor)
        where frequency_factor = min(1.0, request_count / high_threshold)
        and diversity_factor = min(1.0, unique_endpoints / expected_endpoints)

    Score ranges: 0.0 (block) to 1.0 (trusted)
    """

    def __init__(self, high_threshold=100, expected_endpoints=10):
        self.high_threshold = high_threshold
        self.expected_endpoints = expected_endpoints

        # TODO: Initialize CMS, Bloom filter, and per-IP HLL
        self.cms = CountMinSketch(width=2000, depth=5)
        self.bad_ips = BloomFilter(expected_items=10000, fp_rate=0.001)
        self.ip_endpoints = defaultdict(lambda: HyperLogLog(precision=10))

    def add_bad_ip(self, ip):
        """Add an IP to the known-bad list."""
        # TODO: Add to bloom filter
        self.bad_ips.add(ip)

    def record_request(self, ip, endpoint):
        """Record a request from an IP to an endpoint."""
        # TODO:
        # 1. Increment IP count in CMS
        # 2. Add endpoint to this IP's HLL
        self.cms.add(ip)
        self.ip_endpoints[ip].add(endpoint)

    def get_score(self, ip):
        """
        Compute reputation score for an IP.
        Returns float in [0.0, 1.0]. Lower = more suspicious.
        """
        # TODO: Implement scoring formula described in docstring
        # Check bad list first
        if self.bad_ips.might_contain(ip):
            return 0.0

        freq = self.cms.estimate(ip)
        frequency_factor = min(1.0, freq / self.high_threshold)

        unique_eps = self.ip_endpoints[ip].estimate() if ip in self.ip_endpoints else 0
        diversity_factor = min(1.0, unique_eps / self.expected_endpoints)

        return diversity_factor * (1.0 - frequency_factor)


def verify_exercise_2():
    print("Exercise 2: IP Reputation Scoring")
    print("-" * 45)

    scorer = IPReputationScorer(high_threshold=100, expected_endpoints=10)

    # Known bad IP should score 0
    scorer.add_bad_ip("10.0.0.666")
    assert scorer.get_score("10.0.0.666") == 0.0, "Bad IP should score 0"

    # New IP with no requests — score should be 0 (no diversity)
    score = scorer.get_score("192.168.1.1")
    assert score == 0.0, f"New IP with no requests should score ~0, got {score}"

    # Normal user: moderate requests across many endpoints
    for i in range(30):
        endpoint = f"/api/endpoint-{i % 10}"
        scorer.record_request("192.168.1.1", endpoint)
    good_score = scorer.get_score("192.168.1.1")
    assert good_score > 0.5, f"Normal user should score > 0.5, got {good_score}"

    # Bot-like: many requests to single endpoint
    for i in range(90):
        scorer.record_request("10.0.0.99", "/api/login")
    bot_score = scorer.get_score("10.0.0.99")
    assert bot_score < good_score, (
        f"Bot should score lower ({bot_score}) than normal user ({good_score})"
    )

    # Heavy abuser: tons of requests
    for i in range(200):
        scorer.record_request("10.0.0.50", f"/api/ep-{i % 3}")
    abuser_score = scorer.get_score("10.0.0.50")
    assert abuser_score < 0.1, f"Heavy abuser should score < 0.1, got {abuser_score}"

    print(f"  Scores: normal={good_score:.3f}, bot={bot_score:.3f}, abuser={abuser_score:.3f}")
    print("  PASSED\n")


# ===========================================================================
# EXERCISE 3: Priority Rate Limiter
# ===========================================================================
# Premium users get higher limits. Implement using per-tier token buckets.

class PriorityRateLimiter:
    """
    Rate limiter with user tiers. Each tier has its own rate and burst limits.

    Tiers (default):
      - 'free':    rate=1/s, burst=5
      - 'basic':   rate=5/s, burst=20
      - 'premium': rate=20/s, burst=50

    Each user gets a token bucket configured for their tier.
    """

    DEFAULT_TIERS = {
        'free':    {'rate': 1,  'burst': 5},
        'basic':   {'rate': 5,  'burst': 20},
        'premium': {'rate': 20, 'burst': 50},
    }

    def __init__(self, tiers=None):
        self.tiers = tiers or self.DEFAULT_TIERS
        # TODO: Initialize storage for per-user buckets and tier assignments
        # user -> tier name
        self.user_tiers = {}
        # user -> (tokens, last_refill_time)
        self.buckets = {}

    def set_tier(self, user, tier):
        """Assign a user to a tier. Resets their bucket to full."""
        # TODO: Store tier assignment and initialize bucket
        if tier not in self.tiers:
            raise ValueError(f"Unknown tier: {tier}")
        self.user_tiers[user] = tier
        # Reset bucket to full for new tier
        self.buckets[user] = [self.tiers[tier]['burst'], None]

    def allow(self, user, now=None):
        """
        Check if request is allowed for user based on their tier.
        Default tier is 'free' if not set.
        """
        now = now or time.time()

        # TODO: Implement token bucket logic with per-tier configuration
        # 1. Get user's tier (default to 'free')
        # 2. Get or create their token bucket
        # 3. Lazy refill based on elapsed time
        # 4. Check if tokens available

        tier_name = self.user_tiers.get(user, 'free')
        tier_config = self.tiers[tier_name]
        rate = tier_config['rate']
        burst = tier_config['burst']

        if user not in self.buckets:
            self.buckets[user] = [burst, now]

        tokens, last_refill = self.buckets[user]
        if last_refill is None:
            last_refill = now

        elapsed = now - last_refill
        tokens = min(burst, tokens + elapsed * rate)

        if tokens < 1:
            self.buckets[user] = [tokens, now]
            return False

        self.buckets[user] = [tokens - 1, now]
        return True

    def get_tier(self, user):
        return self.user_tiers.get(user, 'free')


def verify_exercise_3():
    print("Exercise 3: Priority Rate Limiter")
    print("-" * 45)

    limiter = PriorityRateLimiter()
    limiter.set_tier("alice", "premium")
    limiter.set_tier("bob", "basic")
    # charlie is default 'free'

    base = 5000.0

    # All requests at same instant to test pure burst capacity
    # Premium user can burst 50
    premium_allowed = sum(
        1 for i in range(60)
        if limiter.allow("alice", now=base)
    )
    assert premium_allowed == 50, f"Premium burst should be 50, got {premium_allowed}"

    # Basic user can burst 20
    basic_allowed = sum(
        1 for i in range(30)
        if limiter.allow("bob", now=base)
    )
    assert basic_allowed == 20, f"Basic burst should be 20, got {basic_allowed}"

    # Free user can burst 5
    free_allowed = sum(
        1 for i in range(10)
        if limiter.allow("charlie", now=base)
    )
    assert free_allowed == 5, f"Free burst should be 5, got {free_allowed}"

    # After 2 seconds, premium refills 40 tokens (rate=20/s)
    premium_after = sum(
        1 for i in range(50)
        if limiter.allow("alice", now=base + 2.0)
    )
    assert premium_after == 40, f"Premium should refill ~40 in 2s, got {premium_after}"

    # After 2 seconds, free refills 2 tokens (rate=1/s)
    free_after = sum(
        1 for i in range(5)
        if limiter.allow("charlie", now=base + 2.0)
    )
    assert free_after == 2, f"Free should refill ~2 in 2s, got {free_after}"

    print(f"  Premium burst={premium_allowed}, Basic burst={basic_allowed}, Free burst={free_allowed}")
    print(f"  Premium refill(2s)={premium_after}, Free refill(2s)={free_after}")
    print("  PASSED\n")


# ===========================================================================
# EXERCISE 4: Burst Detection
# ===========================================================================
# Flag IPs that exceed 10x their average rate in any 1-second micro-window.

class BurstDetector:
    """
    Detects anomalous traffic bursts per IP.

    Tracks two things:
    1. Long-term average rate (requests per second over observation period)
    2. Short-term micro-window rate (requests in current 1-second window)

    An IP is flagged as "bursting" if its micro-window count exceeds
    burst_factor * average_rate.

    Implementation:
    - total_requests and first_seen_time give the long-term average
    - current_window_count tracks the current 1-second micro-window
    """

    def __init__(self, burst_factor=10):
        self.burst_factor = burst_factor
        # TODO: Initialize per-IP tracking state
        # ip -> {'total': int, 'first_seen': float,
        #         'window_start': float, 'window_count': int}
        self.ip_state = {}

    def record(self, ip, now=None):
        """
        Record a request and return True if this request triggers a burst alert.
        """
        now = now or time.time()

        # TODO: Implement burst detection
        # 1. Initialize state for new IPs
        # 2. Update total count
        # 3. Check if we're in a new 1-second micro-window
        #    - If yes, reset window counter
        # 4. Increment window counter
        # 5. Calculate average rate = total / elapsed_time
        # 6. Return True if window_count > burst_factor * average_rate

        if ip not in self.ip_state:
            self.ip_state[ip] = {
                'total': 0,
                'first_seen': now,
                'window_start': now,
                'window_count': 0,
            }

        state = self.ip_state[ip]
        state['total'] += 1

        # Check if we moved to a new micro-window
        if now - state['window_start'] >= 1.0:
            state['window_start'] = now
            state['window_count'] = 0

        state['window_count'] += 1

        # Need at least some history to compute meaningful average
        elapsed = now - state['first_seen']
        if elapsed < 1.0:
            return False  # Not enough data yet

        avg_rate = state['total'] / elapsed
        threshold = self.burst_factor * max(avg_rate, 0.1)  # floor to avoid div issues

        return state['window_count'] > threshold

    def get_average_rate(self, ip, now=None):
        """Get the long-term average rate for an IP."""
        now = now or time.time()
        if ip not in self.ip_state:
            return 0.0
        state = self.ip_state[ip]
        elapsed = now - state['first_seen']
        if elapsed <= 0:
            return 0.0
        return state['total'] / elapsed


def verify_exercise_4():
    print("Exercise 4: Burst Detection")
    print("-" * 45)

    detector = BurstDetector(burst_factor=10)
    base = 10000.0

    # Build up a baseline: 2 req/s for 10 seconds = 20 requests
    alerts = []
    for sec in range(10):
        for req in range(2):
            t = base + sec + req * 0.4
            alert = detector.record("steady-ip", now=t)
            alerts.append(alert)

    # No burst alerts during steady traffic
    assert not any(alerts), "Steady traffic should not trigger alerts"

    avg = detector.get_average_rate("steady-ip", now=base + 10)
    assert 1.5 < avg < 2.5, f"Average rate should be ~2/s, got {avg:.2f}"

    # Now burst: 50 requests in 1 second (25x the average)
    burst_alerts = []
    for i in range(50):
        t = base + 11.0 + i * 0.01  # 50 requests in 0.5 seconds
        alert = detector.record("steady-ip", now=t)
        burst_alerts.append(alert)

    # Should trigger at least some alerts
    num_alerts = sum(burst_alerts)
    assert num_alerts > 0, "Burst should trigger alerts"

    # A brand new IP shouldn't alert immediately (not enough history)
    new_alerts = []
    for i in range(5):
        alert = detector.record("new-ip", now=base + i * 0.1)
        new_alerts.append(alert)
    assert not any(new_alerts), "New IP should not alert (insufficient history)"

    print(f"  Average rate (steady phase): {avg:.2f} req/s")
    print(f"  Burst alerts triggered: {num_alerts}/{len(burst_alerts)}")
    print("  PASSED\n")


# ===========================================================================
# EXERCISE 5: Distributed Rate Limiting Simulation
# ===========================================================================
# N servers each maintain local CMS. Compare accuracy vs a centralized counter.

class CentralizedLimiter:
    """Reference: exact centralized counter (single point of truth)."""

    def __init__(self, limit):
        self.limit = limit
        self.counts = defaultdict(int)

    def allow(self, key):
        if self.counts[key] >= self.limit:
            return False
        self.counts[key] += 1
        return True

    def get_count(self, key):
        return self.counts[key]


class DistributedCMSLimiter:
    """
    N servers, each with a local CMS. Requests are routed via consistent hashing.

    For comparison, we also track exact local counts to measure CMS error.

    Merge strategy: periodically merge all CMS into a global sketch.
    Between merges, each server only sees its local traffic.
    """

    def __init__(self, num_servers, limit, cms_width=500, cms_depth=4):
        self.num_servers = num_servers
        self.limit = limit

        # TODO: Initialize per-server CMS, exact counters, and hash ring
        self.server_ids = [f"srv-{i}" for i in range(num_servers)]

        # Consistent hash ring for routing
        self.ring = {}
        self.sorted_hashes = []
        for srv in self.server_ids:
            for vn in range(100):
                h = int(hashlib.md5(f"{srv}:vn{vn}".encode()).hexdigest(), 16)
                self.ring[h] = srv
                self.sorted_hashes.append(h)
        self.sorted_hashes.sort()

        # Per-server state
        self.server_cms = {s: CountMinSketch(cms_width, cms_depth) for s in self.server_ids}
        self.server_exact = {s: defaultdict(int) for s in self.server_ids}

        # Global merged CMS
        self.global_cms = CountMinSketch(cms_width, cms_depth)

    def _route(self, key):
        """Route a key to a server using consistent hashing."""
        h = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        lo, hi = 0, len(self.sorted_hashes)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.sorted_hashes[mid] < h:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(self.sorted_hashes):
            lo = 0
        return self.ring[self.sorted_hashes[lo]]

    def allow(self, key):
        """
        Route to server, check local CMS estimate, record if allowed.
        """
        # TODO: Implement distributed allow
        # 1. Route key to server
        # 2. Check local CMS estimate
        # 3. If under limit, record in CMS and exact counter, return True
        # 4. Otherwise return False

        server = self._route(key)
        cms = self.server_cms[server]

        if cms.estimate(key) >= self.limit:
            return False

        cms.add(key)
        self.server_exact[server][key] += 1
        return True

    def merge(self):
        """Merge all server CMS into global view."""
        # TODO: Create a fresh CMS and merge all server sketches into it
        width = self.server_cms[self.server_ids[0]].width
        depth = self.server_cms[self.server_ids[0]].depth
        merged = CountMinSketch(width, depth)
        for srv in self.server_ids:
            merged.merge(self.server_cms[srv])
        self.global_cms = merged

    def get_global_estimate(self, key):
        return self.global_cms.estimate(key)

    def get_exact_total(self, key):
        """Sum exact counts across all servers for ground truth."""
        return sum(self.server_exact[s][key] for s in self.server_ids)


def verify_exercise_5():
    print("Exercise 5: Distributed vs Centralized Rate Limiting")
    print("-" * 55)

    num_servers = 5
    limit = 50
    num_users = 100
    requests_per_user = 80  # exceeds limit, so some should be denied

    centralized = CentralizedLimiter(limit)
    distributed = DistributedCMSLimiter(num_servers, limit)

    random.seed(123)
    users = [f"user-{i}" for i in range(num_users)]

    # Generate shuffled request stream
    request_stream = []
    for user in users:
        for _ in range(requests_per_user):
            request_stream.append(user)
    random.shuffle(request_stream)

    central_allowed = 0
    distrib_allowed = 0

    for key in request_stream:
        if centralized.allow(key):
            central_allowed += 1
        if distributed.allow(key):
            distrib_allowed += 1

    # Merge and compare estimates
    distributed.merge()

    total_requests = len(request_stream)
    print(f"  Total requests: {total_requests}")
    print(f"  Centralized allowed: {central_allowed}")
    print(f"  Distributed allowed: {distrib_allowed}")
    print(f"  Difference: {abs(central_allowed - distrib_allowed)}")

    # Check CMS accuracy vs exact counts for a sample of users
    errors = []
    for user in users[:20]:
        exact = distributed.get_exact_total(user)
        estimated = distributed.get_global_estimate(user)
        error = estimated - exact  # CMS overestimates
        errors.append(error)

    avg_error = sum(errors) / len(errors)
    max_error = max(errors)

    print(f"\n  CMS accuracy (sample of 20 users):")
    print(f"    Average overestimate: {avg_error:.1f}")
    print(f"    Max overestimate: {max_error}")

    # CMS should not underestimate
    assert all(e >= 0 for e in errors), "CMS should never underestimate"

    # Distributed should allow roughly similar amount as centralized
    # (may differ because routing concentrates all of a user's traffic on one server)
    ratio = distrib_allowed / central_allowed if central_allowed > 0 else 1
    assert 0.8 < ratio < 1.2, (
        f"Distributed should be within 20% of centralized, ratio={ratio:.3f}"
    )

    # CMS error should be reasonable (not more than 20% of true count for most)
    assert avg_error < limit * 0.3, (
        f"Average CMS error {avg_error} too high"
    )

    print(f"\n  Centralized/Distributed ratio: {ratio:.3f}")
    print("  PASSED\n")


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("=" * 60)
    print("DAY 77 PRACTICE: DISTRIBUTED RATE LIMITER EXERCISES")
    print("=" * 60)
    print()

    verify_exercise_1()
    verify_exercise_2()
    verify_exercise_3()
    verify_exercise_4()
    verify_exercise_5()

    print("=" * 60)
    print("ALL EXERCISES PASSED")
    print()
    print("Key learnings:")
    print("  1. Sliding window log is exact but O(n) memory per user")
    print("  2. Probabilistic structures combine for powerful IP scoring")
    print("  3. Token buckets naturally support per-tier rate limits")
    print("  4. Burst detection needs both long-term and short-term views")
    print("  5. Distributed CMS gives ~centralized accuracy without coordination")
    print("=" * 60)


if __name__ == '__main__':
    main()
