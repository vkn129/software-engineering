"""
Day 65 Practice: Advanced Hash Table Collision Resolution
==========================================================

Five exercises exploring collision resolution beyond the basics:
1. Robin Hood hashing
2. Probe length vs load factor measurement
3. Backward shift deletion (tombstone-free)
4. Hopscotch hashing
5. Thread-safe hash table with per-bucket read-write locks

Run: python3 practice.py
"""

import time
import random
import threading


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

_EMPTY = object()
_DELETED = object()


def _hash_key(key):
    """Positive 64-bit hash from Python's built-in hash."""
    return hash(key) & 0x7FFFFFFFFFFFFFFF


# ===========================================================================
# EXERCISE 1: Robin Hood Hashing
# ===========================================================================
# Robin Hood hashing is a variant of linear probing that reduces variance
# in probe lengths. The key idea: when inserting, if the key being inserted
# has traveled FURTHER from its home bucket than the key currently occupying
# a slot, they swap -- the "rich" key (short probe distance) gives its slot
# to the "poor" key (long probe distance).
#
# This keeps the maximum probe length low (O(log log n) vs O(log n) for
# standard linear probing) without changing the average.
# ===========================================================================

class RobinHoodHashTable:
    """Linear probing with Robin Hood displacement.

    On insert, if we encounter a key whose probe distance from home is
    less than ours, we swap and continue inserting the displaced key.
    This equalizes probe lengths across all keys.
    """

    LOAD_THRESHOLD = 0.7

    def __init__(self, capacity=16):
        self._cap = capacity
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0

    def _home(self, key):
        return _hash_key(key) % self._cap

    def _probe_distance(self, slot, key):
        """How far is `slot` from key's home bucket?"""
        home = self._home(key)
        return (slot - home) % self._cap

    def insert(self, key, value):
        if self._size >= self._cap * self.LOAD_THRESHOLD:
            self._resize(self._cap * 2)

        idx = self._home(key)
        dist = 0  # how far the key being inserted has traveled

        while True:
            k = self._keys[idx]

            if k is _EMPTY:
                # Empty slot -- place the key here
                self._keys[idx] = key
                self._vals[idx] = value
                self._size += 1
                return

            if k == key:
                # Key exists -- update value
                self._vals[idx] = value
                return

            # Robin Hood: if the existing key is "richer" (closer to home)
            # than the key we are inserting, steal this slot
            existing_dist = self._probe_distance(idx, k)
            if existing_dist < dist:
                # Swap: our key takes this slot, displaced key continues
                self._keys[idx], key = key, self._keys[idx]
                self._vals[idx], value = value, self._vals[idx]
                dist = existing_dist

            dist += 1
            idx = (idx + 1) % self._cap

    def search(self, key):
        idx = self._home(key)
        dist = 0

        while True:
            k = self._keys[idx]

            if k is _EMPTY:
                return None

            if k == key:
                return self._vals[idx]

            # Robin Hood optimization: if the existing key's probe distance
            # is less than our current distance, the key cannot be further
            # ahead (it would have been displaced). Early termination.
            existing_dist = self._probe_distance(idx, k)
            if existing_dist < dist:
                return None

            dist += 1
            idx = (idx + 1) % self._cap

    def delete(self, key):
        """Delete with backward shift (Robin Hood tables do not use tombstones)."""
        idx = self._home(key)
        dist = 0

        # Find the key
        while True:
            k = self._keys[idx]
            if k is _EMPTY:
                return False
            if k == key:
                break
            existing_dist = self._probe_distance(idx, k)
            if existing_dist < dist:
                return False
            dist += 1
            idx = (idx + 1) % self._cap

        # Backward shift: pull subsequent entries back to fill the gap
        while True:
            next_idx = (idx + 1) % self._cap
            nk = self._keys[next_idx]
            if nk is _EMPTY or self._probe_distance(next_idx, nk) == 0:
                # Next slot is empty or its occupant is at home -- stop
                self._keys[idx] = _EMPTY
                self._vals[idx] = None
                self._size -= 1
                return True
            # Shift back
            self._keys[idx] = self._keys[next_idx]
            self._vals[idx] = self._vals[next_idx]
            idx = next_idx

    def _resize(self, new_cap):
        old_keys = self._keys
        old_vals = self._vals
        self._cap = new_cap
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY:
                self.insert(k, old_vals[i])

    def max_probe_distance(self):
        """Return the maximum probe distance of any key in the table."""
        max_d = 0
        for i in range(self._cap):
            k = self._keys[i]
            if k is not _EMPTY:
                d = self._probe_distance(i, k)
                max_d = max(max_d, d)
        return max_d

    def probe_distance_variance(self):
        """Variance of probe distances -- Robin Hood minimizes this."""
        dists = []
        for i in range(self._cap):
            k = self._keys[i]
            if k is not _EMPTY:
                dists.append(self._probe_distance(i, k))
        if not dists:
            return 0.0
        mean = sum(dists) / len(dists)
        return sum((d - mean) ** 2 for d in dists) / len(dists)

    @property
    def load_factor(self):
        return self._size / self._cap

    def __len__(self):
        return self._size


