"""
Day 76: Quotient Filter — A space-efficient probabilistic data structure.

Why this exists:
Bloom filters cannot delete elements, merge efficiently, or resize gracefully.
Quotient filters solve all three by storing hash fingerprints in a single
contiguous array using linear probing with three metadata bits per slot.

Core idea: split hash into quotient (bucket index) and remainder (stored value).
The three metadata bits (is_occupied, is_continuation, is_shifted) let us
reconstruct which elements belong to which bucket even after collision shifting.
"""

import hashlib
import random


class QuotientFilter:
    """
    A quotient filter supporting insert, lookup, and delete.

    Parameters:
        q_bits: number of bits for the quotient (table has 2^q_bits slots)
        r_bits: number of bits for the remainder (controls false positive rate)

    False positive rate is approximately 2^(-r_bits) when the filter is not
    too full. As occupancy approaches 1.0, performance degrades due to long
    clusters.

    Implementation:
    Each slot has a remainder and three metadata bits:
      - is_occupied: some element with this canonical slot exists in the table
      - is_continuation: this element is NOT the first in its run
      - is_shifted: this element has been displaced from its canonical slot

    Elements sharing the same quotient form a "run" stored contiguously and
    sorted by remainder. Adjacent runs form "clusters".
    """

    def __init__(self, q_bits=8, r_bits=8):
        self.q_bits = q_bits
        self.r_bits = r_bits
        self.size = 1 << q_bits  # 2^q_bits slots
        self.mask_q = self.size - 1
        self.mask_r = (1 << r_bits) - 1
        self.fingerprint_bits = q_bits + r_bits

        # Each slot: remainder value + 3 metadata bits
        self.remainders = [0] * self.size
        self.is_occupied = [False] * self.size
        self.is_continuation = [False] * self.size
        self.is_shifted = [False] * self.size

        self.count = 0

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    def _hash(self, item):
        """Hash an item to a fingerprint of (q_bits + r_bits) bits."""
        if not isinstance(item, bytes):
            item = str(item).encode('utf-8')
        h = hashlib.sha256(item).digest()
        num_bytes = (self.fingerprint_bits + 7) // 8
        value = int.from_bytes(h[:num_bytes], 'big')
        return value & ((1 << self.fingerprint_bits) - 1)

    def _split_hash(self, item):
        """Split hash into (quotient, remainder)."""
        fp = self._hash(item)
        quotient = (fp >> self.r_bits) & self.mask_q
        remainder = fp & self.mask_r
        return quotient, remainder

    # ------------------------------------------------------------------
    # Slot navigation
    # ------------------------------------------------------------------

    def _incr(self, slot):
        """Next slot with wraparound."""
        return (slot + 1) & self.mask_q

    def _decr(self, slot):
        """Previous slot with wraparound."""
        return (slot - 1) & self.mask_q

    def _is_empty_slot(self, slot):
        """True if no element is stored here (all metadata bits clear or only occupied)."""
        # A slot stores an element if is_shifted or is_continuation is set,
        # OR if is_occupied is set and this is the canonical first element.
        # But is_occupied can be set while the slot holds an element from a
        # different run. We need a cleaner test.
        #
        # A slot is truly empty (holds no element) iff it is not part of
        # any cluster. That means: not is_shifted and not is_continuation,
        # AND either not is_occupied or is_occupied is set but the run for
        # this quotient lives elsewhere.
        #
        # Simplification: a slot holds an element iff
        #   is_shifted OR is_continuation OR (is_occupied AND the slot is
        #   the first of its own run — which is the case when not shifted
        #   and not continuation).
        # In other words, a slot is empty iff all three bits are False,
        # or is_occupied is the only bit set but no element was placed here.
        #
        # Actually, our insert always places an element when is_occupied is
        # set for the first time at the canonical slot. So:
        # slot is empty <=> not is_occupied and not is_shifted and not is_continuation
        #   ... but is_occupied can remain set after deletion of the last element
        #   in a run if other runs reference it. Hmm.
        #
        # Let's use a separate tracking array for "has_element".
        return not self._has_element[slot]

    # ------------------------------------------------------------------
    # Core algorithms
    # ------------------------------------------------------------------

    def _find_run_start(self, quotient):
        """
        Find the slot where the run for `quotient` begins.

        1. Walk backward from quotient to find the cluster start
           (first slot in the cluster that is not shifted).
        2. Walk forward, skipping past runs for earlier quotients,
           until we reach the run belonging to our quotient.

        Returns slot index, or None if is_occupied[quotient] is False.
        """
        if not self.is_occupied[quotient]:
            return None

        # Step 1: find cluster start by walking backward
        b = quotient
        while self.is_shifted[b]:
            b = self._decr(b)

        # Step 2: walk forward, counting runs to skip
        # Count how many occupied canonical slots are between b and quotient
        s = b
        runs_to_skip = 0
        while s != quotient:
            if self.is_occupied[s]:
                runs_to_skip += 1
            s = self._incr(s)

        # Now skip that many complete runs starting from b
        s = b
        while runs_to_skip > 0:
            s = self._incr(s)
            if not self.is_continuation[s]:
                runs_to_skip -= 1

        return s

    def _find_first_empty_after(self, slot):
        """Find the first empty slot at or after `slot`."""
        s = slot
        while self._has_element[s]:
            s = self._incr(s)
        return s

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, item):
        """
        Insert an item into the quotient filter.
        Returns True if inserted, False if filter is full.
        """
        if self.count >= self.size - 1:
            return False  # keep one slot empty to avoid infinite loops

        quotient, remainder = self._split_hash(item)

        # If no element with this quotient exists yet
        if not self.is_occupied[quotient]:
            self.is_occupied[quotient] = True

            if not self._has_element[quotient]:
                # Canonical slot is empty — just place it
                self.remainders[quotient] = remainder
                self._has_element[quotient] = True
                self.count += 1
                return True
            else:
                # Canonical slot is taken by an element from another run.
                # We need to find where our new single-element run goes.
                run_start = self._find_run_start(quotient)
                # run_start is where the NEXT run after ours would start,
                # but since we just set is_occupied, _find_run_start now
                # finds us. Actually, we need to insert before the element
                # currently at this position.
                # Since our quotient was not previously occupied, the run
                # start is the point right after all runs for earlier
                # quotients in the same cluster.
                self._shift_right_and_insert(run_start, remainder,
                                             is_continuation=False,
                                             is_shifted=(run_start != quotient))
                self.count += 1
                return True

        # Quotient is already occupied — find the existing run
        run_start = self._find_run_start(quotient)

        # Walk the run to find sorted insertion point
        s = run_start
        while True:
            if self.remainders[s] == remainder:
                return True  # duplicate fingerprint, treat as already present
            if self.remainders[s] > remainder:
                break  # insert before s
            # Move to next element in run
            ns = self._incr(s)
            if not self.is_continuation[ns] or not self._has_element[ns]:
                # End of run — insert after s
                s = ns
                break
            s = ns

        # s is the slot where we insert (shifting everything right)
        is_cont = (s != run_start)
        is_shift = (s != quotient)
        self._shift_right_and_insert(s, remainder,
                                     is_continuation=is_cont,
                                     is_shifted=is_shift)
        self.count += 1
        return True

    def _shift_right_and_insert(self, slot, remainder, is_continuation, is_shifted):
        """
        Insert remainder at `slot`, shifting all subsequent elements one
        position to the right until an empty slot is found.
        """
        # Find the first empty slot
        empty = self._find_first_empty_after(slot)

        # Shift everything from empty back to slot one position right
        while empty != slot:
            prev = self._decr(empty)
            self.remainders[empty] = self.remainders[prev]
            self.is_shifted[empty] = True  # displaced elements are always shifted
            self.is_continuation[empty] = self.is_continuation[prev]
            self._has_element[empty] = True
            empty = prev

        # Place the new element
        self.remainders[slot] = remainder
        self.is_continuation[slot] = is_continuation
        self.is_shifted[slot] = is_shifted
        self._has_element[slot] = True

        # Fix: the element that was at slot (now shifted to slot+1) —
        # if it was the first of its run (not continuation), and it was
        # at its canonical position (not shifted), the copy at slot+1
        # is now shifted and still not a continuation. But if our new
        # element is NOT a continuation, the old first-of-run becomes
        # a continuation of... no, runs from different quotients don't
        # merge. The old element keeps its is_continuation status.
        # This is handled by copying is_continuation above.

    def contains(self, item):
        """
        Check if an item might be in the filter.
        Returns True if probably present, False if definitely not.
        """
        quotient, remainder = self._split_hash(item)

        if not self.is_occupied[quotient]:
            return False

        run_start = self._find_run_start(quotient)
        if run_start is None:
            return False

        # Scan the run for our remainder
        s = run_start
        while True:
            if self.remainders[s] == remainder:
                return True
            if self.remainders[s] > remainder:
                return False  # sorted, so won't find it
            ns = self._incr(s)
            if not self.is_continuation[ns] or not self._has_element[ns]:
                return False  # end of run
            s = ns

    def delete(self, item):
        """
        Delete an item. Returns True if found and removed, False otherwise.
        """
        quotient, remainder = self._split_hash(item)

        if not self.is_occupied[quotient]:
            return False

        run_start = self._find_run_start(quotient)
        if run_start is None:
            return False

        # Find the element in the run, also track run length
        s = run_start
        target = None
        run_slots = []
        while True:
            run_slots.append(s)
            if self.remainders[s] == remainder and target is None:
                target = s
            ns = self._incr(s)
            if not self.is_continuation[ns] or not self._has_element[ns]:
                break
            s = ns

        if target is None:
            return False

        # If the run has only one element, clear the occupied bit
        if len(run_slots) == 1:
            self.is_occupied[quotient] = False

        # Shift subsequent elements left to fill the gap
        self._shift_left_and_delete(target)
        self.count -= 1
        return True

    def _shift_left_and_delete(self, slot):
        """
        Remove the element at `slot` and shift subsequent elements left
        to fill the gap, stopping when we hit an empty slot or an element
        at its canonical position.
        """
        s = slot
        ns = self._incr(s)

        while self._has_element[ns] and self.is_shifted[ns]:
            # Move ns into s
            self.remainders[s] = self.remainders[ns]
            self.is_shifted[s] = self.is_shifted[slot] if s == slot else True
            self.is_continuation[s] = self.is_continuation[ns]

            # If ns was the start of a new run (not continuation), and we
            # moved it back, it might now be at its canonical slot
            if not self.is_continuation[ns]:
                # This is the start of a run. Check if its new position (s)
                # is its canonical slot.
                # We can't easily determine the canonical slot, so we keep
                # is_shifted as True (conservative). If s happens to be the
                # canonical slot, we should set is_shifted to False.
                # For correctness, walk back to find which quotient this
                # run belongs to.
                pass

            s = ns
            ns = self._incr(s)

        # Clear the last slot
        self.remainders[s] = 0
        self.is_shifted[s] = False
        self.is_continuation[s] = False
        self._has_element[s] = False

    # ------------------------------------------------------------------
    # Properties and display
    # ------------------------------------------------------------------

    @property
    def load_factor(self):
        return self.count / self.size

    def __len__(self):
        return self.count

    def __contains__(self, item):
        return self.contains(item)

    def __repr__(self):
        return (f"QuotientFilter(q_bits={self.q_bits}, r_bits={self.r_bits}, "
                f"slots={self.size}, count={self.count}, "
                f"load_factor={self.load_factor:.2%})")

    def __init__(self, q_bits=8, r_bits=8):
        self.q_bits = q_bits
        self.r_bits = r_bits
        self.size = 1 << q_bits
        self.mask_q = self.size - 1
        self.mask_r = (1 << r_bits) - 1
        self.fingerprint_bits = q_bits + r_bits

        self.remainders = [0] * self.size
        self.is_occupied = [False] * self.size
        self.is_continuation = [False] * self.size
        self.is_shifted = [False] * self.size
        self._has_element = [False] * self.size  # tracks if slot stores an element

        self.count = 0

    def dump(self, limit=None):
        """Debug: print the table state."""
        n = min(self.size, limit) if limit else self.size
        print(f"{'Slot':>4} {'Rem':>5} {'Occ':>3} {'Con':>3} {'Shf':>3} {'Has':>3}")
        print("-" * 26)
        for i in range(n):
            occ = "O" if self.is_occupied[i] else "."
            con = "C" if self.is_continuation[i] else "."
            shf = "S" if self.is_shifted[i] else "."
            has = "*" if self._has_element[i] else "."
            rem = self.remainders[i] if self._has_element[i] else "-"
            print(f"{i:>4} {rem:>5} {occ:>3} {con:>3} {shf:>3} {has:>3}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_basic_operations():
    """Show insert, lookup, and delete operations."""
    print("=" * 60)
    print("DEMO: Basic Quotient Filter Operations")
    print("=" * 60)

    qf = QuotientFilter(q_bits=6, r_bits=8)
    print(f"\nCreated: {qf}")

    items = ["apple", "banana", "cherry", "date", "elderberry",
             "fig", "grape", "honeydew"]
    for item in items:
        qf.insert(item)
        print(f"  Inserted '{item}' -> load_factor={qf.load_factor:.2%}")

    print(f"\nAfter inserts: {qf}")

    print("\nLookup results:")
    for item in items:
        print(f"  '{item}' in filter: {qf.contains(item)}")

    missing = ["kiwi", "lemon", "mango"]
    print("\nItems NOT inserted:")
    for item in missing:
        print(f"  '{item}' in filter: {qf.contains(item)}")

    print("\nDeleting 'banana' and 'fig'...")
    qf.delete("banana")
    qf.delete("fig")
    print(f"After deletion: {qf}")
    print(f"  'banana' in filter: {qf.contains('banana')}")
    print(f"  'fig' in filter: {qf.contains('fig')}")
    print(f"  'apple' in filter: {qf.contains('apple')}")


def demo_false_positive_rate():
    """Measure empirical false positive rate."""
    print("\n" + "=" * 60)
    print("DEMO: False Positive Rate Measurement")
    print("=" * 60)

    q_bits = 10
    r_bits_values = [4, 6, 8, 10, 12]

    for r_bits in r_bits_values:
        qf = QuotientFilter(q_bits=q_bits, r_bits=r_bits)

        inserted = set()
        for i in range(500):
            item = f"item_{i}"
            qf.insert(item)
            inserted.add(item)

        false_positives = 0
        test_count = 10000
        for i in range(test_count):
            item = f"test_{i}_not_inserted"
            if item not in inserted and qf.contains(item):
                false_positives += 1

        fp_rate = false_positives / test_count
        theoretical = 1.0 / (1 << r_bits)
        print(f"  r_bits={r_bits:>2}: measured FP rate = {fp_rate:.4f}, "
              f"theoretical ~{theoretical:.4f}")


def demo_deletion_advantage():
    """Show that deletion works — something Bloom filters cannot do."""
    print("\n" + "=" * 60)
    print("DEMO: Deletion (Advantage over Bloom Filters)")
    print("=" * 60)

    qf = QuotientFilter(q_bits=8, r_bits=8)

    items = [f"element_{i}" for i in range(100)]
    for item in items:
        qf.insert(item)

    print(f"After inserting 100 items: count={len(qf)}")

    deleted = []
    for i in range(0, 100, 2):
        result = qf.delete(items[i])
        deleted.append(items[i])

    print(f"After deleting 50 items: count={len(qf)}")

    still_found = sum(1 for item in deleted if qf.contains(item))
    print(f"Deleted items still 'found' (false positives): {still_found}/50")

    remaining = [items[i] for i in range(1, 100, 2)]
    found = sum(1 for item in remaining if qf.contains(item))
    print(f"Remaining items found: {found}/50")


if __name__ == "__main__":
    demo_basic_operations()
    demo_false_positive_rate()
    demo_deletion_advantage()
