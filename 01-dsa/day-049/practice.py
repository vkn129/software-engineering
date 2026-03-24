"""
Day 49 Practice: Ordered KV Store Capstone Exercises
=====================================================
Week 7 capstone — integrate BST concepts into practical systems.

Run: python practice.py
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))
from ordered_kvstore import OrderedKVStore


# ─── Exercise 1: Time-Windowed Event Counter ───────────────────────
#
# Build an event counter that tracks events with timestamps.
# Support: record(timestamp), count_in_window(start, end)
#
# Use the OrderedKVStore with timestamps as keys.
# This is how rate limiters and monitoring dashboards work.

class EventCounter:
    def __init__(self):
        # TODO: initialize
        pass

    def record(self, timestamp):
        # TODO: record an event at this timestamp
        pass

    def count_in_window(self, start, end):
        # TODO: return number of events in [start, end]
        pass


# ─── Exercise 2: Leaderboard ───────────────────────────────────────
#
# A leaderboard supporting:
#   add_score(player, score)
#   top_k(k) → list of (player, score) top k scores
#   rank_of(player) → 1-based rank
#
# Trick: use negative scores as keys so the "minimum" is the highest score.

class Leaderboard:
    def __init__(self):
        # TODO: initialize
        pass

    def add_score(self, player, score):
        # TODO: add or update player's score
        pass

    def top_k(self, k):
        # TODO: return [(player, score), ...] for top k
        pass

    def rank_of(self, player):
        # TODO: return 1-based rank of player
        pass


# ─── Exercise 3: Percentile Query ──────────────────────────────────
#
# Given a collection of numbers, find the value at the Pth percentile.
# P=50 → median, P=90 → 90th percentile, P=99 → 99th percentile.
#
# Use the ordered store's rank/select operations.

class PercentileTracker:
    def __init__(self):
        # TODO: initialize
        pass

    def add(self, value):
        # TODO: add a value
        pass

    def percentile(self, p):
        # TODO: return value at pth percentile (0-100)
        pass


# ─── Exercise 4: Range Delete ──────────────────────────────────────
#
# Delete all keys in the range [lo, hi] from an OrderedKVStore.
# Return the number of keys deleted.
#
# Challenge: do it efficiently without collecting all keys first.

def range_delete(store, lo, hi):
    # TODO: delete all keys in [lo, hi], return count deleted
    pass


# ─── Exercise 5: Merge Two Ordered Stores ──────────────────────────
#
# Merge two OrderedKVStores into one. If a key exists in both,
# keep the value from store2 (second wins).
# Return a new OrderedKVStore.

def merge_stores(store1, store2):
    # TODO: return merged OrderedKVStore
    pass


# ─── Exercise 6: Interval Overlap Detector ─────────────────────────
#
# Given a set of intervals [start, end], detect if a new interval
# overlaps with any existing one. Uses the ordered store to find
# the interval whose start is just before the new interval's end.
#
# Two intervals [a,b] and [c,d] overlap iff a < d AND c < b.

class IntervalDetector:
    def __init__(self):
        # TODO: initialize
        pass

    def add(self, start, end):
        # TODO: add interval, return True if it overlaps with existing
        pass

    def overlaps(self, start, end):
        # TODO: check if interval overlaps with any existing
        pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

class _SolEventCounter:
    def __init__(self):
        self.store = OrderedKVStore()
        self._counter = 0

    def record(self, timestamp):
        # Use (timestamp, counter) to handle duplicate timestamps
        self._counter += 1
        self.store.put(timestamp + self._counter * 1e-10, True)

    def count_in_window(self, start, end):
        events = self.store.range(start, end + 1)
        return len(events)


class _SolLeaderboard:
    def __init__(self):
        self.store = OrderedKVStore()
        self.players = {}  # player → score

    def add_score(self, player, score):
        if player in self.players:
            old_key = -self.players[player]
            self.store.delete(old_key)
        self.players[player] = score
        self.store.put(-score, player)  # Negative so min = highest

    def top_k(self, k):
        # Get first k entries (smallest keys = highest scores)
        result = []
        items = self.store.range(float('-inf'), float('inf'))
        for neg_score, player in items[:k]:
            result.append((player, -neg_score))
        return result

    def rank_of(self, player):
        if player not in self.players:
            return -1
        score = self.players[player]
        rank = self.store.rank(-score)
        return rank + 1  # 1-based


class _SolPercentileTracker:
    def __init__(self):
        self.store = OrderedKVStore()
        self._count = 0
        self._id = 0

    def add(self, value):
        self._id += 1
        # Use (value, id) to handle duplicates
        self.store.put(value + self._id * 1e-12, value)
        self._count += 1

    def percentile(self, p):
        if self._count == 0:
            return None
        # Index = ceil(p/100 * count) - 1
        idx = max(0, int((p / 100) * self._count + 0.5) - 1)
        idx = min(idx, self._count - 1)
        key, val = self.store.select(idx)
        return val


def _sol_range_delete(store, lo, hi):
    items = store.range(lo, hi + 0.001)  # Small epsilon for inclusive
    count = 0
    for key, _ in items:
        if lo <= key <= hi:
            store.delete(key)
            count += 1
    return count


def _sol_merge_stores(store1, store2):
    result = OrderedKVStore()
    # Add all from store1
    for key, val in store1.range(float('-inf'), float('inf')):
        result.put(key, val)
    # Add all from store2 (overwrites duplicates)
    for key, val in store2.range(float('-inf'), float('inf')):
        result.put(key, val)
    return result


class _SolIntervalDetector:
    def __init__(self):
        self.store = OrderedKVStore()  # key=start, value=end

    def add(self, start, end):
        overlaps = self.overlaps(start, end)
        self.store.put(start, end)
        return overlaps

    def overlaps(self, start, end):
        # Check all intervals that start before our end
        candidates = self.store.range(float('-inf'), end)
        for s, e in candidates:
            if s < end and start < e:
                return True
        return False


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1: Event Counter
    print("\nExercise 1: Event Counter")
    for Cls in [EventCounter, _SolEventCounter]:
        ec = Cls()
        if not hasattr(ec, 'record'):
            print("  (skipped — not implemented)")
            break
        ec.record(1.0)
        ec.record(2.0)
        ec.record(3.0)
        ec.record(5.0)
        r = ec.count_in_window(1.0, 3.5)
        if r is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} window [1, 3.5]", r, 3)

    # Exercise 2: Leaderboard
    print("\nExercise 2: Leaderboard")
    for Cls in [Leaderboard, _SolLeaderboard]:
        lb = Cls()
        if not hasattr(lb, 'add_score'):
            print("  (skipped — not implemented)")
            break
        lb.add_score("Alice", 100)
        lb.add_score("Bob", 200)
        lb.add_score("Charlie", 150)
        top = lb.top_k(2)
        if top is None:
            print("  (skipped — not implemented)")
            break
        names = [p for p, s in top]
        check(f"{Cls.__name__} top_k(2)", names, ["Bob", "Charlie"])

    # Exercise 3: Percentile
    print("\nExercise 3: Percentile Tracker")
    for Cls in [PercentileTracker, _SolPercentileTracker]:
        pt = Cls()
        if not hasattr(pt, 'add'):
            print("  (skipped — not implemented)")
            break
        for v in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            pt.add(v)
        r = pt.percentile(50)
        if r is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} P50", r, 50)

    # Exercise 4: Range Delete
    print("\nExercise 4: Range Delete")
    for fn in [range_delete, _sol_range_delete]:
        store = OrderedKVStore()
        for i in range(1, 11):
            store.put(i, f"val_{i}")
        if fn is range_delete and fn(store, 3, 7) is None:
            print("  (skipped — not implemented)")
            break
        store2 = OrderedKVStore()
        for i in range(1, 11):
            store2.put(i, f"val_{i}")
        count = fn(store2, 3, 7)
        check(f"{fn.__name__}(3, 7) count", count, 5)

    # Exercise 5: Merge Stores
    print("\nExercise 5: Merge Stores")
    for fn in [merge_stores, _sol_merge_stores]:
        s1 = OrderedKVStore()
        s1.put(1, "a")
        s1.put(3, "c")
        s2 = OrderedKVStore()
        s2.put(2, "b")
        s2.put(3, "C")
        if fn is merge_stores and fn(s1, s2) is None:
            print("  (skipped — not implemented)")
            break
        merged = fn(s1, s2)
        items = merged.range(0, 10)
        keys = [k for k, v in items]
        check(f"{fn.__name__} keys", keys, [1, 2, 3])

    # Exercise 6: Interval Detector
    print("\nExercise 6: Interval Overlap Detector")
    for Cls in [IntervalDetector, _SolIntervalDetector]:
        det = Cls()
        if not hasattr(det, 'add'):
            print("  (skipped — not implemented)")
            break
        r1 = det.add(1, 5)
        if r1 is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} add(1,5) no overlap", r1, False)
        check(f"{Cls.__name__} add(4,8) overlap", det.add(4, 8), True)
        check(f"{Cls.__name__} add(10,12) no overlap", det.add(10, 12), False)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