def exercise_1():
    """Compare Robin Hood hashing vs standard linear probing."""
    print("=" * 70)
    print("EXERCISE 1: Robin Hood Hashing")
    print("=" * 70)
    print()
    print("  Robin Hood hashing steals from the rich (short probe distance)")
    print("  to give to the poor (long probe distance). This reduces the")
    print("  VARIANCE of probe lengths without changing the average.")
    print()

    # Standard linear probing for comparison (no resize, fixed capacity)
    class StandardLP:
        def __init__(self, cap):
            self._cap = cap
            self._keys = [_EMPTY] * cap
            self._vals = [None] * cap
            self._size = 0

        def insert(self, key, value):
            idx = _hash_key(key) % self._cap
            while True:
                k = self._keys[idx]
                if k is _EMPTY:
                    self._keys[idx] = key
                    self._vals[idx] = value
                    self._size += 1
                    return
                if k == key:
                    self._vals[idx] = value
                    return
                idx = (idx + 1) % self._cap

        def max_probe_distance(self):
            max_d = 0
            for i in range(self._cap):
                k = self._keys[i]
                if k is not _EMPTY:
                    home = _hash_key(k) % self._cap
                    d = (i - home) % self._cap
                    max_d = max(max_d, d)
            return max_d

        def probe_distance_variance(self):
            dists = []
            for i in range(self._cap):
                k = self._keys[i]
                if k is not _EMPTY:
                    home = _hash_key(k) % self._cap
                    dists.append((i - home) % self._cap)
            if not dists:
                return 0.0
            mean = sum(dists) / len(dists)
            return sum((d - mean) ** 2 for d in dists) / len(dists)

    random.seed(42)
    CAP = 10007  # prime, no resize
    N = int(CAP * 0.7)  # 70% load factor
    keys = [f"rh_{i}" for i in range(N)]
    random.shuffle(keys)

    rh = RobinHoodHashTable(capacity=CAP)
    std = StandardLP(CAP)
    for k in keys:
        rh.insert(k, 1)
        std.insert(k, 1)

    print(f"  Inserted {N} keys into capacity {CAP} (load factor ~0.70)")
    print()
    print(f"  {'Metric':<30s} {'Standard LP':>15s} {'Robin Hood':>15s}")
    print(f"  {'-'*30} {'-'*15} {'-'*15}")
    print(f"  {'Max probe distance':<30s} {std.max_probe_distance():>15d} {rh.max_probe_distance():>15d}")
    print(f"  {'Probe distance variance':<30s} {std.probe_distance_variance():>15.2f} {rh.probe_distance_variance():>15.2f}")
    print()

    # Verify correctness
    rh2 = RobinHoodHashTable(capacity=32)
    for i in range(20):
        rh2.insert(f"k{i}", i)
    for i in range(20):
        assert rh2.search(f"k{i}") == i, f"search failed for k{i}"
    for i in range(0, 20, 2):
        rh2.delete(f"k{i}")
    for i in range(0, 20, 2):
        assert rh2.search(f"k{i}") is None, f"delete failed for k{i}"
    for i in range(1, 20, 2):
        assert rh2.search(f"k{i}") == i, f"post-delete search failed for k{i}"
    print("  Correctness check (insert/search/delete): PASS")
    print()


