"""
Day 167: Rate Limiting — Token, Leaky, Fixed-Window, Sliding-Window

Four canonical algorithms. Each has the same interface: `allow(now)` -> bool.
Time is parameterized so tests are deterministic; in production pass
time.monotonic().
"""

from collections import deque, defaultdict


# ---------------------------------------------------------------------------
# 1. Token Bucket — bursty up to B, sustained rate R
# ---------------------------------------------------------------------------

class TokenBucket:
    """Refill R tokens/sec, capped at B. allow(now) consumes 1 token."""

    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self._last = None   # last refill time

    def allow(self, now: float, cost: float = 1.0) -> bool:
        if self._last is None:
            self._last = now
        # Refill
        elapsed = now - self._last
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self._last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


# ---------------------------------------------------------------------------
# 2. Leaky Bucket — smooth outflow at D, queue size Q
# ---------------------------------------------------------------------------

class LeakyBucket:
    """Bucket leaks D units/sec. allow() adds 1 unit if it fits, else deny."""

    def __init__(self, capacity: float, leak_rate: float):
        self.capacity = float(capacity)
        self.leak_rate = float(leak_rate)
        self.water = 0.0
        self._last = None

    def allow(self, now: float) -> bool:
        if self._last is None:
            self._last = now
        elapsed = now - self._last
        if elapsed > 0:
            self.water = max(0.0, self.water - elapsed * self.leak_rate)
            self._last = now
        if self.water + 1.0 <= self.capacity:
            self.water += 1.0
            return True
        return False


# ---------------------------------------------------------------------------
# 3. Fixed-Window Counter
# ---------------------------------------------------------------------------

class FixedWindow:
    """Up to `limit` requests per `window_secs` aligned window."""

    def __init__(self, limit: int, window_secs: float):
        self.limit = limit
        self.window_secs = float(window_secs)
        self.window_start = None
        self.count = 0

    def allow(self, now: float) -> bool:
        w = int(now // self.window_secs)
        if self.window_start != w:
            self.window_start = w
            self.count = 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


# ---------------------------------------------------------------------------
# 4. Sliding-Window Counter (approximate)
# ---------------------------------------------------------------------------

class SlidingWindowCounter:
    """
    Weighted blend of current and previous window counts:
      effective = current_count + prev_count * (1 - elapsed_fraction)
    """

    def __init__(self, limit: int, window_secs: float):
        self.limit = limit
        self.window_secs = float(window_secs)
        self.current_w = None
        self.current_count = 0
        self.prev_count = 0

    def allow(self, now: float) -> bool:
        w = int(now // self.window_secs)
        if self.current_w is None or w > self.current_w:
            if self.current_w is not None and w == self.current_w + 1:
                self.prev_count = self.current_count
            else:
                self.prev_count = 0
            self.current_w = w
            self.current_count = 0

        elapsed = (now - w * self.window_secs) / self.window_secs   # [0,1)
        effective = self.current_count + self.prev_count * (1.0 - elapsed)
        if effective + 1 <= self.limit:
            self.current_count += 1
            return True
        return False


# ---------------------------------------------------------------------------
# 5. Sliding-Window Log (exact, memory ~ rate * window)
# ---------------------------------------------------------------------------

class SlidingWindowLog:
    """Store timestamps; drop those older than (now - window)."""

    def __init__(self, limit: int, window_secs: float):
        self.limit = limit
        self.window_secs = float(window_secs)
        self.timestamps: "deque[float]" = deque()

    def allow(self, now: float) -> bool:
        cutoff = now - self.window_secs
        while self.timestamps and self.timestamps[0] <= cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) < self.limit:
            self.timestamps.append(now)
            return True
        return False


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_token_bucket():
    print("=" * 60)
    print("DEMO 1: Token Bucket — bursts allowed up to capacity")
    print("=" * 60)
    tb = TokenBucket(capacity=5, refill_rate=1)   # 5 burst, 1/sec sustained
    times = [0, 0, 0, 0, 0, 0, 0, 1, 2]
    for t in times:
        print(f"  t={t}s  allow={tb.allow(t)}  tokens={tb.tokens:.2f}")


def demo_leaky_bucket():
    print("\n" + "=" * 60)
    print("DEMO 2: Leaky Bucket — bursts smoothed")
    print("=" * 60)
    lb = LeakyBucket(capacity=3, leak_rate=1)
    times = [0.0, 0.1, 0.2, 0.3, 0.4, 1.5, 2.6]
    for t in times:
        print(f"  t={t}s  allow={lb.allow(t)}  water={lb.water:.2f}")


def demo_fixed_window_double_burst():
    print("\n" + "=" * 60)
    print("DEMO 3: Fixed Window — boundary double-burst attack")
    print("=" * 60)
    fw = FixedWindow(limit=3, window_secs=10)
    # 3 at end of window 0, then 3 at start of window 1 -> 6 in <1s
    pattern = [9.9, 9.91, 9.92, 10.0, 10.01, 10.02]
    for t in pattern:
        print(f"  t={t}s  allow={fw.allow(t)}")


def demo_sliding_counter_fixes_boundary():
    print("\n" + "=" * 60)
    print("DEMO 4: Sliding Window Counter — boundary smoothed")
    print("=" * 60)
    sw = SlidingWindowCounter(limit=3, window_secs=10)
    pattern = [9.9, 9.91, 9.92, 10.0, 10.01, 10.02, 10.5]
    for t in pattern:
        print(f"  t={t}s  allow={sw.allow(t)}")


def demo_sliding_log_precision():
    print("\n" + "=" * 60)
    print("DEMO 5: Sliding Window Log — exact")
    print("=" * 60)
    sl = SlidingWindowLog(limit=3, window_secs=10)
    pattern = [0, 1, 2, 5, 11, 12]   # 3 within first 10s, expire at t=11
    for t in pattern:
        print(f"  t={t}s  allow={sl.allow(t)}  inflight={len(sl.timestamps)}")


if __name__ == "__main__":
    demo_token_bucket()
    demo_leaky_bucket()
    demo_fixed_window_double_burst()
    demo_sliding_counter_fixes_boundary()
    demo_sliding_log_precision()