# ===========================================================================
# EXERCISE 2: Probe Length vs Load Factor
# ===========================================================================

def exercise_2():
    """Measure average probe length as load factor increases from 0.1 to 0.95."""
    print("=" * 70)
    print("EXERCISE 2: Probe Length vs Load Factor")
    print("=" * 70)
    print()
    print("  Theory predicts:")
    print("    Linear probing:  ~0.5 * (1 + 1/(1-a)^2) for unsuccessful search")
    print("    Double hashing:  ~1/(1-a) for unsuccessful search")
    print("    Chaining:        ~1 + a for unsuccessful search")
    print()

    from hash_table import (ChainingHashTable, LinearProbingHashTable,
                            DoubleHashingTable)

    random.seed(123)
    CAP = 10007  # large prime, no auto-resize (we control load manually)

    load_factors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

    print(f"  {'LF':>5s}  {'Chaining':>10s}  {'Linear':>10s}  {'Double':>10s}")
    print(f"  {'---':>5s}  {'--------':>10s}  {'------':>10s}  {'------':>10s}")

    for target_lf in load_factors:
        n = int(CAP * target_lf)
        keys = [f"lf_{i}" for i in range(n)]
        miss_keys = [f"miss_{i}" for i in range(1000)]

        results = {}
        for name, TableClass in [
            ("Chaining", ChainingHashTable),
            ("Linear", LinearProbingHashTable),
            ("Double", DoubleHashingTable),
        ]:
            # Build table with huge initial capacity so no resize triggers
            t = TableClass(capacity=CAP)
            for k in keys:
                t.insert(k, 1)

            # Measure unsuccessful search probe length
            t.total_probes = 0
            t.total_lookups = 0
            for k in miss_keys:
                t.search(k)
            results[name] = t.avg_probe_length()

        print(f"  {target_lf:5.2f}  {results['Chaining']:10.2f}  "
              f"{results['Linear']:10.2f}  {results['Double']:10.2f}")

    print()
    print("  Notice: linear probing degrades much faster than double hashing")
    print("  at high load factors, matching the 1/(1-a)^2 vs 1/(1-a) theory.")
    print()


# ===========================================================================
# EXERCISE 3: Backward Shift Deletion (Tombstone-Free)
# ===========================================================================

class BackwardShiftHashTable:
    """Linear probing with backward shift deletion -- no tombstones.

    When deleting a key, we shift subsequent entries backward to fill
    the gap, but only if the entry "belongs" at or before the gap.
    This keeps probe chains intact without sentinel markers.

    Advantage over tombstones: no accumulation of dead markers, so
    probe lengths do not degrade over insert/delete cycles.
    """

    LOAD_THRESHOLD = 0.65

    def __init__(self, capacity=16):
        self._cap = capacity
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0

    def insert(self, key, value):
        if self._size >= self._cap * self.LOAD_THRESHOLD:
            self._resize(self._cap * 2)

        idx = _hash_key(key) % self._cap
        while True:
            k = self._keys[idx]
            if k is _EMPTY:
                self._keys[idx] = key
                self._vals[idx] = value
                self._size += 1
                return
            if k == key:
                self._vals[idx] = value
                return
            idx = (idx + 1) % self._cap

    def search(self, key):
        idx = _hash_key(key) % self._cap
        while True:
            k = self._keys[idx]
            if k is _EMPTY:
                return None
            if k == key:
                return self._vals[idx]
            idx = (idx + 1) % self._cap

    def delete(self, key):
        """Backward shift deletion.

        1. Find the key and mark its slot as empty.
        2. Walk forward. For each occupied slot, check if its home bucket
           is at or before the empty slot (wrapping around). If so, shift
           it back to fill the gap, and the new gap is where we shifted from.
        3. Stop when we hit a truly empty slot.
        """
        idx = _hash_key(key) % self._cap

        # Step 1: Find the key
        while True:
            k = self._keys[idx]
            if k is _EMPTY:
                return False
            if k == key:
                break
            idx = (idx + 1) % self._cap

        # Step 2: Backward shift
        gap = idx
        while True:
            candidate = (gap + 1) % self._cap
            ck = self._keys[candidate]

            if ck is _EMPTY:
                # No more entries to shift -- clear the gap
                self._keys[gap] = _EMPTY
                self._vals[gap] = None
                self._size -= 1
                return True

            # Does this candidate "need" the gap? It does if its home
            # bucket is at or before the gap (in circular order).
            # Equivalently: the candidate is displaced past the gap.
            home = _hash_key(ck) % self._cap

            # Check if home is in the range (gap, candidate] circularly.
            # If it IS in that range, the candidate is fine where it is.
            # If it is NOT, the candidate should be shifted back.
            if gap < candidate:
                # No wrap: gap ... candidate
                needs_shift = not (gap < home <= candidate)
            else:
                # Wraps around: gap ... end ... 0 ... candidate
                needs_shift = not (gap < home or home <= candidate)

            if needs_shift:
                self._keys[gap] = self._keys[candidate]
                self._vals[gap] = self._vals[candidate]
                gap = candidate
            else:
                # This entry is fine, but there might be more to shift
                # We must keep going until empty
                candidate_next = (candidate + 1) % self._cap
                # Actually we need to advance gap to candidate if shifted,
                # or advance candidate if not shifted. Let's just scan forward.
                # The correct approach: only advance candidate.
                gap_next = gap  # gap stays
                # We need a different loop structure. Let me redo this.
                break

        # Cleaner backward shift implementation
        # Restart: we know the key is at idx
        self._keys[gap] = _EMPTY
        self._vals[gap] = None
        self._size -= 1
        self._backward_shift_from(gap)
        return True

    def _backward_shift_from(self, gap):
        """Shift entries backward starting from the slot after gap."""
        j = (gap + 1) % self._cap

        while self._keys[j] is not _EMPTY:
            home = _hash_key(self._keys[j]) % self._cap

            # Should this entry be shifted to the gap?
            # Yes if 'home' is not in the range (gap, j] circularly.
            if gap <= j:
                should_shift = home <= gap or home > j
            else:
                should_shift = home <= gap and home > j

            if should_shift:
                self._keys[gap] = self._keys[j]
                self._vals[gap] = self._vals[j]
                self._keys[j] = _EMPTY
                self._vals[j] = None
                gap = j

            j = (j + 1) % self._cap

    def _resize(self, new_cap):
        old_keys = self._keys
        old_vals = self._vals
        self._cap = new_cap
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY:
                self.insert(k, old_vals[i])

    @property
    def load_factor(self):
        return self._size / self._cap

    def __len__(self):
        return self._size


def exercise_3():
    """Compare tombstone vs backward shift deletion."""
    print("=" * 70)
    print("EXERCISE 3: Tombstone vs Backward Shift Deletion")
    print("=" * 70)
    print()

    from hash_table import LinearProbingHashTable

    random.seed(99)
    N = 5000
    keys = [f"del_{i}" for i in range(N)]
    random.shuffle(keys)

    # Tombstone-based (from hash_table.py)
    tomb = LinearProbingHashTable(capacity=16)
    for k in keys:
        tomb.insert(k, 1)

    # Backward shift
    bshift = BackwardShiftHashTable(capacity=16)
    for k in keys:
        bshift.insert(k, 1)

    # Verify both have all keys
    assert all(tomb.search(k) == 1 for k in keys), "Tombstone table missing keys"
    assert all(bshift.search(k) == 1 for k in keys), "BackwardShift table missing keys"

    # Delete half the keys, then search for remaining half
    delete_keys = keys[:N // 2]
    remain_keys = keys[N // 2:]

    for k in delete_keys:
        tomb.delete(k)
        bshift.delete(k)

    # Verify deletes
    assert all(tomb.search(k) is None for k in delete_keys), "Tombstone: deleted key found"
    assert all(bshift.search(k) is None for k in delete_keys), "BackwardShift: deleted key found"
    assert all(tomb.search(k) == 1 for k in remain_keys), "Tombstone: remaining key missing"
    assert all(bshift.search(k) == 1 for k in remain_keys), "BackwardShift: remaining key missing"

    print("  Correctness (both methods): PASS")
    print()

    # Measure probe lengths after deletion
    tomb.total_probes = 0
    tomb.total_lookups = 0
    for k in remain_keys:
        tomb.search(k)
    tomb_avg = tomb.avg_probe_length()

    # For backward shift, count probes manually
    probes_total = 0
    for k in remain_keys:
        idx = _hash_key(k) % bshift._cap
        p = 0
        while True:
            p += 1
            if bshift._keys[idx] == k:
                break
            idx = (idx + 1) % bshift._cap
        probes_total += p
    bshift_avg = probes_total / len(remain_keys)

    print(f"  After deleting {N // 2} of {N} keys:")
    print(f"    Tombstone avg probes:       {tomb_avg:.2f}")
    print(f"    Backward shift avg probes:  {bshift_avg:.2f}")
    print()
    print("  Backward shift keeps probe chains clean -- no tombstone buildup.")
    print()

    # Stress test: many insert/delete cycles
    bshift2 = BackwardShiftHashTable(capacity=16)
    for cycle in range(5):
        batch = [f"cycle_{cycle}_{i}" for i in range(1000)]
        for k in batch:
            bshift2.insert(k, cycle)
        for k in batch:
            assert bshift2.search(k) == cycle
        for k in batch:
            bshift2.delete(k)
        assert len(bshift2) == 0

    print("  Stress test (5 cycles of 1000 insert/delete): PASS")
    print()


# ===========================================================================
# EXERCISE 4: Hopscotch Hashing
# ===========================================================================
# In hopscotch hashing, each entry must reside within H "hops" of its
# home bucket. If a new entry would land too far away, we shuffle closer
# entries outward to make room. This bounds the worst-case probe length
# to H, providing O(1) worst-case lookup with small H.
# ===========================================================================

class HopscotchHashTable:
    """Hopscotch hashing with neighborhood size H.

    Each bucket has a 'hop_info' bitmask indicating which of the next H
    slots contain an entry that belongs to this bucket. Lookups only need
    to check H slots (one cache line if H is small enough).

    Insert: if the first empty slot is within H hops, place there.
    If not, look for an entry within H of the empty slot that can be
    moved further from its home (still within its own H neighborhood)
    to free up a closer slot.
    """

    def __init__(self, capacity=32, neighborhood=8):
        self.H = neighborhood
        self._cap = capacity
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        # hop_info[i] is a bitmask: bit j means slot (i+j) % cap holds
        # an entry whose home is bucket i
        self._hop_info = [0] * self._cap
        self._size = 0

    def insert(self, key, value):
        if self._size >= self._cap * 0.6:
            self._resize(self._cap * 2)

        home = _hash_key(key) % self._cap

        # Check if key already exists in neighborhood
        bits = self._hop_info[home]
        for j in range(self.H):
            if bits & (1 << j):
                idx = (home + j) % self._cap
                if self._keys[idx] == key:
                    self._vals[idx] = value
                    return

        # Find the nearest empty slot (linear scan)
        empty = home
        dist = 0
        while dist < self._cap:
            if self._keys[empty] is _EMPTY:
                break
            dist += 1
            empty = (home + dist) % self._cap
        else:
            self._resize(self._cap * 2)
            self.insert(key, value)
            return

        # If empty slot is within H hops, place there
        if dist < self.H:
            self._keys[empty] = key
            self._vals[empty] = value
            self._hop_info[home] |= (1 << dist)
            self._size += 1
            return

        # Empty slot too far -- need to shuffle entries closer
        while dist >= self.H:
            # Look for an entry in the H-1 slots before `empty` that can
            # be moved to `empty` (i.e., it is within H of its own home)
            moved = False
            for j in range(1, self.H):
                candidate = (empty - j) % self._cap
                cand_key = self._keys[candidate]
                if cand_key is _EMPTY:
                    continue
                cand_home = _hash_key(cand_key) % self._cap

                # Distance from candidate's home to empty slot
                cand_to_empty = (empty - cand_home) % self._cap
                if cand_to_empty < self.H:
                    # Move candidate to empty slot
                    self._keys[empty] = self._keys[candidate]
                    self._vals[empty] = self._vals[candidate]
                    self._keys[candidate] = _EMPTY
                    self._vals[candidate] = None

                    # Update hop_info: remove old bit, add new bit
                    cand_to_old = (candidate - cand_home) % self._cap
                    self._hop_info[cand_home] &= ~(1 << cand_to_old)
                    self._hop_info[cand_home] |= (1 << cand_to_empty)

                    empty = candidate
                    dist = (empty - home) % self._cap
                    moved = True
                    break

            if not moved:
                # Cannot make room -- resize
                self._resize(self._cap * 2)
                self.insert(key, value)
                return

        # Now empty is within H hops of home
        self._keys[empty] = key
        self._vals[empty] = value
        self._hop_info[home] |= (1 << dist)
        self._size += 1

    def search(self, key):
        home = _hash_key(key) % self._cap
        bits = self._hop_info[home]

        # Only check slots indicated by the hop bitmask -- at most H slots
        for j in range(self.H):
            if bits & (1 << j):
                idx = (home + j) % self._cap
                if self._keys[idx] == key:
                    return self._vals[idx]
        return None

    def delete(self, key):
        home = _hash_key(key) % self._cap
        bits = self._hop_info[home]

        for j in range(self.H):
            if bits & (1 << j):
                idx = (home + j) % self._cap
                if self._keys[idx] == key:
                    self._keys[idx] = _EMPTY
                    self._vals[idx] = None
                    self._hop_info[home] &= ~(1 << j)
                    self._size -= 1
                    return True
        return False

    def _resize(self, new_cap):
        old_keys = self._keys
        old_vals = self._vals
        self._cap = new_cap
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._hop_info = [0] * self._cap
        self._size = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY:
                self.insert(k, old_vals[i])

    @property
    def load_factor(self):
        return self._size / self._cap

    def __len__(self):
        return self._size


def exercise_4():
    """Test hopscotch hashing."""
    print("=" * 70)
    print("EXERCISE 4: Hopscotch Hashing")
    print("=" * 70)
    print()
    print("  Hopscotch hashing bounds the worst-case lookup to H probes.")
    print("  Each key must be within H slots of its home bucket.")
    print()

    random.seed(77)
    ht = HopscotchHashTable(capacity=64, neighborhood=8)

    N = 500
    keys = [f"hop_{i}" for i in range(N)]
    random.shuffle(keys)

    for k in keys:
        ht.insert(k, 1)

    # Verify all keys found
    found = sum(1 for k in keys if ht.search(k) == 1)
    print(f"  Inserted {N} keys: {found}/{N} found  {'PASS' if found == N else 'FAIL'}")

    # Verify lookup only checks within H slots
    violations = 0
    for i in range(ht._cap):
        k = ht._keys[i]
        if k is not _EMPTY:
            home = _hash_key(k) % ht._cap
            dist = (i - home) % ht._cap
            if dist >= ht.H:
                violations += 1

    print(f"  Neighborhood violations (dist >= H): {violations}  "
          f"{'PASS' if violations == 0 else 'FAIL'}")

    # Delete half
    for k in keys[:N // 2]:
        ht.delete(k)

    remaining = sum(1 for k in keys[N // 2:] if ht.search(k) == 1)
    deleted = sum(1 for k in keys[:N // 2] if ht.search(k) is None)
    print(f"  After deleting {N // 2}: remaining={remaining}/{N // 2}, "
          f"deleted={deleted}/{N // 2}  "
          f"{'PASS' if remaining == N // 2 and deleted == N // 2 else 'FAIL'}")
    print()


# ===========================================================================
# EXERCISE 5: Thread-Safe Hash Table with Per-Bucket Read-Write Locks
# ===========================================================================
# A single global lock serializes all operations. Per-bucket locks allow
# concurrent reads on different buckets and concurrent writes to different
# buckets. We use a read-write lock: multiple readers OR one writer per bucket.
#
# We simulate this with actual threading.Lock and threading.RLock, plus a
# lock counter to observe contention.
# ===========================================================================

class RWLock:
    """Simple read-write lock.

    Multiple readers can hold the lock simultaneously.
    A writer gets exclusive access.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._readers = 0
        self._readers_lock = threading.Lock()
        self.read_acquisitions = 0
        self.write_acquisitions = 0

    def acquire_read(self):
        with self._readers_lock:
            self._readers += 1
            if self._readers == 1:
                self._lock.acquire()
            self.read_acquisitions += 1

    def release_read(self):
        with self._readers_lock:
            self._readers -= 1
            if self._readers == 0:
                self._lock.release()

    def acquire_write(self):
        self._lock.acquire()
        self.write_acquisitions += 1

    def release_write(self):
        self._lock.release()


class ThreadSafeHashTable:
    """Chaining hash table with per-bucket read-write locks.

    Each bucket gets its own RWLock, allowing:
    - Multiple threads to read different buckets concurrently
    - Multiple threads to write to different buckets concurrently
    - Multiple readers on the same bucket concurrently
    - Only one writer per bucket at a time (exclusive)

    This is much better than a single global lock, which serializes
    everything. The trade-off is memory overhead (one lock per bucket)
    and complexity in resize (must acquire all locks).
    """

    def __init__(self, capacity=16):
        self._cap = capacity
        self._buckets = [None] * self._cap
        self._locks = [RWLock() for _ in range(self._cap)]
        self._size = 0
        self._size_lock = threading.Lock()

    def insert(self, key, value):
        idx = _hash_key(key) % self._cap
        self._locks[idx].acquire_write()
        try:
            node = self._buckets[idx]
            while node is not None:
                if node.key == key:
                    node.value = value
                    return
                node = node.next
            self._buckets[idx] = _TSNode(key, value, self._buckets[idx])
            with self._size_lock:
                self._size += 1
        finally:
            self._locks[idx].release_write()

    def search(self, key):
        idx = _hash_key(key) % self._cap
        self._locks[idx].acquire_read()
        try:
            node = self._buckets[idx]
            while node is not None:
                if node.key == key:
                    return node.value
                node = node.next
            return None
        finally:
            self._locks[idx].release_read()

    def delete(self, key):
        idx = _hash_key(key) % self._cap
        self._locks[idx].acquire_write()
        try:
            node = self._buckets[idx]
            prev = None
            while node is not None:
                if node.key == key:
                    if prev is None:
                        self._buckets[idx] = node.next
                    else:
                        prev.next = node.next
                    with self._size_lock:
                        self._size -= 1
                    return True
                prev = node
                node = node.next
            return False
        finally:
            self._locks[idx].release_write()

    def lock_stats(self):
        total_reads = sum(l.read_acquisitions for l in self._locks)
        total_writes = sum(l.write_acquisitions for l in self._locks)
        return {"read_acquisitions": total_reads, "write_acquisitions": total_writes}

    def __len__(self):
        return self._size


class _TSNode:
    __slots__ = ('key', 'value', 'next')
    def __init__(self, key, value, nxt=None):
        self.key = key
        self.value = value
        self.next = nxt


def exercise_5():
    """Thread-safe hash table with per-bucket read-write locks."""
    print("=" * 70)
    print("EXERCISE 5: Thread-Safe Hash Table (Per-Bucket RW Locks)")
    print("=" * 70)
    print()

    ts = ThreadSafeHashTable(capacity=32)
    N = 2000
    NUM_THREADS = 4

    # Phase 1: Concurrent inserts from multiple threads
    def writer_task(thread_id, keys_subset):
        for k in keys_subset:
            ts.insert(k, thread_id)

    keys = [f"ts_{i}" for i in range(N)]
    chunk = N // NUM_THREADS
    threads = []
    for t in range(NUM_THREADS):
        subset = keys[t * chunk:(t + 1) * chunk]
        thr = threading.Thread(target=writer_task, args=(t, subset))
        threads.append(thr)

    t0 = time.perf_counter()
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()
    insert_time = (time.perf_counter() - t0) * 1000

    print(f"  Phase 1: {NUM_THREADS} threads inserted {N} keys in {insert_time:.1f} ms")
    assert len(ts) == N, f"Expected {N}, got {len(ts)}"
    print(f"  Size: {len(ts)} (correct: {len(ts) == N})")

    # Phase 2: Concurrent reads
    found_count = [0]
    found_lock = threading.Lock()

    def reader_task(keys_subset):
        count = 0
        for k in keys_subset:
            if ts.search(k) is not None:
                count += 1
        with found_lock:
            found_count[0] += count

    threads = []
    for t in range(NUM_THREADS):
        subset = keys[t * chunk:(t + 1) * chunk]
        thr = threading.Thread(target=reader_task, args=(subset,))
        threads.append(thr)

    t0 = time.perf_counter()
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()
    read_time = (time.perf_counter() - t0) * 1000

    print(f"  Phase 2: {NUM_THREADS} threads read {N} keys in {read_time:.1f} ms")
    print(f"  Found: {found_count[0]}/{N}")

    # Phase 3: Mixed read/write
    def mixed_task(thread_id, keys_subset):
        for i, k in enumerate(keys_subset):
            if i % 3 == 0:
                ts.insert(f"new_{thread_id}_{i}", thread_id)
            elif i % 3 == 1:
                ts.search(k)
            else:
                ts.delete(k)

    threads = []
    for t in range(NUM_THREADS):
        subset = keys[t * chunk:(t + 1) * chunk]
        thr = threading.Thread(target=mixed_task, args=(t, subset))
        threads.append(thr)

    t0 = time.perf_counter()
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()
    mixed_time = (time.perf_counter() - t0) * 1000

    stats = ts.lock_stats()
    print(f"  Phase 3: Mixed read/write in {mixed_time:.1f} ms")
    print(f"  Lock stats: {stats['read_acquisitions']} read acquisitions, "
          f"{stats['write_acquisitions']} write acquisitions")
    print(f"  Final size: {len(ts)}")
    print()
    print("  Per-bucket locks allow parallelism: threads accessing different")
    print("  buckets never block each other. Multiple readers on the same")
    print("  bucket also proceed concurrently.")
    print()


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    exercise_1()
    print()
    exercise_2()
    print()
    exercise_3()
    print()
    exercise_4()
    print()
    exercise_5()

    print("=" * 70)
    print("All exercises complete.")
    print("=" * 70)
